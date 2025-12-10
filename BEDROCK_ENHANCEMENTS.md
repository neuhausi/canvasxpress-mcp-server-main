# Enhancing MCP Server with Bedrock Agent Knowledge Base

This document outlines enhancements from the AWS Bedrock CanvasXpress Agent (`smitha26-bedrock-canvasxpress-agent`) that could be ported to this MCP server.

---

## Summary Comparison

| Aspect | MCP Server (Current) | Bedrock Agent |
|--------|---------------------|---------------|
| **Few-shot examples** | 132 | ~13,460 |
| **Knowledge docs** | `schema.txt` + `prompt_template.md` | 10 specialized modules (~150KB) |
| **Decision guidance** | None | Full decision tree |
| **Rules** | Basic in prompt | 52+ comprehensive rules |
| **Metadata per example** | Minimal | Rich (chart_type, use_case, complexity) |

---

## Enhancement 1: Add Knowledge Base Documents

The Bedrock agent has 10 specialized knowledge modules in `kb_content/`. These could be added to our `data/` folder and incorporated into the prompt.

### Files to Port

| File | Size | Purpose |
|------|------|---------|
| `canvasxpress_rules.md` | 17KB | Comprehensive rules for all chart types, axis config, decorations |
| `canvasxpress_schema.md` | 32KB | Complete field definitions and valid options |
| `DECISION-TREE.md` | 5KB | Chart type selection based on data dimensionality |
| `PARAMETER-COMPATIBILITY-MATRIX.md` | 9KB | Which parameters work together |
| `CONTRADICTIONS.md` | 3KB | Parameter conflict identification |
| `MINIMAL-PARAMETERS.md` | 3KB | Essential params per chart type |
| `CHAIN-OF-THOUGHT.md` | 2KB | Systematic problem-solving approaches |
| `COMPARISON.md` | 11KB | Feature comparisons between chart types |
| `CONTEXT.md` | 35KB | CanvasXpress ecosystem context |
| `OVERVIEW.md` | 34KB | High-level capabilities |

### Implementation

1. **Copy files to MCP server:**
   ```bash
   cp ../smitha26-bedrock-canvasxpress-agent/kb_content/*.md data/knowledge/
   ```

2. **Update `canvasxpress_generator.py` to load knowledge docs:**
   ```python
   def __init__(self, ...):
       # Load knowledge base documents
       self.knowledge_docs = {}
       knowledge_dir = os.path.join(data_dir, "knowledge")
       for filename in os.listdir(knowledge_dir):
           if filename.endswith('.md'):
               with open(os.path.join(knowledge_dir, filename)) as f:
                   self.knowledge_docs[filename] = f.read()
   ```

3. **Include relevant docs in prompt:**
   ```python
   def build_prompt(self, description, headers, similar_examples):
       # Add decision tree for chart selection
       decision_tree = self.knowledge_docs.get('DECISION-TREE.md', '')
       rules = self.knowledge_docs.get('canvasxpress_rules.md', '')
       # ... include in prompt template
   ```

---

## Enhancement 2: Expand Few-Shot Examples

The Bedrock agent has ~13,460 examples vs our 132. These are stored as `.txt` + `.txt.metadata.json` pairs.

### Conversion Script

The Bedrock repo includes `convert_fewshots.py` which converts JSON examples to Bedrock format. We could reverse this or use the source JSON files directly.

### Option A: Convert Bedrock Examples to MCP Format

```python
import os
import json

def convert_bedrock_to_mcp(kb_fewshots_dir, output_file):
    examples = []
    example_id = 0
    
    for filename in os.listdir(kb_fewshots_dir):
        if filename.endswith('.txt') and not filename.endswith('.metadata.json'):
            # Read description
            with open(os.path.join(kb_fewshots_dir, filename)) as f:
                description = f.read().strip()
            
            # Read metadata
            metadata_file = filename + '.metadata.json'
            with open(os.path.join(kb_fewshots_dir, metadata_file)) as f:
                metadata = json.load(f)
            
            attrs = metadata['metadataAttributes']
            config = json.loads(attrs['canvasxpress_config'])
            
            examples.append({
                "id": example_id,
                "type": attrs['chart_type'],
                "description": description,
                "config": config,
                "headers": ",".join(attrs['data_columns']),
                "source": "bedrock"
            })
            example_id += 1
    
    with open(output_file, 'w') as f:
        json.dump(examples, f, indent=2)
    
    print(f"Converted {len(examples)} examples")
```

### Option B: Sample Subset

The full 13K examples may be overkill. Consider sampling:
- 10-20 examples per chart type
- Focus on different complexity levels
- Include edge cases

---

## Enhancement 3: Improve Prompt Template

The Bedrock agent's `canvasxpress_rules.md` contains detailed rules that could replace or augment our `prompt_template.md`.

### Key Rules to Add

