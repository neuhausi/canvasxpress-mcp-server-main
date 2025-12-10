# Technical Overview

Developer reference for extending the CanvasXpress MCP Server.

---

## Architecture

```
┌──────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│  MCP Client      │────▶│  mcp_server.py      │────▶│  Generator      │
│  (Claude, CLI)   │     │  (FastMCP 2.0)      │     │  (RAG Pipeline) │
└──────────────────┘     └─────────────────────┘     └────────┬────────┘
                                                              │
                         ┌────────────────────────────────────┼────────────────────┐
                         │                                    │                    │
                         ▼                                    ▼                    ▼
                  ┌─────────────┐                    ┌──────────────┐      ┌──────────────┐
                  │ Vector DB   │                    │ Embeddings   │      │ LLM Provider │
                  │ (Milvus)    │                    │ (Pluggable)  │      │ (Pluggable)  │
                  │ 132 examples│                    │              │      │              │
                  └─────────────┘                    └──────────────┘      └──────────────┘
                                                     BGE-M3 (local)        Azure OpenAI
                                                     OpenAI API            Google Gemini
                                                     Gemini API
```

### Provider Support

The server supports multiple LLM and embedding providers via environment variables:

| Component | Options | Default | Env Variable |
|-----------|---------|---------|--------------|
| **LLM** | Azure OpenAI, Google Gemini | `openai` | `LLM_PROVIDER` |
| **Embeddings** | BGE-M3 (local), Azure OpenAI, Google Gemini | `local` | `EMBEDDING_PROVIDER` |

See `.env.example` for full configuration options.

---

## Directory Structure

```
├── src/
│   ├── mcp_server.py           # MCP server entry point (FastMCP)
│   └── canvasxpress_generator.py  # Core RAG logic + provider classes
├── scripts/
│   └── init_vector_db.py       # Local venv DB initialization script
├── data/
│   ├── few_shot_examples.json  # 132 examples (input to vector DB)
│   ├── prompt_template.md      # LLM prompt template
│   └── schema.txt              # CanvasXpress config schema
├── vector_db/                  # Created by `make init` or `make init-local`
│   └── canvasxpress_mcp.db     # Milvus database
├── venv/                       # Created by `make venv` (local dev only)
├── mcp_cli.py                  # CLI client for testing
├── mcp_http_client.py          # HTTP client example
├── test_vector_db.py           # Vector DB test utility
└── examples_usage.py           # Python API usage examples
```

---

## Core Classes & Methods

### `EmbeddingProvider` (src/canvasxpress_generator.py)

Abstract embedding provider supporting multiple backends.

| Method | Purpose |
|--------|---------|
| `__init__(provider)` | Initialize with "local", "openai", or "gemini" |
| `encode(texts)` | Batch encode texts to embeddings |
| `encode_query(text)` | Encode single query text |

**Dimensions by provider:**
- `local` (BGE-M3): 1024
- `openai` (text-embedding-3-small): 1536
- `gemini` (text-embedding-004): 768

### `LLMProvider` (src/canvasxpress_generator.py)

Abstract LLM provider supporting multiple backends.

| Method | Purpose |
|--------|---------|
| `__init__(provider, **kwargs)` | Initialize with "openai" or "gemini" |
| `generate(prompt, temperature, max_retries)` | Generate text from prompt |

### `CanvasXpressGenerator` (src/canvasxpress_generator.py)

Main class that implements the RAG pipeline.

| Method | Purpose |
|--------|---------|
| `__init__(data_dir, vector_db_path, llm_model, llm_environment)` | Initialize generator, load examples, setup vector DB |
| `get_similar_examples(description, num_examples=25)` | Semantic search for similar few-shot examples |
| `build_prompt(description, headers, similar_examples)` | Construct LLM prompt with retrieved examples |
| `generate(description, headers, temperature)` | **Main entry point** - returns CanvasXpress JSON config |

### `mcp_server.py`

FastMCP server that exposes one tool:

```python
@mcp.tool()
def generate_canvasxpress_config(
    description: str,      # Natural language chart description
    headers: str = None,   # Optional column names
    temperature: float = 0.0
) -> str:                  # JSON response (see below)
```

**Response Format:**
```json
{
  "success": true,
  "description": "original user description",
  "headers": "original headers or null",
  "config": {"graphType": "Bar", ...},
  "error": null
}
```

