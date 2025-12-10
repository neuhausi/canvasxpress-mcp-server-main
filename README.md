# CanvasXpress MCP Server

🎨 **Model Context Protocol (MCP) server for generating CanvasXpress visualizations from natural language.**

This MCP server provides AI assistants like Claude Desktop with the ability to generate CanvasXpress JSON configurations from natural language descriptions. It uses Retrieval Augmented Generation (RAG) with 132 few-shot examples (66 human + 66 GPT-4 descriptions) and semantic search.

**📄 Based on:** [Smith & Neuhaus (2024) - CanvasXpress NLP Research](https://osf.io/preprints/osf/kf2xp_v1)  
**🔌 Supports:** Azure OpenAI (BMS Proxy) **or** Google Gemini  
**🚀 Built with [FastMCP 2.0](https://gofastmcp.com)** - The modern standard for Python MCP servers

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- ✅ Docker installed and running (or Python 3.10+ for local venv)
- ✅ API key: BMS Azure OpenAI **or** Google Gemini
- ✅ 8GB RAM for local embeddings, or 2GB for cloud embeddings
- ✅ No GPU required

### Step 1: Clone Repository
```bash
git clone https://github.com/bms-ips/canvasxpress-mcp-server.git
cd canvasxpress-mcp-server
```

### Step 2: Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or vim, code, etc.
```

**For Azure OpenAI (BMS) with local embeddings:**
```bash
LLM_PROVIDER=openai
AZURE_OPENAI_KEY=your_key_from_genai.web.bms.com
LLM_MODEL=gpt-4o-global
LLM_ENVIRONMENT=nonprod
EMBEDDING_PROVIDER=local  # BGE-M3 (highest accuracy)
```

**For Google Gemini (fully cloud-based) ⭐ Lightweight:**
```bash
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key_from_aistudio.google.com
GEMINI_MODEL=gemini-2.0-flash-exp
EMBEDDING_PROVIDER=gemini  # Cloud embeddings (no PyTorch needed)
```

### Step 3: Choose Your Setup

#### Option A: Docker (Full) - Default
```bash
make build      # Build Docker image (~8GB with PyTorch)
make init       # Initialize vector DB (downloads BGE-M3 ~2GB)
make run-http   # Start server
```

#### Option B: Local Venv (Lightweight) ⭐ For smaller servers
```bash
make venv-light  # Create lightweight venv (~500MB, no PyTorch)
make init-local  # Initialize vector DB (uses cloud embeddings)
make run-local   # Start server
```
> **Note:** Option B requires `EMBEDDING_PROVIDER=gemini` or `EMBEDDING_PROVIDER=openai` in `.env`

### Step 4: Test the Server

```bash
# Using the CLI client (works with either setup)
python3 mcp_cli.py -q "Create a bar chart with blue bars"

# Or inside Docker:
docker exec -it $(docker ps -q) python3 /app/mcp_cli.py -q "Create a scatter plot"

# Full JSON response
python3 mcp_cli.py -q "Bar chart" --json
```

### That's it! 🎉

Your server is running at `http://localhost:8000/mcp`

**Quick Reference:**
| Command | Purpose |
|---------|---------|
| `make logs` | View server output (Docker daemon mode) |
| `make stop` | Stop Docker server |
| `make test-db` | Test vector database |

---

## 📊 Server Modes

### HTTP Mode (Network Access) - Recommended
```bash
make run-http   # Docker: daemon mode
make run-httpi  # Docker: interactive mode  
make run-local  # Local venv: foreground
```
- **Access at**: `http://localhost:8000/mcp`
- **Use for**: Remote access, web-based AI assistants, multiple clients

### STDIO Mode (Local Only)
```bash
make run        # Docker
make run-locali # Local venv
```
- **Use for**: Claude Desktop integration on same machine
- **Single client only**

---

## 🧪 Testing Options

**CLI Client** (Quick & Easy) ⭐
```bash
python3 mcp_cli.py -q "Heatmap with clustering" --headers "Gene,Sample1,Sample2"
python3 mcp_cli.py -q "Bar chart" --json          # Full JSON response
python3 mcp_cli.py -q "Line chart" --config-only  # Config only
```

**HTTP MCP Client**
```bash
docker exec -it $(docker ps -q) python3 /app/mcp_http_client.py
```

**Vector Database Test**
```bash
make test-db  # Verifies 132 examples loaded
```

**Python API**
```bash
python3 examples_usage.py
# Tests the generator as a Python library (no MCP)
```

**Next Steps:**
- 🌐 **HTTP Client Guide**: See `HTTP_CLIENT_GUIDE.md` for HTTP/network usage
- 📖 **Python API**: See `PYTHON_USAGE.md` for API reference
- 🔌 **Claude Desktop**: Configure MCP integration (see below)
- 📘 **Technical Details**: See `TECHNICAL_OVERVIEW.md` for architecture

---

## 🌟 Features

- **🎯 High Accuracy**: 93% exact match, 98% similarity (peer-reviewed methodology)
- **🔍 Semantic Search**: BGE-M3 embeddings with vector database (or cloud embeddings)
- **🤖 Multi-Provider LLM**: Azure OpenAI (BMS) **or** Google Gemini
- **📊 Multi-Provider Embeddings**: Local BGE-M3, Azure OpenAI, or Google Gemini
- **🐳 Docker or Local**: Run in Docker containers or Python virtual environment
- **🔌 FastMCP 2.0**: Modern, Pythonic MCP server framework with **HTTP & STDIO support**
- **🌐 Network Access**: HTTP mode for remote deployment and multiple concurrent clients
- **📊 132 Few-Shot Examples**: 66 chart types × 2 description styles (human + GPT-4)

---

## ⚙️ Provider Configuration

The server supports multiple LLM and embedding providers. Configure in `.env`:

### LLM Providers

| Provider | `LLM_PROVIDER` | Required Variables | Models |
|----------|----------------|-------------------|--------|
| Azure OpenAI (BMS) | `openai` | `AZURE_OPENAI_KEY`, `LLM_MODEL`, `LLM_ENVIRONMENT` | gpt-4o-global, gpt-4o-mini-global |
| Google Gemini | `gemini` | `GOOGLE_API_KEY`, `GEMINI_MODEL` | gemini-2.0-flash-exp, gemini-1.5-pro |

### Embedding Providers

| Provider | `EMBEDDING_PROVIDER` | Dimension | Notes |
|----------|---------------------|-----------|-------|
| BGE-M3 (local) | `local` | 1024 | **Recommended** - proven 93% accuracy, requires ~2GB download |
| Azure OpenAI | `openai` | 1536 | Uses `text-embedding-3-small` |
| Google Gemini | `gemini` | 768 | Uses `text-embedding-004` |

### Example Configurations

**Azure OpenAI + Local BGE-M3** (default, recommended for BMS):
```bash
LLM_PROVIDER=openai
AZURE_OPENAI_KEY=your_key
LLM_MODEL=gpt-4o-global
LLM_ENVIRONMENT=nonprod
EMBEDDING_PROVIDER=local
```

**Google Gemini + Local BGE-M3** (best accuracy with Gemini):
```bash
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key
GEMINI_MODEL=gemini-2.0-flash-exp
EMBEDDING_PROVIDER=local
```

**Full Gemini** (no local model needed, faster startup):
```bash
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key
GEMINI_MODEL=gemini-2.0-flash-exp
EMBEDDING_PROVIDER=gemini
```

> **Note:** If you change `EMBEDDING_PROVIDER`, you must reinitialize the vector database (`make init` or `make init-local`) since different providers have different embedding dimensions.

---

## 📋 Prerequisites

- Docker **OR** Python 3.10+
- API key: BMS Azure OpenAI **or** Google Gemini
- Linux/macOS (tested on Amazon Linux 2023)
- 8GB RAM for local embeddings, or 2GB for cloud embeddings
- No GPU required (embeddings run on CPU)

---

## 🐍 Local Development (Alternative to Docker)

If you prefer running without Docker, you can use a Python virtual environment.

### Prerequisites

**⚠️ Requires Python 3.10+** (FastMCP requirement)

```bash
# Check your Python version
python3 --version

# If you have multiple Python versions, check for 3.10+
python3.10 --version  # or python3.11, python3.12
```

**If Python 3.10+ is not installed**, install it:

```bash
# Amazon Linux 2023 / RHEL 9 / Fedora
sudo dnf install python3.11 python3.11-pip python3.11-devel

# Amazon Linux 2 / RHEL 8 / CentOS 8
sudo amazon-linux-extras install python3.11
# Or use pyenv (see below)

# Ubuntu 22.04+
sudo apt install python3.11 python3.11-venv python3.11-dev

# Ubuntu 20.04 (add deadsnakes PPA first)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# macOS (with Homebrew)
brew install python@3.11

# Using pyenv (any Linux/macOS)
curl https://pyenv.run | bash
pyenv install 3.11.9
pyenv local 3.11.9
```

### Step 1: Configure Python Path (if needed)

The Makefile uses `python3.12` by default. If your Python 3.10+ has a different name:

```bash
# Check what Python executables you have
ls -la /usr/bin/python3*

# Edit the Makefile to use your Python
nano Makefile

# Change this line near the top:
PYTHON_BIN = python3.12
# To whatever you have, e.g.:
PYTHON_BIN = python3.11
# Or:
PYTHON_BIN = python3
```

### Step 2: Create Virtual Environment

**Option A: Full Installation (~8GB)** - Local BGE-M3 embeddings
```bash
make venv
```
This creates a `./venv/` directory and installs all dependencies (~5-10 minutes for PyTorch/BGE-M3).
Use this if you want `EMBEDDING_PROVIDER=local` (default, highest accuracy).

**Option B: Lightweight Installation (~500MB)** - Cloud embeddings only ⭐
```bash
make venv-light
```
This installs only cloud-compatible dependencies (no PyTorch, no BGE-M3).
**Perfect for lightweight servers** that will use Gemini or OpenAI for embeddings.

> **⚠️ If using venv-light:** You MUST set `EMBEDDING_PROVIDER=gemini` (or `openai`) in your `.env` file before running `make init-local`. The local BGE-M3 model is not installed.

### Step 3: Configure Environment
```bash
cp .env.example .env
nano .env  # Add your AZURE_OPENAI_KEY
```

**For lightweight venv, use this configuration:**
```bash
# Example .env for venv-light (Gemini for both LLM and embeddings)
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
EMBEDDING_PROVIDER=gemini
GEMINI_EMBEDDING_MODEL=text-embedding-004
```

### Step 4: Initialize Vector Database
```bash
make init-local
```
Creates `./vector_db/canvasxpress_mcp.db` with 132 embedded examples.

### Step 5: Start Server
```bash
make run-local   # HTTP mode (http://localhost:8000/mcp)
make run-locali  # STDIO mode (for Claude Desktop)
```

### Step 6: Test
```bash
# Activate venv for CLI
source venv/bin/activate
python mcp_cli.py -q "Create a bar chart"
```

### Cleanup
```bash
make clean-local  # Remove venv and vector_db
```

### Troubleshooting Local Setup

**"python3.12: command not found"**
- Edit `PYTHON_BIN` in the Makefile to match your Python 3.10+ executable name
- Common alternatives: `python3.11`, `python3.10`, `python3`

**"No module named 'venv'" or venv creation fails**
- Install the venv module: `sudo apt install python3.11-venv` (Ubuntu) or `sudo dnf install python3.11` (RHEL/Amazon Linux)

**Permission denied on vector_db**
- If you previously ran Docker, the `vector_db/` directory may be owned by root
- Fix with: `sudo rm -rf vector_db && mkdir vector_db`

**Import errors when running**
- Make sure you activated the venv: `source venv/bin/activate`
- Verify dependencies installed: `pip list | grep fastmcp`

**"No module named 'FlagEmbedding'" (with venv-light)**
- You used `make venv-light` but have `EMBEDDING_PROVIDER=local` in `.env`
- Fix: Set `EMBEDDING_PROVIDER=gemini` (or `openai`) in `.env`
- The lightweight venv doesn't include the BGE-M3 model

**BGE-M3 model download fails**
- Ensure you have ~2GB free disk space
- Check network connectivity (may need VPN for some networks)
- The model downloads to `~/.cache/huggingface/`

---

## 🔧 Detailed Setup (Docker)

If you need more control or want to customize the Docker setup:

### Build Docker Image
```bash
make build
# Or manually:
docker build -t canvasxpress-mcp-server:latest .
```

### Initialize Vector Database
```bash
make init
# This creates ./vector_db/ directory with embedded examples
```

### Start MCP Server
```bash
make run-http  # HTTP mode (daemon, background)
# Check status with: make logs
```

### Configure Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "canvasxpress": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "canvasxpress-mcp-server",
        "python",
        "/app/src/mcp_server.py"
      ]
    }
  }
}
```

Restart Claude Desktop.

### Test in Claude

Open Claude Desktop and try:

> "Use the CanvasXpress tool to create a bar chart showing sales by region with blue bars and a legend on the right"

## 📖 Usage

### Transport Modes

The MCP server supports **two transport modes**:

#### 1. HTTP Mode (Default) - Network Access 🌐
```bash
make run-http   # Daemon mode (background)
make run-httpi  # Interactive mode (foreground)
```
- **URL**: `http://localhost:8000/mcp`
- **Access**: From anywhere on network/internet
- **Clients**: Multiple simultaneous connections
- **Use cases**: 
  - Remote AI assistants (ChatGPT, Claude web)
  - Cloud deployment (AWS, GCP, Azure)
  - Team collaboration
  - Production services

