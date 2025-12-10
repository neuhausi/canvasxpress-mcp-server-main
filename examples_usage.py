#!/usr/bin/env python3
"""
Example: Using CanvasXpress Generator as a Python Tool

This shows how to import and use the generator in your own Python scripts.
"""

import os
import json
import sys

# Add src to path if running from project root
sys.path.insert(0, 'src')

from canvasxpress_generator import CanvasXpressGenerator


def example_1_basic_usage():
    """Example 1: Basic usage - generate a simple chart"""
    print("=" * 60)
    print("Example 1: Basic Bar Chart")
    print("=" * 60)
    
    # Initialize the generator (only do this ONCE, reuse the instance)
    generator = CanvasXpressGenerator(
        data_dir='data',
        vector_db_path='/root/.cache/canvasxpress_mcp.db',
        llm_model=os.environ.get('LLM_MODEL', 'gpt-4o-global'),
        llm_environment=os.environ.get('LLM_ENVIRONMENT', 'nonprod')
    )
    
    # Generate a configuration
    config = generator.generate(
        description="Create a bar chart with blue bars and legend on the right",
        headers="Region, Sales, Profit"
    )
    
    print("\n📊 Generated Configuration:")
    print(json.dumps(config, indent=2))
    return config


def example_2_multiple_charts():
    """Example 2: Generate multiple charts (reuse generator instance)"""
    print("\n" + "=" * 60)
    print("Example 2: Multiple Charts (Efficient)")
    print("=" * 60)
    
    # Initialize ONCE
    generator = CanvasXpressGenerator(
        data_dir='data',
        vector_db_path='/root/.cache/canvasxpress_mcp.db',
        llm_model='gpt-4o-global',
        llm_environment='nonprod'
    )
    
    # Generate multiple configs
    charts = [
        {
            "name": "Scatter Plot",
            "description": "Scatter plot with red points, x-axis is time, y-axis is expression",
            "headers": "Time, Expression, Gene"
        },
        {
            "name": "Heatmap",
            "description": "Heatmap with clustering, show dendrograms on both sides",
            "headers": "Gene1, Gene2, Gene3, Sample"
        },
        {
            "name": "Line Chart",
            "description": "Line chart with multiple series, show all in different colors",
            "headers": "Date, Series1, Series2, Series3"
        }
    ]
    
    results = []
    for chart in charts:
        print(f"\n🎨 Generating: {chart['name']}")
        config = generator.generate(
            description=chart['description'],
            headers=chart['headers']
        )
        results.append({
            "name": chart['name'],
            "config": config
        })
        print(f"   ✓ Generated {chart['name']}")
    
    return results


def example_3_with_error_handling():
    """Example 3: With proper error handling"""
    print("\n" + "=" * 60)
    print("Example 3: With Error Handling")
    print("=" * 60)
    
    try:
        generator = CanvasXpressGenerator(
            data_dir='data',
            vector_db_path='/root/.cache/canvasxpress_mcp.db',
            llm_model='gpt-4o-global',
            llm_environment='nonprod'
        )
        
        config = generator.generate(
            description="Pie chart showing market share by company",
            headers="Company, MarketShare",
            temperature=0.0  # Deterministic output
        )
        
        print("\n✅ Success!")
        print(json.dumps(config, indent=2))
        return config
        
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON Error: LLM returned invalid JSON")
        print(f"   Error: {e}")
        return None
        
    except RuntimeError as e:
        print(f"\n❌ Runtime Error: {e}")
        print(f"   Check your API key and network connection")
        return None
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return None


def example_4_inspect_similar_examples():
    """Example 4: See what examples the RAG system finds"""
    print("\n" + "=" * 60)
    print("Example 4: Inspect RAG Retrieval")
    print("=" * 60)
    
    generator = CanvasXpressGenerator(
        data_dir='data',
        vector_db_path='/root/.cache/canvasxpress_mcp.db',
        llm_model='gpt-4o-global',
        llm_environment='nonprod'
    )
    
    # Get similar examples without generating
    description = "Boxplot showing gene expression across samples"
    similar = generator.get_similar_examples(description, num_examples=5)
    
    print(f"\n🔍 Top 5 similar examples for: '{description}'\n")
    for i, ex in enumerate(similar, 1):
        print(f"{i}. Type: {ex['type']}")
        print(f"   Description: {ex['description'][:80]}...")
        print(f"   Similarity Score: {ex['score']:.4f}")
        print()
    
    return similar


def example_5_save_to_file():
    """Example 5: Generate and save config to file"""
    print("\n" + "=" * 60)
    print("Example 5: Generate and Save to File")
    print("=" * 60)
    
    generator = CanvasXpressGenerator(
        data_dir='data',
        vector_db_path='/root/.cache/canvasxpress_mcp.db',
        llm_model='gpt-4o-global',
        llm_environment='nonprod'
    )
    
    config = generator.generate(
        description="Network graph with curved edges and labeled nodes",
        headers="Source, Target, Weight"
    )
    
    # Save to file
    output_file = "my_canvasxpress_config.json"
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to: {output_file}")
    print(f"\n📝 Use in CanvasXpress:")
    print(f"   new CanvasXpress(data, {json.dumps(config)})")
    
    return config


def main():
    """Run all examples"""
    
    # Check environment
    if not os.environ.get('AZURE_OPENAI_KEY'):
        print("❌ Error: AZURE_OPENAI_KEY not set")
        print("\nSet it with:")
        print("  export AZURE_OPENAI_KEY=your_key_here")
        print("  export LLM_MODEL=gpt-4o-global")
        print("  export LLM_ENVIRONMENT=nonprod")
        return 1
    
    print("🚀 CanvasXpress Generator - Python Tool Examples")
    print("=" * 60)
    
    # Run examples
    try:
        # Example 1: Basic usage
        example_1_basic_usage()
        
        # Example 2: Multiple charts (comment out if you want to save API calls)
        # example_2_multiple_charts()
        
        # Example 3: Error handling
        # example_3_with_error_handling()
        
        # Example 4: Inspect RAG (no API call)
        example_4_inspect_similar_examples()
        
        # Example 5: Save to file
        # example_5_save_to_file()
        
        print("\n" + "=" * 60)
        print("✅ Examples complete!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
