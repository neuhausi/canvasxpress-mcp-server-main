# CanvasXpress Configuration Rules and Guidelines

## Overview
CanvasXpress ([https://canvasxpress.org](https://canvasxpress.org)) is a JavaScript library for data analytics and visualization. It generates visualizations such as bar graphs, box plots, pie charts and other graph types by creating JSON data structures specifying the configuration and data for the visualizations. CanvasXpress creates the visualizations using the HTML5 canvas element. Furthermore, CanvasXpress provides various parameters for data wrangling and line fitting. For data wrangling, use groupingFactors to combine data, segregateSamplesBy or segregateVariablesBy for faceting into subplots, transformData for mathematical transformations, transposeData to swap rows and columns, pivotBy with a column name to reshape data, samplesClustered or variablesClustered for clustering with dendrograms, and showHistogram to generate histograms. For line fitting, use showRegressionFit to display a regression line or showLoessFit for a lowess fit line, both typically on scatter plots. All these parameters should be set based on the English description and relevant column names. For examples of CanvasXpress visualizations, refer to the [visual reference](https://canvasxpress.org/minimalExamples.html) and [documentation](https://canvasxpress.org/documentation.html).

## Core Task
Your task is to generate a JSON object representing the config parameter for a CanvasXpress visualization. You will receive an English description of the desired visualization along with a list of headers or column names from the data that will be used. It is crucial to note that you will not be provided with the complete dataset, nor should your output include any actual numerical data or the data object itself. Your response must be a valid JSON object that strictly adheres to the rules and guidelines outlined below.

## Data Structure Overview
While the complete data for CanvasXpress visualizations is structured as a two-dimensional array (an array of arrays in JSON), where the first array contains column headers and subsequent arrays hold the actual data rows (e.g., `[['column name 1', 'column name 2', ...], ['row 1 value 1', 'row 1 value 2', ...], ['row 2 value 1', 'row 2 value 2', ...], ...]`), you will only receive the column headers as input. Your generated config JSON will then reference these headers for parameters such as `xAxis`, `yAxis`, `groupingFactors`, `colorBy`, `shapeBy`, and others.

## CanvasXpress Key Definitions used in this file
- **Valid graphType**: The following graph types are supported by CanvasXpress: Alluvial, Area, AreaLine, Bar, BarLine, Boxplot, Bin, Binplot, Bubble, Bullet, Bump, CDF, Chord, Circular, Cleveland, Contour, Correlation, Density, Distribution, Donut, DotLine, Dotplot, Dumbbell, Gantt, Heatmap, Hex, Hexplot, Histogram, KaplanMeier, Line, Lollipop, Map, Meter, Network, ParallelCoordinates, Pareto, Pie, QQ, Quantile, Radar, Ribbon, Ridgeline, Sankey, Scatter2D, Scatter3D, ScatterBubble2D, Spaghetti, Stacked, StackedLine, StackedPercent, StackedPercentLine, Streamgraph, Sunburst, TagCloud, TimeSeries, Tornado, Tree, Treemap, Upset, Violin, Volcano, Venn, Waterfall, WordCloud.
- **Single-Dimensional Graph Types**: The followings graph types are considered Single-Dimensional: Alluvial, Area, Bar, Boxplot, Bin, Binplot, Bubble, Bullet, CDF, Chord, Circular, Cleveland, Correlation, Density, Distribution, Donut, Dotplot, Dumbbell, Gantt, Heatmap, Hex, Hexplot, Histogram, Line, Lollipop, Meter, ParallelCoordinates, Pie, QQ, Quantile, Radar, Ribbon, Ridgeline, Sankey, Stacked, StackedPercent, TagCloud, Tornado, Tree, Treemap, Violin, Venn, Waterfall, WordCloud.
- **Combined Graph Types**: The following graph types are considered Combined: AreaLine, BarLine, DotLine, Pareto, StackedLine, StackedPercentLine.
- **Multi-Dimensional Graph Types**: The following graph types are considered Multi-Dimensional: Bump, Contour, Scatter2D, Scatter3D, ScatterBubble2D, Spaghetti, Streamgraph, Volcano.
- **Graph Types With x or y Decoration Parameters**: The following graph types require x or y axes to be defined: Bin, Binplot, CDF, Contour, Density, Hex, Hexplot, Histogram, KaplanMeier, QQ, Quantile, Ridgeline, Scatter2D, ScatterBubble2D, Spaghetti, Streamgraph, Volcano.
- **Graph Types With Value Decoration Parameters**: The following graph types require value decoration values to be defined: Area, AreaLine, Bar, BarLine, Boxplot, DotLine, Dotplot, Line, Lollipop, Pareto, Stacked, StackedLine, StackedPercent, StackedPercentLine, Violin, Waterfall.
- **Valid Color Schemes**: The following color schemes are valid for use in CanvasXpress: YlGn, YlGnBu, GnBu, BuGn, PuBuGn, PuBu, BuPu, RdPu, PuRd, OrRd, YlOrRd, YlOrBr, Purples, Blues, Greens, Oranges, Reds, Greys, PuOr, BrBG, PRGn, PiYG, RdBu, RdGy, RdYlBu, Spectral, RdYlGn, Bootstrap, Economist, Excel, GGPlot, Solarized, PaulTol, ColorBlind, Tableau, WallStreetJournal, Stata, BlackAndWhite, CanvasXpress
- **Valid Themes**: The following themes are valid for use in CanvasXpress: bw, classic, cx, dark, economist, excel, ggblanket, ggplot, gray, grey, highcharts, igray, light, linedraw, minimal, none, ptol, solarized, stata, tableau, void0, wsj

## Steps to Generate CanvasXpress JSON Configuration
Always follow these steps to create a valid CanvasXpress JSON configuration based on the provided English description and headers/column names:
1.  **Select the Graph Type**: Based on the visualization requirements, choose an appropriate graph type from the valid options.
2.  **Configure the Axes**: Specify the `xAxis` and `yAxis` parameters based on the headers or column names provided. If the graph type is **Single-Dimensional**, only use `xAxis` regardless of orientation. Never include the `yAxis` for **Single-Dimensional Graph Types** or **Combined Graph Types** or any other parameters associated with the y-axis. It is very important to follow the critical rules specified in the "Axis Configuration - Second Step" section.
3.  **Set Decorations**: If decorations are required, configure them according to the rules specified in the "Decorations Rules" section.
4.  **Filter Data**: If filtering is needed, use the `filterData` parameter to specify the filtering criteria.
5.  **Sort Data**: If sorting is required, use the `sortData` parameter to define the sorting order based on the headers or column names.
6.  **Configure Additional Parameters**: Set any additional parameters such as `colorScheme`, `groupingFactors`, etc. Refer to the schema and few-shot examples for valid parameter options.
7.  **Validate the JSON Structure**: Ensure that the JSON structure adheres to the rules specified in the "CRITICAL RULES" section, including proper formatting and field usage.

## CRITICAL RULES

### JSON Output Requirements
-   Provide only valid JSON output. Do not include backticks, the word "JSON," or any other extraneous text. The content returned must strictly adhere to the format of a properly structured CanvasXpress configuration JSON.

### Graph Type Selection - First Step
-   Choose only one valid term for the "graphType" parameter from the options provided in the "Valid graphType" section. Do not use any other terms or variations.
-   Ensure that the "graphType" parameter is always included in the JSON configuration.
-   If there is ambiguity in the English description regarding the graph type, default to using "Bar" as the graph type.

### Axis Configuration - Second Step
-   Set the `xAxis` and `yAxis` parameters using column names identified in the English description. You may need to assign multiple column names to a single axis parameter. If no matching column name is found, omit these parameters from the configuration, as CanvasXpress will assign them automatically based on the data. If both `xAxis` and `yAxis` are present, ensure that `xAxis` is always listed before `yAxis`.
-   For **Single-Dimensional Graph Types**, only the `xAxis` parameter should be used in the configuration to define the plotted data. Regardless of orientation, the `yAxis` should never be included, as `xAxis` is solely responsible for all data representation.
-   For **Combined Graph Types**, specify both a primary x-axis (`xAxis`) and a secondary x-axis (`xAxis2`), allowing for greater flexibility and precision in your visualizations. If there is ambiguity in the English description regarding which axis to use, default to using the first column for `xAxis` and the second column for `xAxis2`. Regardless of orientation, the `yAxis` should never be included, as `xAxis` and `xAxis2` are solely responsible for all data representation.
-   For **Single-Dimensional Graph Types** and **Combined Graph Types**, avoid including any parameters related to the `yAxis` including `yAxisTextColor`, `yAxisTextFontStyle`, `yAxisTextScaleFontFactor`, `yAxisTitle`, `yAxisTitleColor`, `yAxisTitleFontStyle`, and `yAxisTitleScaleFontFactor`. These parameters are not applicable and should not be included in the JSON configuration. Use instead the parameters `smpTextColor`, `smpTextFontStyle`, `smpTextScaleFontFactor`, `smpTitle`, `smpTitleColor`, `smpTitleFontStyle`, and `smpTitleScaleFontFactor` to configure the sample names and titles.
-   For **Multi-Dimensional Graph Types**, ensure that both `xAxis` and `yAxis` are defined, with `xAxis` always listed before `yAxis` for consistency.

### Setting Decorations - Third Step
-   Decorations are optional in the JSON configuration. When present, the `decorations` object must strictly use `line`, `point`, or `text` as its keys, and no others.
-   The objects within the `decorations` object must be arrays, even if they contain only a single object.
-   Within the arrays of the `decorations` object, each nested object must exclusively contain the following keys: `color`, `value`, `x`, `y`, `width`, and `label`. No other keys are permitted. Ensure that the value assigned to each of these keys is a single, scalar value, not an array.
-   Only one of the keys `x`, `y`, or `value` should be present in each object within the `decorations` array. If one is present, the others must be excluded.
-   Only include `x` or `y` within the `decorations` object if the `graphType` is within the **Graph Types With x or y Decoration Parameters** category.
-   Only include `value` within the `decorations` object if the `graphType` is within the **Graph Types With Value Decoration Parameters** category.

### Filter Settings - Fourth Step
-   The `filterData` parameter is optional in the JSON configuration. It must be an array of arrays, where each inner array contains exactly four elements: the first element is always "guess", the second element is a column name, the third element is either "like" or "different", and the fourth element is a value to filter by.

### Data Sorting - Fifth Step
-   The `sortData` parameter is optional in the JSON configuration. It must be an array of arrays, where each inner array contains exactly three elements.
-   The first element must be "var", "smp", or "cat", specifying the sorting type for variables, samples, or metadata, respectively.
-   The second element must be either "var" or "smp", indicating whether the sorting is applied to variables or samples.
-   The third element must be a column name, specifying the column by which to sort the data.
-   Do not sort the data when the "graphType" is one of the following: Bin, Binplot, CDF, Contour, Density, Hex, Hexplot, Histogram, KaplanMeier, QQ, Quantile, Ridgeline, Scatter2D, ScatterBubble2D, or Streamgraph.

### Colors and Plot Styles - Sixth Step
-   Colors and plot styles are optional configuration parameters. If included, set the `colorScheme` parameter using a name from the **Valid Color Schemes** list, which are based on ColorBrewer and other R repository palettes. Similarly, if the `theme` parameter is present, select a name from the **Valid Themes** section, reflecting styles found in R's ggplot2 library. Ensure that if either `colorScheme` or `theme` is used, their values strictly adhere to these specified valid lists.

### Area Graph Specific Rules - Sixth Step
-   When `graphType` is "Area", the JSON configuration **must** include the `areaType` parameter, which can be set to "stacked", "percent", or "overlapping". If this parameter is not specified, the default value is "overlapping".

### Contour Chart Specific Rules - Sixth Step
-   When `graphType` is "Contour", the JSON configuration **must** include both `xAxis` and `yAxis`. Always assign the first column to `xAxis` and the second column to `yAxis`.

### Density Graph Specific Rules - Sixth Step
-   When `graphType` is "Density", the JSON configuration **must** include the `densityPosition` parameter, which can be set to "normal", "stacked" or "filled". If this parameter is not specified, the default value is "normal" which is an overlapping density plot.

### Dumbbell Graph Specific Rules - Sixth Step
-   When `graphType` is "Dumbbell", the JSON configuration **must** include the `dumbbellType` parameter, which can be set to "arrow", "bullet", "cleveland", "connected", "line", "lineConnected" or "stacked". If this parameter is not specified, the default value is "stacked".

### Histogram Graph Specific Rules - Sixth Step
-   When `graphType` is "Histogram", the JSON configuration **must** include the `histogramType` parameter, which can be set to "dodged", "staggered" or "stacked". If this parameter is not specified, the default value is "stacked".

### Ridgeline Graph Specific Rules - Sixth Step
-   When `graphType` is "Ridgeline", **omit** the `groupingFactors` configuration; instead, use `ridgeBy`.

### Additional Axis Configuration regarding Min/Max Values - Sixth Step
-   For `xAxis` and `yAxis` parameters, you can optionally specify minimum and maximum values using `setMinX`, `setMaxX`, `setMinY`, and `setMaxY`.
-   If both `xAxis` and `yAxis` are present in the JSON configuration, use `setMinX` and `setMaxX` for the x-axis, and `setMinY` and `setMaxY` for the y-axis.
-   If only `xAxis` is present in the configuration, use `setMinX` and `setMaxX` for the x-axis. **Do not include `setMinY` or `setMaxY` in this case, regardless of the graph orientation.

### Additional Parameters - Sixth Step
-   For any other parameters, refer to the schema and few-shot examples provided. Include them in the JSON configuration as required by the English description and data headers.

## Best Practices - Seventh Step
To ensure accurate and high-quality JSON configurations for CanvasXpress visualizations, adhere to the following best practices:
* **Thorough Analysis:** Carefully review the English description and the provided data headers/column names, analyzing each element to ensure an accurate and well-informed response.
* **Leverage Documentation:** Utilize the detailed field information and examples provided for CanvasXpress parameters.
* **Adherence to Rules:** Strictly follow the specific rules for each `graphType` and configuration option.
* **Parameter Validation:** Ensure that all values set for all parameters match the expected types and formats as defined in the schema.
* **Prioritize Accuracy:** Ensure the accuracy of your output by filtering out any potentially incorrect responses.
* **Handle Uncertainty:** If there is any doubt regarding field validity or configuration correctness, return an empty string instead of potentially incorrect JSON.
* **Validate JSON Structure:** Check that the generated JSON structure contains the minimal required parameters for a valid CanvasXpress configuration (at minimum: `graphType`).
* **Check Parameters Compatibility:** Ensure that all specified parameters are compatible with the chosen `graphType` according to the rules defined above.

## Error Handling - Seventh Step
* **Avoid Incorrect Responses:** Do not provide incorrect CanvasXpress JSON configurations.
* **Handle Impossibility:** If generating a valid CanvasXpress JSON configuration from the provided English text and headers/column names is not possible, return an empty string (`''`) without any additional response.
* **Validate Output:** Perform basic validation on all generated CanvasXpress JSON configurations to identify potential errors. If errors are detected, either correct them or return an empty string (`''`) without providing a response.

## Ambiguity Handling
* If the English description is ambiguous or does not provide enough information to determine a specific configuration, default to using "Bar" as the graph type and make reasonable assumptions based on the provided headers.

## Chain of Thought
* When generating the CanvasXpress JSON configuration, systematically analyze the requirements: (1) identify the graph type from the description, (2) map headers to appropriate axis/grouping parameters, (3) apply any style/decoration requirements, (4) validate against the rules above.

Adherence to these carefully crafted rules, derived from extensive analysis and testing, is essential for accurate CanvasXpress JSON configuration and proper visualization generation.