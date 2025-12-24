# Interactive Test Shell

## Quick Start

```bash
make test-shell
```

This opens an interactive bash shell inside a Docker container with:
- ✅ All dependencies installed
- ✅ Vector database mounted at `/root/.cache/`
- ✅ Environment variables loaded from `.env`
- ✅ All source code available in `/app/`

## What You Can Do

### 1. Run the Examples Script

```bash
# Inside the test shell:
python /app/examples_usage.py
```

This will:
- Generate a bar chart (Example 1)
- Inspect RAG retrieval (Example 4)
- Show how to use the generator as a Python library

### 2. Test the Vector Database

```bash
python /app/test_vector_db.py
```

Comprehensive database testing with:
- Database info (132 examples)
- Chart type distribution
- Semantic search demos

### 3. Interactive Python

```bash
# Start Python REPL
python

# Then try:
>>> import sys
>>> sys.path.insert(0, '/app/src')
>>> from canvasxpress_generator import CanvasXpressGenerator
>>> 
>>> gen = CanvasXpressGenerator(
...     data_dir='/app/data',
...     vector_db_path='/root/.cache/canvasxpress_mcp.db'
... )
>>> 
>>> # Get similar examples (no API call)
>>> examples = gen.get_similar_examples("bar chart with blue bars", num_examples=3)
>>> for ex in examples:
...     print(f"{ex['type']}: {ex['score']:.4f}")
>>> 
>>> # Generate a chart (makes API call)
>>> config = gen.generate("scatter plot with regression line", headers="X, Y")
>>> print(config)
```

### 4. Explore the Data

```bash
# View few-shot examples
head -n 50 /app/data/few_shot_examples.json | python -m json.tool

# Count chart types
python -c "import json; data = json.load(open('/app/data/few_shot_examples.json')); types = {}; [types.update({d['type']: types.get(d['type'], 0) + 1}) for d in data]; print('\n'.join(f'{k}: {v}' for k, v in sorted(types.items(), key=lambda x: -x[1])))"

# Check schema
head -n 20 /app/data/schema.md
```

### 5. Inspect Vector Database

```bash
# Check database file
ls -lh /root/.cache/canvasxpress_mcp.db

# Check HuggingFace cache (BGE-M3 model)
du -sh /root/.cache/huggingface/

# Python inspection
python -c "from pymilvus import MilvusClient; client = MilvusClient('/root/.cache/canvasxpress_mcp.db'); print('Collections:', client.list_collections()); print('Stats:', client.get_collection_stats('few_shot_examples'))"
```

### 6. Test API Connectivity

```bash
# Check which provider is configured
echo "LLM Provider: ${LLM_PROVIDER:-openai}"
echo "Embedding Provider: ${EMBEDDING_PROVIDER:-local}"

# Test BMS proxy (if using openai provider)
curl -s https://bms-openai-proxy-eus-prod.azu.bms.com/openai-urls.json | python -m json.tool

# Check environment
echo "API Key: ${AZURE_OPENAI_KEY:0:10}..."
echo "Gemini Key: ${GEMINI_API_KEY:0:10}..."
echo "Model: $LLM_MODEL"
echo "Environment: $LLM_ENVIRONMENT"
```

### 7. Run Custom Python Code

Create a test script on the fly:

```bash
cat > /tmp/my_test.py << 'EOF'
import sys
sys.path.insert(0, '/app/src')
from canvasxpress_generator import CanvasXpressGenerator

gen = CanvasXpressGenerator(
    data_dir='/app/data',
    vector_db_path='/root/.cache/canvasxpress_mcp.db'
)

# Your custom test
description = "heatmap with dendrograms"
similar = gen.get_similar_examples(description, num_examples=5)

print(f"\nTop 5 examples for: '{description}'\n")
for i, ex in enumerate(similar, 1):
    print(f"{i}. {ex['type']} (score: {ex['score']:.4f})")
    print(f"   {ex['description'][:100]}...\n")
EOF

python /tmp/my_test.py
```

## Example Session

```bash
$ make test-shell
🐚 Starting interactive test shell...
📁 Vector database mounted at: /root/.cache/
📝 Example scripts available: /app/examples_usage.py

root@abc123:/app# 

# Test the database
root@abc123:/app# python test_vector_db.py
... (test output)

# Run examples
root@abc123:/app# python examples_usage.py
🚀 CanvasXpress Generator - Python Tool Examples
============================================================
Example 1: Basic Bar Chart
============================================================
... (generates chart)

# Interactive Python
root@abc123:/app# python
>>> import sys; sys.path.insert(0, 'src')
>>> from canvasxpress_generator import CanvasXpressGenerator
>>> gen = CanvasXpressGenerator(data_dir='data', vector_db_path='/root/.cache/canvasxpress_mcp.db')
... (interactive testing)

# Exit when done
root@abc123:/app# exit
$
```

## Tips

1. **The container is ephemeral**: Any changes you make (except to `/root/.cache/`) will be lost when you exit. This is by design - it keeps your environment clean.

2. **Vector database persists**: The database at `/root/.cache/` is mounted from your host's `vector_db/` directory, so it persists across sessions.

3. **Environment variables**: The `.env` file is automatically loaded, so `AZURE_OPENAI_KEY`, `GEMINI_API_KEY`, `LLM_PROVIDER`, `EMBEDDING_PROVIDER`, and other vars are available.

4. **Fast iteration**: Make changes to scripts on your host (e.g., edit `examples_usage.py`), rebuild with `make build`, then test again in `make test-shell`.

5. **No GPU needed**: BGE-M3 runs on CPU (if using local embeddings), so embeddings and search work fine without a GPU. For cloud embeddings (OpenAI/Gemini), no local model is required.

## Troubleshooting

### Shell doesn't start

```bash
# Check if .env exists
ls -la .env

# If missing, create it
cp .env.example .env
# Edit .env with your API key
```

### "vector_db not found" warning

```bash
# Initialize the database first
make init

# Then try again
make test-shell
```

### Import errors

```bash
# Inside the shell, check Python path
root@abc123:/app# python -c "import sys; print('\n'.join(sys.path))"

# Should include /app/src
# If not, manually add:
root@abc123:/app# export PYTHONPATH=/app/src:$PYTHONPATH
```

### API errors

```bash
# Verify environment variables
root@abc123:/app# env | grep AZURE
root@abc123:/app# env | grep LLM

# Test connectivity
root@abc123:/app# curl https://bms-openai-proxy-eus-prod.azu.bms.com/openai-urls.json
```

## Comparison with Other Targets

| Command | Purpose | Interactive? | API Calls? |
|---------|---------|--------------|------------|
| `make test-db` | Test vector database | No | No |
| `make test-shell` | Interactive testing | Yes | Optional |
| `make shell` | Shell in running server | Yes | N/A |
| `make run` | Start MCP server | No | Yes (when used) |

- **`make test-db`**: Quick automated test, no interaction
- **`make test-shell`**: Full control, run any commands you want
- **`make shell`**: For debugging the running server container
- **`make run`**: Production mode, server runs in background

## Exit the Shell

```bash
root@abc123:/app# exit
# or press Ctrl+D
```

The container is automatically removed when you exit (`--rm` flag).

---

**Happy testing!** 🧪