1. **Axis Configuration Rules:**
   - Single-dimensional charts use only `xAxis`
   - Multi-dimensional charts use both `xAxis` and `yAxis`
   - Combined chart types use `xAxis` and `xAxis2`

2. **Decoration Rules:**
   - Only use `line`, `point`, or `text` keys
   - Arrays even for single objects
   - Only one of `x`, `y`, or `value` per decoration

3. **Graph-Specific Rules:**
   - Area: Must include `areaType` (stacked/percent/overlapping)
   - Contour: Must include both `xAxis` and `yAxis`
   - Density: Must include `densityPosition`
   - Histogram: Must include `histogramType`
   - Ridgeline: Use `ridgeBy` instead of `groupingFactors`

4. **Valid Values Lists:**
   - 60+ valid `graphType` values
   - Valid color schemes (ColorBrewer-based)
   - Valid themes (ggplot2-based)

---

## Enhancement 4: Add Decision Tree Logic

The `DECISION-TREE.md` provides structured chart selection. This could be:

1. **Added to prompt** - Let LLM use it for reasoning
2. **Pre-processing step** - Analyze query and suggest chart type before RAG

### Decision Tree Structure

```
ONE-DIMENSIONAL DATA:
├── Goal: Compare categories → Bar, Lollipop, Cleveland
├── Goal: Show distribution → Histogram, Density, Boxplot, Violin
├── Goal: Part-to-whole → Pie, Donut, Treemap, Sunburst
├── Goal: Show ranking → Bar, Pareto
└── Goal: Time series → Line, Area, Streamgraph

TWO-DIMENSIONAL DATA:
├── Goal: Correlation → Scatter2D, ScatterBubble2D, Contour
├── Goal: Time series + multiple vars → Line, Spaghetti
└── Goal: Compare metrics → BarLine, Radar, ParallelCoordinates

NETWORK/RELATIONSHIP DATA:
├── Hierarchical → Tree, Treemap, Sunburst
├── General network → Network
└── Flow → Sankey, Chord, Alluvial
```

---

## Enhancement 5: Rich Metadata for Examples

Bedrock examples include metadata that improves retrieval:

```json
{
  "metadataAttributes": {
    "chart_type": "Alluvial",
    "data_columns": ["Id", "Age", "Class", "Sex"],
    "canvasxpress_config": "{...}",
    "explanation": "This configuration creates...",
    "use_case": "categorical_comparison",
    "complexity": "intermediate"
  }
}
```

### Add to MCP Examples

Extend `few_shot_examples.json`:
```json
{
  "id": 0,
  "type": "Bar",
  "description": "...",
  "config": {...},
  "headers": "...",
  "source": "human",
  "use_case": "categorical_comparison",
  "complexity": "basic",
  "explanation": "Creates a bar chart for comparing categories"
}
```

This enables:
- Filtering by use case during retrieval
- Complexity-based ranking
- Better explanations in responses

---

## Enhancement 6: Parameter Compatibility Checking

The `PARAMETER-COMPATIBILITY-MATRIX.md` and `CONTRADICTIONS.md` files define which parameters work together.

### Post-Processing Validation

```python
def validate_config(config):
    """Check for parameter conflicts."""
    graph_type = config.get('graphType')
    
    # Single-dimensional charts shouldn't have yAxis
    single_dim = ['Bar', 'Boxplot', 'Pie', 'Histogram', ...]
    if graph_type in single_dim and 'yAxis' in config:
        del config['yAxis']
        
    # Ridgeline uses ridgeBy, not groupingFactors
    if graph_type == 'Ridgeline' and 'groupingFactors' in config:
        config['ridgeBy'] = config.pop('groupingFactors')
    
    return config
```

---

## Priority Order for Implementation

1. **High Impact, Low Effort:**
   - Copy `DECISION-TREE.md` → add to prompt
   - Copy `canvasxpress_rules.md` → replace/augment prompt template

2. **High Impact, Medium Effort:**
   - Sample 500-1000 examples from Bedrock's 13K
   - Add to vector DB (requires `make init`)

3. **Medium Impact, Medium Effort:**
   - Add metadata fields to examples
   - Update retrieval to use metadata

4. **Lower Priority:**
   - Post-processing validation
   - Full knowledge base integration

---

## File Locations

Bedrock agent repo: `../smitha26-bedrock-canvasxpress-agent/`

| Bedrock Path | Description |
|--------------|-------------|
| `kb_content/*.md` | Knowledge base documents |
| `kb_fewshots/` | 13K+ few-shot examples |
| `convert_fewshots.py` | Conversion utility |
| `README_FEWSHOT_CONVERSION.md` | Conversion docs |

---

## Notes

- The Bedrock agent uses OpenSearch Serverless for vector search; we use Milvus-lite
- Bedrock examples use 768-dim embeddings; we use 1024-dim BGE-M3
- If switching to cloud embeddings (Gemini), dimensions would need to match
- Adding all 13K examples would significantly increase `make init` time
