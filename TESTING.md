# Testing Guide

Complete testing guide for the CanvasXpress MCP Server.

## Quick Test Overview

```bash
# 1. Test vector database (132 examples)
make test-db

# 2. Test HTTP MCP client (generates 3 charts via MCP protocol)
docker exec -it $(docker ps -q --filter ancestor=canvasxpress-mcp-server:latest) python3 /app/mcp_http_client.py

# 3. Test direct Python API (no MCP)
python3 examples_usage.py
```

**See also:**
- `HTTP_CLIENT_GUIDE.md` - Complete guide to HTTP/network testing
- `test_mcp_protocol.py` - Protocol-level testing and validation

---

## Vector Database Testing Utility

### Quick Start

```bash
# Test the vector database
make test-db
```

### What It Does

The `test_vector_db.py` utility performs comprehensive testing of the Milvus vector database:

1. **Database Information**
   - Verifies connection to `vector_db/canvasxpress_mcp.db`
   - Lists all collections (should be `few_shot_examples`)
   - Checks row count (should be 132)

2. **Sample Data Inspection**
   - Displays first 3 examples with:
     - ID, Type, Description
   - Helps you understand what data is stored

3. **Chart Type Distribution**
   - Shows all 30 unique chart types
   - Example output:
     ```
     Scatter2D            :  12 examples
     Boxplot              :  10 examples
     Histogram            :  10 examples
     Area                 :   8 examples
     Bar                  :   8 examples
     ...
     ```

4. **Vector Dimensions**
   - Verifies embeddings are properly dimensioned:
     - BGE-M3 (local): 1024-dimensional
     - OpenAI: 1536-dimensional
     - Gemini: 768-dimensional
   - Shows sample embedding values

5. **Semantic Search Testing**
   - Runs 3 test queries:
     - "bar chart with blue bars"
     - "scatter plot with regression line"
     - "heatmap showing gene expression"
   - Shows similarity scores and retrieved examples
   - Demonstrates RAG (Retrieval Augmented Generation) in action

### Example Output

```
======================================================================
  🧪 CANVASXPRESS VECTOR DATABASE TESTING UTILITY
======================================================================

======================================================================
  📊 DATABASE INFORMATION
======================================================================

✓ Collections: ['few_shot_examples']
✓ Collection name: few_shot_examples
✓ Row count: 132

======================================================================
  📈 CHART TYPE DISTRIBUTION
======================================================================

  Scatter2D            :  12 examples
  Boxplot              :  10 examples
  Histogram            :  10 examples
  Area                 :   8 examples
  Bar                  :   8 examples
  Density              :   8 examples
  Ridgeline            :   8 examples
  ...

✓ Total unique chart types: 30

======================================================================
  🔍 SEMANTIC SEARCH TEST
======================================================================

Query: 'scatter plot with regression line'
Retrieving top 3 most similar examples...

--- Result 1 (Similarity: 0.7282) ---
ID: 100
Type: Scatter2D
Description: Show the correlation between cty and hwy in a scatter plot. 
             Draw the regression fit.

✓ Search completed successfully
```

### When to Use

- **After `make init`**: Verify database was populated correctly
- **Before `make run`**: Ensure all 132 examples are ready
- **Debugging**: If generation quality is poor, check what examples RAG finds
- **Curiosity**: Understand what chart types and examples are available

### Troubleshooting

#### Database Shows 0 Rows

```bash
# Reinitialize (requires sudo due to Docker ownership)
sudo rm -rf vector_db/canvasxpress_mcp.db vector_db/milvus
make init
make test-db
```

#### Permission Denied Errors

The vector database files are created by Docker with root ownership:

```bash
# Use sudo to delete
sudo rm -rf vector_db/canvasxpress_mcp.db

# Or change ownership (if you want to manage manually)
sudo chown -R $(whoami):$(whoami) vector_db/
```

#### Slow First Run

**For local embeddings (default):** The BGE-M3 model (~2GB) is cached in `vector_db/huggingface/`. First run downloads it, subsequent runs are fast.

**For cloud embeddings:** No model download required, but API calls may add latency.

## Python Usage Testing

See `examples_usage.py` for testing the generator as a Python library:

```bash
# Set environment
source <(sed 's/^/export /' .env)

# For cloud embeddings (no PyTorch required):
export EMBEDDING_PROVIDER=openai  # or gemini

# Run examples
python3 examples_usage.py
```

This demonstrates:
- Basic chart generation
- Multiple charts (reusing generator instance)
- Error handling
- Inspecting RAG retrieval
- Saving configs to files

See `PYTHON_USAGE.md` for complete API documentation.

## MCP Server Testing

### With Claude Desktop

1. Configure `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "canvasxpress": {
         "command": "docker",
         "args": ["exec", "-i", "canvasxpress-mcp-server", "python", "/app/src/mcp_server.py"]
       }
     }
   }
   ```

2. Start server: `make run`

3. Test in Claude Desktop:
   > "Use the CanvasXpress tool to create a bar chart with blue bars"

### With FastMCP Inspector (Coming Soon)

```bash
# Using FastMCP development tools
fastmcp dev src/mcp_server.py
```

## Continuous Testing

### In Development

```bash
# Watch for changes and reload
make stop
make build
make init
make test-db
make run
```

### Before Deployment

```bash
# Full test suite
make clean
make build
make init
make test-db  # Should show 132 examples
make run
make logs     # Check for errors
```

## Performance Benchmarks

Expected performance on typical hardware (8GB RAM, no GPU):

### Local Embeddings (BGE-M3)
- **Database init**: 3-5 minutes (one-time)
- **Database test**: 30-60 seconds
- **Chart generation**: 2-5 seconds per chart
- **Semantic search**: ~100ms per query

BGE-M3 runs on CPU, so no GPU is required.

### Cloud Embeddings (OpenAI/Gemini)
- **Database init**: 1-2 minutes (API calls for 132 examples)
- **Database test**: 10-20 seconds
- **Chart generation**: 2-5 seconds per chart
- **Semantic search**: ~200-500ms per query (API latency)

## Next Steps

- ✅ Run `make test-db` to verify your setup
- ✅ Try `python3 examples_usage.py` for Python API
- ✅ Start server with `make run`
- ✅ Configure Claude Desktop for MCP integration

---

**Questions?** See the main [README.md](README.md) or open an issue.
