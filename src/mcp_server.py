"""
CanvasXpress MCP Server (FastMCP 2.0)

Model Context Protocol server that provides CanvasXpress configuration generation
as a tool for AI assistants like Claude Desktop.

Usage:
    # Docker workflow
    make run-http       # HTTP mode (daemon)
    make run            # STDIO mode
    
    # Local virtual environment workflow
    make venv           # Create venv & install deps
    make init-local     # Initialize vector DB
    make run-local      # Run HTTP server locally

Configuration via environment variables (set in .env file):
    AZURE_OPENAI_KEY: BMS Azure OpenAI API key
    AZURE_OPENAI_API_VERSION: API version (default: 2024-02-01)
    LLM_MODEL: Azure model name (default: gpt-4o-mini-global)
    LLM_ENVIRONMENT: BMS environment - nonprod or prod (default: nonprod)
    
    MCP_TRANSPORT: Transport mode - stdio or http (default: stdio)
    MCP_HOST: HTTP host to bind to (default: 0.0.0.0)
    MCP_PORT: HTTP port to listen on (default: 8000)
"""

import json
import os

from dotenv import load_dotenv
from fastmcp import FastMCP

# Load .env file if running locally (not in Docker)
if not os.path.exists('/app/data'):
    load_dotenv()

# Handle imports for both Docker and local environments
try:
    from canvasxpress_generator import CanvasXpressGenerator
except ImportError:
    from src.canvasxpress_generator import CanvasXpressGenerator

# Auto-detect paths based on environment (Docker vs local)
def get_paths():
    """Detect if running in Docker or locally and return appropriate paths."""
    if os.path.exists('/app/data'):
        # Docker environment
        return {
            'data_dir': '/app/data',
            'vector_db_path': '/root/.cache/canvasxpress_mcp.db',
            'environment': 'docker'
        }
    else:
        # Local environment - paths relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return {
            'data_dir': os.path.join(base_dir, 'data'),
            'vector_db_path': os.path.join(base_dir, 'vector_db', 'canvasxpress_mcp.db'),
            'environment': 'local'
        }

PATHS = get_paths()

# Initialize FastMCP server
mcp = FastMCP("CanvasXpress Chart Generator 🎨")

# Get configuration from environment
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini-global")
LLM_ENVIRONMENT = os.environ.get("LLM_ENVIRONMENT", "nonprod")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")
EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "local")

# Initialize generator on startup
print("=" * 60)
print("🚀 Starting CanvasXpress MCP Server (FastMCP 2.0)")
print("=" * 60)
print(f"📦 Environment: {PATHS['environment']}")
print(f"📦 Data dir: {PATHS['data_dir']}")
print(f"📦 Vector DB: {PATHS['vector_db_path']}")
print(f"📦 LLM Provider: {LLM_PROVIDER}")
print(f"📦 Embedding Provider: {EMBEDDING_PROVIDER}")
print("=" * 60)

generator = CanvasXpressGenerator(
    data_dir=PATHS['data_dir'],
    vector_db_path=PATHS['vector_db_path'],
    llm_model=LLM_MODEL,
    llm_environment=LLM_ENVIRONMENT
)

print("=" * 60)
print("✅ Generator initialized! Server ready.")
print("=" * 60)


@mcp.tool()
def generate_canvasxpress_config(
    description: str,
    headers: str = None,
    temperature: float = 0.0
) -> str:
    """Generate CanvasXpress visualization configuration from natural language description.
    
    Uses RAG with 132 few-shot examples and BGE-M3 semantic search.
    Returns JSON with status, description, headers, and configuration.
    
    Based on peer-reviewed methodology (Smith & Neuhaus, JOSS 2025):
    - 93% exact match accuracy
    - 98% similarity score
    - 25 most relevant examples per query
    
    Example charts supported: bar, boxplot, scatter, line, heatmap, area,
    dotplot, pie, venn, network, sankey, genome, and 30+ more.
    
    Args:
        description: Natural language description of the desired visualization.
            Be specific about chart type, data columns, styling, and interactivity.
            Example: 'Create a bar chart showing sales by region with blue bars
            and a legend on the right'
        headers: Optional column names/headers from your dataset.
            Example: 'Region, Sales, Profit, Year'
        temperature: LLM temperature (0.0-1.0). Use 0.0 for deterministic output.
            Default: 0.0
    
    Returns:
        JSON string with structure:
        {
            "success": true/false,
            "description": "original description",
            "headers": "original headers or null",
            "config": {...} or null,
            "error": null or "error message"
        }
    """
    try:
        # Generate configuration
        config = generator.generate(
            description=description,
            headers=headers,
            temperature=temperature
        )
        
        # Return structured JSON response
        result = {
            "success": True,
            "description": description,
            "headers": headers,
            "config": config,
            "error": None
        }
        return json.dumps(result)
        
    except json.JSONDecodeError as e:
        result = {
            "success": False,
            "description": description,
            "headers": headers,
            "config": None,
            "error": f"JSON parsing error: {str(e)}. The LLM returned invalid JSON. Try rephrasing your description."
        }
        return json.dumps(result)
        
    except Exception as e:
        result = {
            "success": False,
            "description": description,
            "headers": headers,
            "config": None,
            "error": f"Generation error: {str(e)}"
        }
        return json.dumps(result)


if __name__ == "__main__":
    import sys
    
    # Check for transport argument
    if "--http" in sys.argv or os.environ.get("MCP_TRANSPORT") == "http":
        # HTTP mode: accessible over the network
        host = os.environ.get("MCP_HOST", "0.0.0.0")
        port = int(os.environ.get("MCP_PORT", "8000"))
        
        print("\n🌐 Starting HTTP MCP Server")
        print(f"📡 Accessible at: http://{host}:{port}/mcp")
        print("=" * 60)
        
        mcp.run(transport="http", host=host, port=port)
    else:
        # STDIO mode (default): for Claude Desktop and local clients
        print("\n📋 Starting STDIO MCP Server")
        print("💻 For Claude Desktop / local MCP clients")
        print("=" * 60)
        
        mcp.run()