#### 2. STDIO Mode - Local Only 💻
```bash
make run
```
- **Access**: Same machine only
- **Clients**: Single local client (Claude Desktop)
- **Use cases**:
  - Claude Desktop integration
  - Local development
  - Private/offline usage

**To switch modes**, edit `.env`:
```bash
# For HTTP mode (default)
MCP_TRANSPORT=http

# For STDIO mode
MCP_TRANSPORT=stdio
```

### CLI Client (mcp_cli.py)

**Command-line interface for querying the HTTP MCP server with custom requests.**

#### Basic Usage

```bash
# Simple query
python3 mcp_cli.py -q "Generate a bar graph with title 'hello, world'"

# With column headers
python3 mcp_cli.py -q "Scatter plot of expression over time" --headers "Time,Expression,Gene"

# Adjust LLM temperature
python3 mcp_cli.py -q "Create a clustered heatmap" --temperature 0.2

# Connect to remote server
python3 mcp_cli.py -q "Bar chart" --url http://myserver:8000

# JSON output (for piping)
python3 mcp_cli.py -q "Line chart" --json

# Config-only output
python3 mcp_cli.py -q "Line chart" --config-only
```

#### Inside Docker

```bash
# Run directly in container
docker exec -it $(docker ps -q) python3 /app/mcp_cli.py -q "Create a scatter plot"

# Or exec into container first
docker exec -it $(docker ps -q) /bin/bash
python3 mcp_cli.py -q "Pie chart showing market share"
```

#### Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `-q, --query` | Natural language visualization description | Required |
| `--headers` | Comma-separated column headers | Optional |
| `--temperature` | LLM temperature (0.0-1.0) | 0.0 |
| `--url` | MCP server URL | http://localhost:8000 |
| `--json` | Output full JSON response | false |
| `--config-only` | Output only the config (no wrapper) | false |

**Note:** The CLI client connects to the running HTTP MCP server. Make sure the server is running with `make run-http` first.

### Available Tool

The server provides one tool: `generate_canvasxpress_config`

**Parameters:**
- `description` (required): Natural language description of visualization
- `headers` (optional): Column names from your dataset
- `temperature` (optional): LLM temperature, default 0.0

**Example:**

```
Description: "Create a scatter plot with log scale on y-axis, red points, and regression line"
Headers: "Time, Expression, Gene"
Temperature: 0.0
```

### Supported Chart Types

Bar, Boxplot, Scatter, Line, Heatmap, Area, Dotplot, Pie, Venn, Network, Sankey, Genome, Stacked, Circular, Radar, Bubble, Candlestick, and 40+ more.

## 🔧 Configuration

### Environment Variables

Configure your `.env` file with your BMS credentials:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_KEY=your_key_from_genai.web.bms.com
AZURE_OPENAI_API_VERSION=2024-02-01
LLM_MODEL=gpt-4o-global
LLM_ENVIRONMENT=nonprod