On error:
```json
{
  "success": false,
  "description": "...",
  "headers": "...",
  "config": null,
  "error": "Error message describing what went wrong"
}
```

---

## Data Flow

1. **User Request** → `"Create a bar chart with blue bars"`
2. **Embed Query** → BGE-M3 converts to 1024-dim vector
3. **Vector Search** → Milvus returns top 25 similar examples
4. **Build Prompt** → Template + schema + few-shot examples + user query
5. **LLM Call** → Azure OpenAI generates JSON config
6. **Return** → `{"graphType": "Bar", "colors": ["blue"]}`

---

## Key Files Detail

### `data/few_shot_examples.json`
```json
[
  {
    "id": 0,
    "type": "Area",
    "description": "Area graph of hwy with title...",
    "config": {"graphType": "Area", "xAxis": ["hwy"], ...},
    "headers": "Id,class,cty,cyl,...",
    "source": "human"  // or "gpt4"
  },
  ...
]
```
- 132 examples total (66 charts × 2 descriptions each)
- `source`: "human" = human-written, "gpt4" = GPT-4 generated description

### `data/prompt_template.md`
Template with placeholders:
- `{canvasxpress_config_english}` - User's description
- `{headers_column_names}` - Optional headers
- `{schema_info}` - CanvasXpress schema
- `{few_shot_examples}` - Retrieved examples

### `data/schema.txt`
CanvasXpress configuration schema documentation (properties, types, valid values).

---

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `AZURE_OPENAI_KEY` | BMS Azure API key | `aaa15abe...` |
| `LLM_MODEL` | Model name | `gpt-4o-global` |
| `LLM_ENVIRONMENT` | BMS environment | `nonprod` or `prod` |
| `MCP_TRANSPORT` | Server mode | `http` or `stdio` |
| `MCP_PORT` | HTTP port | `8000` |

---

## Deployment Options

The server supports two deployment methods:

### Option 1: Docker (Recommended for Production)
```bash
make build      # Build Docker image (~8GB due to PyTorch)
make init       # Initialize vector DB
make run-http   # Start server (daemon mode)
```
- **Pros**: Isolated, reproducible, no Python version conflicts
- **Cons**: Large image size, requires Docker

### Option 2: Local Virtual Environment - Full (Development)
```bash
make venv       # Create venv with Python 3.12 (~8GB with PyTorch)
make init-local # Initialize local vector DB
make run-local  # Start server (HTTP mode)
```
- **Pros**: Faster iteration, no Docker required
- **Cons**: Requires Python 3.10+, large disk footprint (~8GB)
- **Use when**: You want local BGE-M3 embeddings (highest accuracy)

### Option 3: Local Virtual Environment - Lightweight ⭐
```bash
make venv-light # Create venv with cloud deps only (~500MB)
# Edit .env: set EMBEDDING_PROVIDER=gemini (or openai)
make init-local # Initialize local vector DB  
make run-local  # Start server (HTTP mode)
```
- **Pros**: Small footprint (~500MB), fast install, no PyTorch
- **Cons**: Requires cloud API for embeddings (Gemini or OpenAI)
- **Use when**: Lightweight servers, or you prefer cloud embeddings

**Path Auto-Detection**: The server (`mcp_server.py`) automatically detects which environment it's running in:
- **Docker**: Uses `/app/data` and `/root/.cache/canvasxpress_mcp.db`
- **Local**: Uses `./data` and `./vector_db/canvasxpress_mcp.db`

---

## Extending the Server

### Add More Few-Shot Examples
1. Edit `data/few_shot_examples.json` - add new entries:
   ```json
   {
     "id": 133,
     "type": "NewChartType",
     "description": "Natural language description...",
     "config": {"graphType": "NewChartType", ...},
     "headers": "Col1,Col2,Col3",
     "source": "human"
   }
   ```
2. Delete existing vector DB: `sudo rm -rf vector_db/canvasxpress_mcp.db`
3. Rebuild: `make init`

### Update Prompt Template
Edit `data/prompt_template.md` to modify how the LLM prompt is constructed.
The template uses Python format strings: `{canvasxpress_config_english}`, `{headers_column_names}`, `{schema_info}`, `{few_shot_examples}`.

