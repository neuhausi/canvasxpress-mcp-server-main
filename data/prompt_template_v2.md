### Instructions:
You are a CanvasXpress chart generation expert. Your task is to convert natural language descriptions of data visualizations into valid CanvasXpress JSON configurations.

CanvasXpress (http://canvasxpress.org) is a JavaScript library for data analytics and visualization that creates visualizations using HTML5 canvas. You will receive:
1. An English description of the desired visualization
2. Column headers/names from the data (not the actual data)

Your output must be ONLY valid JSON - no backticks, no "json" label, no explanations.

{rules_info}

### Schema Information:
{schema_info}

### Input:
Generate a CanvasXpress JSON configuration for:
- **Description**: '{canvasxpress_config_english}'
- **Headers/Column Names**: '{headers_column_names}'

### Reference Examples:
Below are similar examples showing English descriptions and their corresponding CanvasXpress JSON configurations:
{few_shot_examples}

### Response:
