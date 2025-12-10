#!/usr/bin/env python3
"""
Initialize the vector database for local development.

This script creates the Milvus vector database and embeds all few-shot examples.
Run this once before starting the MCP server locally.

Usage:
    python scripts/init_vector_db.py
    # or
    make init-local
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get paths relative to project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(project_root, 'data')
vector_db_dir = os.path.join(project_root, 'vector_db')
vector_db_path = os.path.join(vector_db_dir, 'canvasxpress_mcp.db')

print("=" * 60)
print("🔧 Initializing Vector Database (Local)")
print("=" * 60)
print(f"📁 Data directory: {data_dir}")
print(f"📁 Vector DB path: {vector_db_path}")
print(f"📦 Embedding provider: {os.environ.get('EMBEDDING_PROVIDER', 'local')}")
print("=" * 60)

# Create vector_db directory if it doesn't exist
os.makedirs(vector_db_dir, exist_ok=True)

# Import and initialize generator (this creates/loads the vector DB)
from canvasxpress_generator import CanvasXpressGenerator

embedding_provider = os.environ.get('EMBEDDING_PROVIDER', 'local')
if embedding_provider == 'local':
    print("\n⏳ Loading BGE-M3 model and embedding examples...")
    print("   (This may take 3-5 minutes on first run)\n")
elif embedding_provider == 'gemini':
    print("\n⏳ Using Gemini API for embeddings...")
    print("   (Requires GOOGLE_API_KEY in .env)\n")
elif embedding_provider == 'openai':
    print("\n⏳ Using Azure OpenAI API for embeddings...")
    print("   (Requires AZURE_OPENAI_KEY in .env)\n")
else:
    print(f"\n⚠️  Unknown embedding provider: {embedding_provider}")
    print("   Valid options: local, gemini, openai\n")

generator = CanvasXpressGenerator(
    data_dir=data_dir,
    vector_db_path=vector_db_path
)

print("\n" + "=" * 60)
print("✅ Vector database initialized successfully!")
print("=" * 60)
print(f"\n📊 Examples loaded: {len(generator.examples)}")
print(f"📁 Database location: {vector_db_path}")
print("\nNext steps:")
print("  1. Run the server: make run-local")
print("  2. Test with CLI:  python3 mcp_cli.py -q 'bar chart'")
