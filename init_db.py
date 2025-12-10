#!/usr/bin/env python3
"""
Vector Database Initialization Script

Forces initialization of the Milvus vector database with all examples.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, '/app/src')

from canvasxpress_generator import CanvasXpressGenerator

def main():
    """Initialize the database, dropping existing collection if needed."""
    print("🔧 Initializing CanvasXpress Vector Database...")
    print("=" * 70)
    
    try:
        # Initialize generator (this will create/populate database)
        generator = CanvasXpressGenerator()
        
        # Verify the database has data
        from pymilvus import MilvusClient
        client = MilvusClient("/root/.cache/canvasxpress_mcp.db")
        stats = client.get_collection_stats("few_shot_examples")
        
        print("\n" + "=" * 70)
        print(f"✅ Vector database initialized successfully!")
        print(f"✅ Collection: few_shot_examples")
        print(f"✅ Total examples: {stats['row_count']}")
        print("=" * 70)
        
        if stats['row_count'] == 0:
            print("\n⚠️  WARNING: No data was inserted!")
            print("This is unexpected. Check the initialization logic.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
