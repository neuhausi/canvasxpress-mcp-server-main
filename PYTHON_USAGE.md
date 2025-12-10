# Using CanvasXpress Generator as a Python Tool

## 🚀 Quick Start

### Minimal Example (Azure OpenAI)

```python
import os
import sys
sys.path.insert(0, 'src')

from canvasxpress_generator import CanvasXpressGenerator

# Set environment for Azure OpenAI
os.environ['AZURE_OPENAI_KEY'] = 'your_key_here'
os.environ['LLM_MODEL'] = 'gpt-4o-global'
os.environ['LLM_ENVIRONMENT'] = 'nonprod'
os.environ['LLM_PROVIDER'] = 'openai'
os.environ['EMBEDDING_PROVIDER'] = 'local'  # or 'openai', 'gemini'

# Initialize (do this ONCE, reuse the instance)
generator = CanvasXpressGenerator(
    data_dir='data',
    vector_db_path='vector_db/canvasxpress_mcp.db',
    llm_model='gpt-4o-global',
    llm_environment='nonprod'
)

# Generate a chart config
config = generator.generate(
    description="Bar chart with blue bars and legend on right",
    headers="Region, Sales"
)

print(config)  # Returns dict with CanvasXpress JSON config
```

### Minimal Example (Google Gemini)

```python
import os
import sys
sys.path.insert(0, 'src')

from canvasxpress_generator import CanvasXpressGenerator

# Set environment for Gemini
os.environ['GOOGLE_API_KEY'] = 'your_key_here'
os.environ['LLM_PROVIDER'] = 'gemini'
os.environ['GEMINI_MODEL'] = 'gemini-2.0-flash-exp'
os.environ['EMBEDDING_PROVIDER'] = 'gemini'  # or 'local' for BGE-M3

# Initialize
generator = CanvasXpressGenerator(
    data_dir='data',
    vector_db_path='vector_db/canvasxpress_mcp.db'
)

config = generator.generate("Scatter plot with red points")
print(config)
```

---

## 📚 API Reference

### `CanvasXpressGenerator.__init__()`

```python
generator = CanvasXpressGenerator(
    data_dir='data',                    # Where few-shot examples are
    vector_db_path='vector_db/...',     # Milvus database location
    llm_model='gpt-4o-global',          # Azure model name
    llm_environment='nonprod'           # BMS environment (nonprod/prod)
)
```

**What it does:**
- Loads 132 few-shot examples
- Initializes embedding model (BGE-M3 local, or cloud API)
- Connects to Milvus vector database
- Sets up LLM client (Azure OpenAI or Gemini)

**Note:** This is expensive (2-3 seconds), so create ONE instance and reuse it!

---

### `generator.generate()`

```python
config = generator.generate(
    description="Natural language chart description",
    headers="Column1, Column2, Column3",  # Optional
    temperature=0.0,                       # Optional (0.0 = deterministic)
    max_retries=3                         # Optional (endpoint retry count)
)
```

**Returns:** `dict` - CanvasXpress JSON configuration

**Raises:**
- `json.JSONDecodeError` - LLM returned invalid JSON
- `RuntimeError` - All Azure OpenAI endpoints failed

**Example:**
```python
config = generator.generate(
    description="Scatter plot with red points, log scale on y-axis",
    headers="Time, Expression, Gene"
)
# Returns: {"graphType": "Scatter", "xAxis": ["Time"], ...}
```

---

### `generator.get_similar_examples()`

```python
examples = generator.get_similar_examples(
    description="Your chart description",
    num_examples=25  # Default: 25
)
```

**Returns:** `list[dict]` - Most similar examples from vector database

**Use case:** Inspect what the RAG system finds (useful for debugging)

**Example:**
```python
similar = generator.get_similar_examples(
    "Heatmap with clustering",
    num_examples=5
)
for ex in similar:
    print(ex['type'], ex['description'], ex['score'])
```

---

## 💡 Usage Patterns

### Pattern 1: Single Chart

```python
# Initialize once
generator = CanvasXpressGenerator(...)

# Generate
config = generator.generate("Bar chart with blue bars")
```

### Pattern 2: Multiple Charts (Efficient)

```python
# Initialize ONCE
generator = CanvasXpressGenerator(...)

# Generate many charts (reuses embeddings, DB, model)
configs = []
for description in chart_descriptions:
    config = generator.generate(description)
    configs.append(config)
```

