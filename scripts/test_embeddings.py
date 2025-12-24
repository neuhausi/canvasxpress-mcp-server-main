#!/usr/bin/env python3
"""
Test embedding retrieval from vector DB using the configured embedding provider.

Uses EMBEDDING_PROVIDER from .env (local, onnx, openai, or gemini).

Usage:
    python scripts/test_embeddings.py "your query here"
    python scripts/test_embeddings.py "bar chart" --limit 5
    python scripts/test_embeddings.py  # uses default query
"""

import argparse
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
load_dotenv()

from canvasxpress_generator import EmbeddingProvider


def main():
    parser = argparse.ArgumentParser(description="Test embedding retrieval from vector DB")
    parser.add_argument("query", nargs="?", default="Generate a bar chart with title 'hi'",
                        help="Query to search for (default: bar chart query)")
    parser.add_argument("--limit", "-n", type=int, default=10,
                        help="Number of results to return (default: 10)")
    parser.add_argument("--db", default="./vector_db/canvasxpress_mcp.db",
                        help="Path to vector database (default: ./vector_db/canvasxpress_mcp.db)")
    args = parser.parse_args()

    # Get provider from environment
    provider = os.getenv("EMBEDDING_PROVIDER", "local")
    
    print("=" * 70)
    print("🔍 Embedding Retrieval Test")
    print("=" * 70)
    print(f"📦 Provider: {provider}")
    
    # Show provider-specific config
    if provider == "local":
        print(f"   Model: BGE-M3 (1024 dimensions)")
    elif provider == "onnx":
        model = os.getenv("ONNX_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        print(f"   Model: {model}")
    elif provider == "openai":
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        print(f"   Model: {model}")
    elif provider == "gemini":
        model = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
        print(f"   Model: {model}")
    
    print(f"📁 Database: {args.db}")
    print("=" * 70)

    # Initialize embedding provider (reuse the class from canvasxpress_generator)
    print("\n⏳ Loading embedding model...")
    embedder = EmbeddingProvider(provider=provider)
    print(f"   ✓ Loaded ({embedder.dimension} dimensions)")

    # Connect to vector DB
    from pymilvus import MilvusClient
    print(f"\n📂 Connecting to vector database...")
    client = MilvusClient(args.db)
    
    # List collections
    collections = client.list_collections()
    if not collections:
        print("❌ ERROR: No collections found! Run 'make init-local' first.")
        sys.exit(1)
    
    collection_name = collections[0]
    stats = client.get_collection_stats(collection_name)
    row_count = stats.get("row_count", "unknown")
    print(f"   ✓ Collection: {collection_name} ({row_count} vectors)")

    # Test query
    print(f"\n🔍 Query: \"{args.query}\"")
    print("-" * 70)

    # Generate embedding for query
    query_embedding = embedder.encode_query(args.query)

    # Search
    results = client.search(
        collection_name=collection_name,
        data=[query_embedding],
        limit=args.limit,
        output_fields=["description", "config"]
    )

    # Display results
    print(f"\n📊 TOP {args.limit} RESULTS:")
    print("=" * 70)
    
    for i, hit in enumerate(results[0], 1):
        desc = hit["entity"]["description"]
        config = hit["entity"]["config"]
        
        # Truncate for display
        if len(desc) > 120:
            desc = desc[:120] + "..."
        if len(config) > 100:
            config = config[:100] + "..."
        
        print(f"\n{i}. [Score: {hit['distance']:.4f}]")
        print(f"   Description: {desc}")
        print(f"   Config: {config}")

    print("\n" + "=" * 70)
    print("✅ Test complete")


if __name__ == "__main__":
    main()