# MCP Server Configuration
MCP_TRANSPORT=http              # http (network, default) or stdio (local)
MCP_HOST=0.0.0.0               # HTTP: bind to all interfaces
MCP_PORT=8000                  # HTTP: port to listen on
```

### Available Azure Models

| Model | Description | Best For |
|-------|-------------|----------|
| gpt-4o-mini-global | Fast, cost-effective | Quick prototyping, testing |
| gpt-4o-global | Most capable | Production, complex charts |
| gpt-4-turbo-global | Fast GPT-4 | Balance of speed & quality |

### BMS Proxy Details

- **Endpoints URL**: https://bms-openai-proxy-eus-prod.azu.bms.com/openai-urls.json
- **Retry Logic**: Automatically rotates endpoints on failures (429, connection errors)
- **Max Retries**: 3 attempts per request
- **API Version**: 2024-02-01

## 🛠️ Development

### Makefile Commands

```bash
make help       # Show all commands
make build      # Build Docker image
make init       # Initialize vector database
make test-db    # Test vector database (inspect examples, search)
make run        # Start server (STDIO mode)
make run-http   # Start server (HTTP mode, daemon/background)
make run-httpi  # Start server (HTTP mode, interactive)
make stop       # Stop server
make logs       # View logs
make shell      # Open shell in container
make clean      # Remove container and image
```

### Testing Utilities

#### Vector Database Testing

Test and inspect the Milvus vector database:

```bash
make test-db
```

**What it tests:**
- ✓ Database connection and collection info
- ✓ Row count (should be 132 examples)
- ✓ Sample data display (first 3 examples)
- ✓ Chart type distribution (30 unique types)
- ✓ Vector dimensions (1024 for BGE-M3)
- ✓ Semantic search with 3 sample queries

**Example output:**
```
✓ Collections: ['few_shot_examples']
✓ Row count: 132
✓ Total unique chart types: 30
✓ Vector dimension: 1024 (BGE-M3) or 1536 (OpenAI) or 768 (Gemini)