### Pattern 3: With Error Handling

```python
try:
    config = generator.generate(description)
except json.JSONDecodeError:
    print("LLM returned invalid JSON, try again")
except RuntimeError as e:
    print(f"All endpoints failed: {e}")
```

### Pattern 4: Batch Processing

```python
import pandas as pd

# Load chart requests from CSV
df = pd.read_csv('chart_requests.csv')

generator = CanvasXpressGenerator(...)

results = []
for _, row in df.iterrows():
    config = generator.generate(
        description=row['description'],
        headers=row['headers']
    )
    results.append({
        'id': row['id'],
        'config': config
    })

# Save results
pd.DataFrame(results).to_json('generated_configs.json')
```

---

## 🔧 Configuration

### Environment Variables

```bash
export AZURE_OPENAI_KEY=aaa15abe392d6274ca83981bb68c1383
export AZURE_OPENAI_API_VERSION=2024-02-01
export LLM_MODEL=gpt-4o-global
export LLM_ENVIRONMENT=nonprod
```

Or set in Python:
```python
import os
os.environ['AZURE_OPENAI_KEY'] = 'your_key'
os.environ['LLM_MODEL'] = 'gpt-4o-global'
os.environ['LLM_ENVIRONMENT'] = 'nonprod'
```

### Available Models

| Model | Speed | Cost | Quality |
|-------|-------|------|---------|
| gpt-4o-mini-global | ⚡⚡⚡ | 💰 | ⭐⭐⭐ |
| gpt-4o-global | ⚡⚡ | 💰💰💰 | ⭐⭐⭐⭐ |
| gpt-4-turbo-global | ⚡⚡ | 💰💰 | ⭐⭐⭐⭐ |

---

## 📝 Complete Example

See `examples_usage.py` for full working examples:

```bash
# Set environment
export AZURE_OPENAI_KEY=your_key_here
export LLM_MODEL=gpt-4o-global
export LLM_ENVIRONMENT=nonprod

# Run examples
python3 examples_usage.py
```

---

## 🚨 Common Issues

### Issue: "AZURE_OPENAI_KEY not set"
**Solution:** Set environment variable before importing

### Issue: "Failed to fetch BMS OpenAI endpoints"
**Solution:** Ensure you're on BMS network/VPN

### Issue: "No such file or directory: 'data/few_shot_examples.json'"
**Solution:** Run from project root directory

### Issue: Generator initialization takes forever
**Solution:** Normal on first run (downloads BGE-M3 model ~2GB)

### Issue: "RuntimeError: Azure OpenAI call failed after 3 attempts"
**Solution:** Check API key, network, and BMS proxy access

---

## 🎯 Best Practices

1. **Reuse generator instance** - Don't create new instance for each chart
2. **Use temperature=0.0** - For consistent, reproducible configs
3. **Add error handling** - Azure endpoints can fail, retry logic is built-in
4. **Batch processing** - Generate multiple charts in one session
5. **Inspect examples** - Use `get_similar_examples()` to debug poor results

---

## 📚 Integration Examples

### With Flask

```python
from flask import Flask, request, jsonify
from canvasxpress_generator import CanvasXpressGenerator

app = Flask(__name__)
generator = CanvasXpressGenerator(...)  # Initialize once at startup

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    config = generator.generate(
        description=data['description'],
        headers=data.get('headers')
    )
    return jsonify(config)
```

### With Jupyter Notebook

```python
from canvasxpress_generator import CanvasXpressGenerator
import os

os.environ['AZURE_OPENAI_KEY'] = 'your_key'
generator = CanvasXpressGenerator(...)

# Generate in notebook
config = generator.generate("Scatter plot with regression line")
print(config)
```

### With Command Line Script

```python
#!/usr/bin/env python3
import sys
from canvasxpress_generator import CanvasXpressGenerator

generator = CanvasXpressGenerator(...)
config = generator.generate(sys.argv[1])
print(config)
```

Usage: `./generate.py "Bar chart with blue bars"`

---

## 🔗 Related Files

- `examples_usage.py` - Full working examples
- `test_generator.py` - Simple test script
- `src/canvasxpress_generator.py` - Source code
- `README.md` - Full documentation
