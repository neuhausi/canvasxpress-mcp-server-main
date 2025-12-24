#!/usr/bin/env python3
"""
Prepare data files from the reference code for the MCP server.
This script extracts the few-shot examples and schema from the reference directory.
"""

import json
import shutil
from pathlib import Path

# Paths
REFERENCE_DIR = Path(__file__).parent.parent / "reference"
DATA_DIR = Path(__file__).parent

def prepare_few_shot_examples():
    """Extract and convert few-shot examples from reference format to MCP format.
    
    Creates 132 individual examples (66 configs × 2 descriptions each):
    - 66 with human-written descriptions
    - 66 with GPT-4 generated descriptions
    """
    print("📦 Preparing few-shot examples...")
    
    # Load the reference data
    source_file = REFERENCE_DIR / "all_few_shots.json"
    with open(source_file) as f:
        data = json.load(f)
    
    # Extract the Questions (which are the few-shot examples)
    # Create TWO separate examples for each: one with human description, one with GPT-4 description
    examples = []
    example_id = 0
    
    for i, item in enumerate(data["Questions"]):
        # Each item has: Type, Answer (config), Question, QuestionGPT4
        
        # Example 1: Human-written description
        example_human = {
            "id": example_id,
            "type": item["Type"],
            "description": item["Question"],  # Original human description
            "config": item["Answer"],
            "headers": ",".join(data["data"][0]),  # Column headers from data
            "source": "human",
            "original_id": i
        }
        examples.append(example_human)
        example_id += 1
        
        # Example 2: GPT-4 generated description (for same config)
        example_gpt4 = {
            "id": example_id,
            "type": item["Type"],
            "description": item["QuestionGPT4"],  # GPT-4 generated alternative
            "config": item["Answer"],
            "headers": ",".join(data["data"][0]),
            "source": "gpt4",
            "original_id": i
        }
        examples.append(example_gpt4)
        example_id += 1
    
    # Save in our format
    output_file = DATA_DIR / "few_shot_examples.json"
    with open(output_file, "w") as f:
        json.dump(examples, f, indent=2)
    
    print(f"✓ Created {len(examples)} few-shot examples in {output_file}")
    print(f"  - {len(examples)//2} human-written descriptions")
    print(f"  - {len(examples)//2} GPT-4 generated descriptions")
    return len(examples)

def copy_schema():
    """Copy schema file from reference."""
    print("📦 Copying schema...")
    
    source_file = REFERENCE_DIR / "schema.txt"
    dest_file = DATA_DIR / "schema.md"
    
    shutil.copy(source_file, dest_file)
    
    print(f"✓ Copied schema to {dest_file}")

def copy_prompt_template():
    """Copy prompt template from reference."""
    print("📦 Copying prompt template...")
    
    source_file = REFERENCE_DIR / "prompt.md"
    dest_file = DATA_DIR / "prompt_template.md"
    
    shutil.copy(source_file, dest_file)
    
    print(f"✓ Copied prompt template to {dest_file}")

def main():
    """Prepare all data files."""
    print("=" * 60)
    print("Preparing CanvasXpress MCP Server Data")
    print("=" * 60)
    
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)
    
    # Prepare each component
    num_examples = prepare_few_shot_examples()
    copy_schema()
    copy_prompt_template()
    
    print("=" * 60)
    print(f"✅ Data preparation complete!")
    print(f"   - {num_examples} few-shot examples")
    print(f"   - Schema documentation")
    print(f"   - Prompt template")
    print("=" * 60)

if __name__ == "__main__":
    main()