🔍 SEMANTIC SEARCH TEST
Query: 'bar chart with blue bars'
--- Result 1 (Similarity: 0.5845) ---
ID: 11
Type: Bar
Description: Create a bar graph with vertical orientation...
```

This is useful for:
- Verifying database initialization
- Understanding what examples are available
- Testing semantic search quality
- Debugging RAG retrieval issues

#### Python Usage Examples

Test the generator as a Python library:

```bash
# Set environment variables
source <(sed 's/^/export /' .env)

# Run examples
python3 examples_usage.py
```

See `examples_usage.py` and `PYTHON_USAGE.md` for detailed usage patterns.

### Directory Structure

```
canvasxpress-mcp-server/
├── data/                       # Few-shot examples and schema
│   ├── few_shot_examples.json  # 132 examples (66 configs × 2 descriptions)
│   ├── schema.txt              # CanvasXpress config schema
│   └── prompt_template.md      # LLM prompt template
├── src/                        # Source code
│   ├── canvasxpress_generator.py  # Core RAG pipeline + provider classes
│   └── mcp_server.py           # FastMCP server entry point
├── scripts/                    # Utility scripts
│   └── init_vector_db.py       # Local venv DB initialization
├── vector_db/                  # Vector database (auto-created)
│   └── canvasxpress_mcp.db     # Milvus database with embeddings
├── venv/                       # Python venv (if using local setup)
├── mcp_cli.py                  # CLI client for HTTP server
├── mcp_http_client.py          # HTTP client examples
├── test_vector_db.py           # Vector database testing utility
├── examples_usage.py           # Python usage examples
├── Dockerfile
├── Makefile
├── requirements.txt            # Full deps (with PyTorch/BGE-M3)
├── requirements-light.txt      # Lightweight deps (cloud only)
├── .env.example
└── README.md
```

### Local Testing (without Docker)

For local development, use the virtual environment setup:

```bash
# Create venv (full or lightweight)
make venv        # Full (~8GB, includes BGE-M3)
make venv-light  # Lightweight (~500MB, cloud embeddings)