### Add New Chart Types
1. Add examples to `data/few_shot_examples.json` (see above)
2. Update `data/schema.txt` with new config properties/values
3. Rebuild vector DB: `make init`

### Configure Providers

The server supports multiple LLM and embedding providers. Configure via `.env`:

**LLM Providers (currently supported):**
- `openai` - Azure OpenAI via BMS Proxy (default)
- `gemini` - Google Gemini

**Embedding Providers (currently supported):**
- `local` - BGE-M3 local model (default, 1024 dimensions)
- `openai` - Azure OpenAI text-embedding-3-small (1536 dimensions)
- `gemini` - Google Gemini text-embedding-004 (768 dimensions)

Example `.env` for full Gemini setup:
```bash
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=gemini
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_EMBEDDING_MODEL=text-embedding-004
```

> **Note:** If you change `EMBEDDING_PROVIDER`, you must reinitialize the vector database since different providers have different embedding dimensions.

### Add a New LLM Provider

To add a new provider (e.g., Anthropic Claude):

1. **Add to `LLMProvider` class in `canvasxpress_generator.py`:**
   ```python
   def _init_anthropic(self, **kwargs):
       import anthropic
       self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
   
   def _generate_anthropic(self, prompt, temperature, max_retries):
       response = self.client.messages.create(...)
       return response.content[0].text
   ```

2. **Add conditional import at module level:**
   ```python
   if LLM_PROVIDER == "anthropic":
       import anthropic
   ```

3. **Update `requirements.txt` (or `requirements-light.txt`):**
   ```
   anthropic>=0.20.0
   ```

### Add a New MCP Tool
```python
# In src/mcp_server.py
@mcp.tool()
def my_new_tool(param1: str, param2: int = 10) -> str:
    """Tool description shown to AI assistants."""
    # Implementation
    return result
```

### Change Embedding Model
Edit `canvasxpress_generator.py`:
```python
self.bge_m3_ef = BGEM3FlagModel('BAAI/bge-m3', ...)  # Change model here
```
Note: Update `dimension=1024` in `_setup_vector_db()` if dimensions change.

### Using Cloud Embeddings (Implemented)

Cloud embeddings are now supported as an alternative to local BGE-M3. This reduces Docker image size from ~8GB to ~1-2GB since PyTorch is not required.

**Available Providers:**

| Provider | `EMBEDDING_PROVIDER` | Dimension | Notes |
|----------|---------------------|-----------|-------|
| BGE-M3 (local) | `local` | 1024 | Default, proven accuracy, requires PyTorch |
| Azure OpenAI | `openai` | 1536 | Uses `text-embedding-3-small` |
| Google Gemini | `gemini` | 768 | Free tier: 1,500 req/min |

**To use cloud embeddings:**

1. **Set provider in `.env`:**
   ```bash
   EMBEDDING_PROVIDER=gemini  # or "openai"
   GOOGLE_API_KEY=your_key    # for gemini
   # or AZURE_OPENAI_KEY for openai
   ```

2. **Delete and reinitialize vector DB:**
   ```bash
   rm -rf vector_db
   make init-local  # or make init for Docker
   ```

3. **(Optional) Reduce Docker image size:**
   If using cloud embeddings exclusively, you can comment out PyTorch dependencies in `requirements.txt`:
   ```
   # torch>=2.0.0          # Not needed for cloud embeddings
   # FlagEmbedding>=1.2.10
   # sentence-transformers>=3.0.0
   ```

**Note:** You cannot mix embedding providers - all examples must be embedded with the same provider. Switching requires re-embedding all 132 examples.

---

## Testing

```bash
make test-db      # Verify vector DB (132 examples, search test)
make run-http     # Start server (daemon)
python3 mcp_cli.py -q "bar chart"              # Pretty formatted output
python3 mcp_cli.py -q "bar chart" --json       # Full JSON response
python3 mcp_cli.py -q "bar chart" --config-only  # Just the config
make stop         # Stop server
```

---

## Dependencies

Key packages (see `requirements.txt`):
- `fastmcp>=2.0.0` - MCP server framework
- `pymilvus[milvus-lite]` - Vector database
- `FlagEmbedding` - BGE-M3 embeddings
- `openai` - Azure OpenAI client
