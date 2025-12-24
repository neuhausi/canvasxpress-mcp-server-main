#!/usr/bin/env python3
"""
Generate Alternative Wordings for Few-Shot Examples

This script reads few_shot_examples.json and enriches each example with
alternative English wordings using an LLM (OpenAI or Gemini).

The number of alternatives is configurable via ALT_WORDING_COUNT env var (default: 3).

Usage:
    python scripts/generate_alt_wordings.py           # Add alternatives to examples that don't have them
    python scripts/generate_alt_wordings.py --force   # Regenerate ALL alternatives (overwrite existing)
    
Environment Variables:
    LLM_PROVIDER        - 'openai' or 'gemini' (default: from .env)
    ALT_WORDING_COUNT   - Number of alternatives to generate (default: 3)
    ALT_WORDING_TEMP    - Temperature for generation (default: 0.1)
    
The script supports resuming - it will skip examples that already have alt_descriptions
(unless --force is used).
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import LLMProvider from canvasxpress_generator
from canvasxpress_generator import LLMProvider


def build_alt_wording_prompt(description: str, num_alternatives: int = 3) -> str:
    """Build the prompt for generating alternative wordings."""
    return f"""Generate {num_alternatives} different alternative wordings for the following paragraph that describes a data visualization. Each alternative should express the exact same meaning but use different phrasing.

CRITICAL CONSTRAINTS:
1. Keep these terms EXACTLY unchanged: "sort", "group by", "filter"
2. Do NOT substitute "sort" with "group by" or vice versa (they have different meanings)
3. Do NOT substitute "sort" with "organize" 
4. For filter criteria, use only "like" and "different" (use "different" instead of "not like")
5. Preserve all numbers, column names, and specific values exactly

VARIATION GUIDELINES:
- Vary sentence structure (active/passive, order of clauses)
- Use synonyms for non-critical words
- Each alternative should be noticeably different from the others

OUTPUT FORMAT:
Return ONLY a JSON array of {num_alternatives} strings, no other text:
["alternative 1", "alternative 2", "alternative 3"]

PARAGRAPH:
{description}"""


def clean_json_response(response: str) -> str:
    """Remove markdown code blocks and clean up JSON response."""
    # Remove ```json or ``` blocks
    cleaned = re.sub(r'^```json\s*', '', response.strip())
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    return cleaned.strip()


def generate_alternatives(
    llm: LLMProvider,
    description: str,
    num_alternatives: int = 3,
    temperature: float = 0.1,
    max_retries: int = 3
) -> list:
    """Generate alternative wordings for a description."""
    prompt = build_alt_wording_prompt(description, num_alternatives)
    
    for attempt in range(max_retries):
        try:
            response = llm.generate(prompt, temperature=temperature)
            cleaned = clean_json_response(response)
            alternatives = json.loads(cleaned)
            
            # Validate response
            if not isinstance(alternatives, list):
                raise ValueError(f"Expected list, got {type(alternatives)}")
            if len(alternatives) != num_alternatives:
                print(f"   ⚠️  Expected {num_alternatives} alternatives, got {len(alternatives)}")
            
            return alternatives
            
        except json.JSONDecodeError as e:
            print(f"   ⚠️  Attempt {attempt + 1}: JSON parse error: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
        except Exception as e:
            print(f"   ⚠️  Attempt {attempt + 1}: Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
    
    return None


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Generate alternative wordings for few-shot examples"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Regenerate ALL alternatives, overwriting existing ones"
    )
    args = parser.parse_args()
    
    # Configuration
    num_alternatives = int(os.environ.get("ALT_WORDING_COUNT", "3"))
    temperature = float(os.environ.get("ALT_WORDING_TEMP", "0.1"))
    llm_provider_name = os.environ.get("LLM_PROVIDER", "openai").lower()
    force_regenerate = args.force
    
    # Paths
    project_root = Path(__file__).parent.parent
    examples_file = project_root / "data" / "few_shot_examples.json"
    
    print("=" * 70)
    print("🔧 Generate Alternative Wordings for Few-Shot Examples")
    print("=" * 70)
    print(f"📁 Examples file: {examples_file}")
    print(f"🤖 LLM Provider: {llm_provider_name}")
    print(f"📝 Alternatives per example: {num_alternatives}")
    print(f"🌡️  Temperature: {temperature}")
    print(f"🔄 Force regenerate: {force_regenerate}")
    print("=" * 70)
    
    # Load examples
    print("\n📖 Loading few-shot examples...")
    with open(examples_file) as f:
        examples = json.load(f)
    
    total = len(examples)
    already_done = sum(1 for ex in examples if "alt_descriptions" in ex)
    
    if force_regenerate:
        to_process = total
        print(f"   Total examples: {total}")
        print(f"   Mode: FORCE - will regenerate all {total} examples")
    else:
        to_process = total - already_done
        print(f"   Total examples: {total}")
        print(f"   Already processed: {already_done}")
        print(f"   To process: {to_process}")
    
    if to_process == 0:
        print("\n✅ All examples already have alternative wordings!")
        print("   Use --force to regenerate them.")
        return
    
    # Initialize LLM
    print(f"\n🔧 Initializing {llm_provider_name} LLM...")
    llm = LLMProvider(provider=llm_provider_name)
    
    # Process examples
    print(f"\n🚀 Generating alternatives...\n")
    processed = 0
    failed = 0
    
    for i, example in enumerate(examples):
        # Skip if already has alternatives (unless force mode)
        if "alt_descriptions" in example and not force_regenerate:
            continue
        
        description = example["description"]
        example_id = example.get("id", i + 1)
        
        print(f"[{i + 1}/{total}] Example {example_id}: {description[:60]}...")
        
        alternatives = generate_alternatives(
            llm=llm,
            description=description,
            num_alternatives=num_alternatives,
            temperature=temperature
        )
        
        if alternatives:
            example["alt_descriptions"] = alternatives
            processed += 1
            print(f"   ✓ Generated {len(alternatives)} alternatives")
        else:
            failed += 1
            print(f"   ✗ Failed to generate alternatives")
        
        # Save progress after each example (resume support)
        with open(examples_file, 'w') as f:
            json.dump(examples, f, indent=2)
        
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ Generation complete!")
    print("=" * 70)
    print(f"   Processed: {processed}")
    print(f"   Failed: {failed}")
    print(f"   Total with alternatives: {already_done + processed}")
    print(f"\n📁 Updated: {examples_file}")
    print("\nNext steps:")
    print("  1. Delete existing vector DB: rm -rf vector_db/")
    print("  2. Re-initialize: make init-local")
    print("  3. Run server: make run-local")


if __name__ == "__main__":
    main()