# Configure environment
cp .env.example .env
nano .env  # Add your API key, set EMBEDDING_PROVIDER if using venv-light

# Initialize database
make init-local

# Start server
make run-local   # HTTP mode
make run-locali  # STDIO mode

# Test with CLI
source venv/bin/activate
python mcp_cli.py -q "Create a bar chart"
```

See the "Local Development" section above for detailed instructions.

## 📊 Methodology

Based on peer-reviewed research (Smith & Neuhaus, 2024):

1. **Embedding Model**: BGE-M3 (1024d, local) or cloud alternatives (OpenAI 1536d, Gemini 768d)
2. **Vector DB**: Milvus-lite (local SQLite-based storage)
3. **Few-Shot Examples**: 132 examples (66 configs with human + GPT-4 descriptions)
4. **Retrieval**: Top 25 most similar examples per query
5. **LLM**: Azure OpenAI (BMS proxy) or Google Gemini
6. **Retry Logic**: Endpoint rotation on failures (BMS proxy pattern)

**Performance (with BGE-M3 + Azure OpenAI):**
- 93% exact match accuracy
- 98% similarity score
- Handles 30+ chart types
- Automatic failover across Azure regions

## 🐛 Troubleshooting

### Server won't start

```bash
# Check logs
make logs

# Verify .env file exists
ls -la .env

# Rebuild
make clean
make build
make init
```

### Vector database errors

```bash
# Test the database first
make test-db

# If you see "Row count: 0" or errors, reinitialize:
sudo rm -rf vector_db/canvasxpress_mcp.db vector_db/milvus
make init

# Verify it worked
make test-db
```

**Note:** The vector database files are created by Docker with root ownership, so you need `sudo` to delete them.

### Empty database after init

If `make init` shows success but `make test-db` reports 0 rows:

```bash
# The collection exists but is empty, force recreation
sudo rm -rf vector_db/canvasxpress_mcp.db vector_db/milvus
make init
```

This ensures the database is populated with all 132 examples.

### Testing semantic search

```bash
# Run the test utility to see RAG in action
make test-db

# This will:
# - Show all 132 examples are loaded
# - Display chart type distribution
# - Run sample semantic searches
# - Verify embedding dimensions (1024)
```

### API key issues

```bash
# Test API key and BMS proxy
docker run --rm --env-file .env canvasxpress-mcp-server:latest \
  python -c "import os, requests; print('Key:', os.environ.get('AZURE_OPENAI_KEY')); r = requests.get('https://bms-openai-proxy-eus-prod.azu.bms.com/openai-urls.json'); print('Proxy:', r.status_code)"
```

### BMS Proxy Issues

```bash
# Check if you can reach BMS proxy
curl https://bms-openai-proxy-eus-prod.azu.bms.com/openai-urls.json

# If timeout, ensure you're on BMS network or VPN
```

### Claude Desktop not connecting

1. Check config file path: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Verify server is running: `docker ps | grep canvasxpress`
3. Restart Claude Desktop
4. Check Claude Desktop logs: `~/Library/Logs/Claude/`

## 📚 Resources

- **Original Research**: [Smith & Neuhaus (2024) - CanvasXpress NLP Preprint](https://osf.io/preprints/osf/kf2xp_v1)
- **FastMCP 2.0**: https://gofastmcp.com/
- **CanvasXpress**: https://www.canvasxpress.org/
- **MCP Protocol**: https://modelcontextprotocol.io/
- **BGE-M3 Model**: https://huggingface.co/BAAI/bge-m3

## 📝 License

Based on reference implementation (JOSS publication).
MCP server implementation: MIT License

## 🤝 Contributing

Issues and pull requests welcome!

## 📧 Support

For issues related to:
- **MCP Server**: Open GitHub issue
- **CanvasXpress**: See https://www.canvasxpress.org/documentation.html
- **MCP Protocol**: See https://modelcontextprotocol.io/docs

---

**Built with ❤️ using [FastMCP 2.0](https://gofastmcp.com) and the Model Context Protocol**
