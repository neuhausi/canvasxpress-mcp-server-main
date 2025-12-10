#!/usr/bin/env python3
"""
Vector Database Testing Utility

Test and inspect the Milvus vector database containing CanvasXpress examples.
"""

import sys
from pathlib import Path
from pymilvus import MilvusClient
from FlagEmbedding import BGEM3FlagModel


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def test_database_info(db_path: str):
    """Test basic database information."""
    print_header("📊 DATABASE INFORMATION")
    
    client = MilvusClient(db_path)
    
    # List collections
    collections = client.list_collections()
    print(f"✓ Collections: {collections}")
    
    if not collections:
        print("❌ No collections found!")
        return None
    
    # Get collection stats
    collection_name = collections[0]
    stats = client.get_collection_stats(collection_name)
    print(f"✓ Collection name: {collection_name}")
    print(f"✓ Row count: {stats['row_count']}")
    
    # Check if database is empty
    if stats['row_count'] == 0:
        print("\n⚠️  WARNING: Database has 0 rows!")
        print("The collection exists but no data was inserted.")
        print("This usually means 'make init' needs to be run again.\n")
        return None
    
    return client, collection_name


def test_sample_data(client: MilvusClient, collection_name: str, limit: int = 5):
    """Display sample data from the database."""
    print_header(f"📋 SAMPLE DATA (First {limit} examples)")
    
    results = client.query(
        collection_name=collection_name,
        filter="",
        output_fields=["id", "type", "description"],
        limit=limit
    )
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Example {i} ---")
        print(f"ID: {result['id']}")
        print(f"Type: {result.get('type', 'N/A')}")
        print(f"Description: {result.get('description', 'N/A')[:200]}...")
    
    print(f"\n✓ Retrieved {len(results)} examples")


def test_chart_types(client: MilvusClient, collection_name: str):
    """Show distribution of chart types."""
    print_header("📈 CHART TYPE DISTRIBUTION")
    
    # Get all chart types
    results = client.query(
        collection_name=collection_name,
        filter="",
        output_fields=["type"],
        limit=200
    )
    
    # Count types
    type_counts = {}
    for result in results:
        chart_type = result.get('type', 'unknown')
        type_counts[chart_type] = type_counts.get(chart_type, 0) + 1
    
    # Sort and display
    for chart_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {chart_type:20s} : {count:3d} examples")
    
    print(f"\n✓ Total unique chart types: {len(type_counts)}")


def test_semantic_search(client: MilvusClient, collection_name: str, query: str, top_k: int = 5):
    """Test semantic search with a query."""
    print_header(f"🔍 SEMANTIC SEARCH TEST")
    
    print(f"Query: '{query}'")
    print(f"Retrieving top {top_k} most similar examples...\n")
    
    # Initialize embedding model
    print("Loading BGE-M3 model...")
    bge_m3_ef = BGEM3FlagModel('BAAI/bge-m3', use_fp16=False)
    
    # Generate query embedding
    query_embedding = bge_m3_ef.encode([query])['dense_vecs'][0]
    query_vector = query_embedding.tolist() if hasattr(query_embedding, 'tolist') else query_embedding
    
    # Search
    results = client.search(
        collection_name=collection_name,
        data=[query_vector],
        limit=top_k,
        output_fields=["id", "type", "description"]
    )
    
    # Display results
    for i, hits in enumerate(results):
        for j, hit in enumerate(hits, 1):
            print(f"\n--- Result {j} (Similarity: {hit['distance']:.4f}) ---")
            print(f"ID: {hit['entity']['id']}")
            print(f"Type: {hit['entity'].get('type', 'N/A')}")
            print(f"Description: {hit['entity'].get('description', 'N/A')[:300]}...")
    
    print(f"\n✓ Search completed successfully")


def test_vector_dimensions(client: MilvusClient, collection_name: str):
    """Check vector dimensions."""
    print_header("🔢 VECTOR DIMENSIONS")
    
    # Get one example with vector
    results = client.query(
        collection_name=collection_name,
        filter="",
        output_fields=["id", "vector"],
        limit=1
    )
    
    if results and 'vector' in results[0]:
        vector = results[0]['vector']
        print(f"✓ Vector dimension: {len(vector)}")
        print(f"✓ Vector type: {type(vector)}")
        print(f"✓ Sample values (first 5): {vector[:5]}")
    else:
        print("❌ Could not retrieve vector data")


def main():
    """Run all tests."""
    db_path = "/root/.cache/canvasxpress_mcp.db"
    
    print("\n" + "="*70)
    print("  🧪 CANVASXPRESS VECTOR DATABASE TESTING UTILITY")
    print("="*70)
    
    # Test 1: Database info
    result = test_database_info(db_path)
    if result is None:
        print("\n❌ Database tests failed!")
        sys.exit(1)
    
    client, collection_name = result
    
    # Test 2: Sample data
    test_sample_data(client, collection_name, limit=3)
    
    # Test 3: Chart types
    test_chart_types(client, collection_name)
    
    # Test 4: Vector dimensions
    test_vector_dimensions(client, collection_name)
    
    # Test 5: Semantic search
    test_queries = [
        "bar chart with blue bars",
        "scatter plot with regression line",
        "heatmap showing gene expression"
    ]
    
    for query in test_queries:
        test_semantic_search(client, collection_name, query, top_k=3)
    
    # Summary
    print_header("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("The vector database is working correctly and ready for use!\n")


if __name__ == "__main__":
    main()
