# CanvasXpress Schema for Most Common Configuration Parameters
The complete schema with all the configuration parameters used in CanvasXpress can be found in the [API documentation](https://canvasxpress.org/api/general.html)

## CanvasXpress Key Definitions used in this Schema Summary
This file contains the schema of the most common CanvasXpress configuration fields organized by section and then category. Each parameter field includes:

- **Description**: What the field controls
- **Type**: Data type (string, boolean, integer, float, array, object, color)
- **Options**: Valid values (where applicable)
- **Default**: Default value

## Graph Types Section

### Area Graphs
-  **areaType**: Description: "Types of area graphs when displaying multiple series. The options include overlapping which is the default, stacked, and percent area graphs" Type: "string" Options: ["overlapping", "stacked", "percent"] Default: "overlapping"

### Bar Graphs
-  **barZero**: Description: "Flag to force zero in bar graphs with positive values" Type: "boolean" Default: true

### Bin Plots
-  **binplotBinWidth**: Description: "Width in actual units for the histogram bin" Type: "array" Default: []
-  **binplotBins**: Description: "Approximate number of bins in a bin plot. It may vary considerably to the actual number used in the bin plot to ensure a pretty size for the intervals in the bin plot. ggplots default is 30" Type: "array" Default: []
-  **binplotShape**: Description: "Type for the shape to use in binplots" Type: "string" Options: ["rectangle", "hexagon", "oval"] Default: "hexagon"

### Boxplot Graphs
-  **boxplotConnect**: Description: "Flag to show data in boxplots connected" Type: "boolean" Default: false
-  **boxplotNotched**: Description: "Flag to notch boxplots" Type: "boolean" Default: false
-  **boxplotType**: Description: "Boxplot type" Type: "string" Options: ["boxWhiskers", "range"] Default: "boxWhiskers"
-  **boxplotWhiskersType**: Description: "Boxplot whiskers type" Type: "string" Options: ["single", "double", "none"] Default: "double"
-  **showBoxplotOriginalData**: Description: "Flag to show/hide the observed data point in boxplots. (Should be called showBoxplotDataPoints)" Type: "boolean" Default: false

### Bullet Graphs
-  **bulletTargetVarName**: Description: "Variable name to use to identify target in bullet graphs" Type: "string" Options: [false] Default: false

### Circular Graphs
-  **circularType**: Description: "Property to set the subtype of circular graph. If set to sunburst or bubble then smpOverlays can be used to build a hierarchy for the graph" Type: "string" Options: ["normal", "radar", "sunburst", "chord", "bubble"] Default: "normal"

### Contours
-  **contourFilled**: Description: "Flag to color the contour plot" Type: "boolean" Default: false
-  **showContourDataPoints**: Description: "Flag to show/hide the data points in contours" Type: "boolean" Default: false

### Density Plots
-  **densityPosition**: Description: "Histogram density position" Type: "string" Options: ["normal", "stacked", "filled"] Default: "normal"

### Dumbbell Graphs
-  **dumbbellType**: Description: "Style for the dumbbell plot" Type: "string" Options: ["arrow", "bullet", "cleveland", "connected", "line", "lineConnected", "stacked"] Default: "stacked"

### Histograms
-  **histogramType**: Description: "Type of histogram when multiple series are present" Type: "string" Options: ["dodged", "staggered", "stacked"] Default: "dodged"
-  **showFilledHistogramDensity**: Description: "Flag to show/hide the filled histogram density" Type: "boolean" Default: false
-  **showHistogram**: Description: "Flag or sample annotation to create histogram. If true is specified then the histogram will be done with all data" Type: "string" Default: ""
-  **showHistogramBars**: Description: "Flag to hide the histogram bars" Type: "boolean" Default: false
-  **showHistogramDensity**: Description: "Flag to show/hide the density kernel in histograms" Type: "boolean" Default: false
-  **showHistogramMedian**: Description: "Flag to show/hide the histogram median" Type: "boolean" Default: false
-  **showHistogramQuantiles**: Description: "Flag to show/hide the quantile 0.25 and 0.75 in density plots" Type: "boolean" Default: false

### Line Graphs
-  **lineErrorType**: Description: "Line error type in the line graphs. The line type must be spline for the area error type. " Type: "string" Options: ["bar", "area"] Default: "bar"
-  **lineType**: Description: "Type of line used to join the points in line graphs" Type: "string" Options: ["rect", "solid", "spline", "dotted", "dashed", "dotdash", "longdash", "twodash"] Default: "rect"

### Maps
-  **mapColor**: Description: "Color for the maps" Type: "color" Default: "#0ab0db"
-  **mapConfig**: Description: "Map config" Type: "object" Default: {}
-  **mapId**: Description: "Map Id for the map div in the DOM" Type: "string" Default: ""
-  **topoJSON**: Description: "TopoJSON map string" Type: "string" Default: ""
-  **useLeaflet**: Description: "Flag to use leaflet" Type: "boolean" Default: false

### Quantile Regression Plots
-  **showQuantileRegressionFit**: Description: "Flag to show/hide the Quantile Regression fit in Scatter2D plots" Type: "boolean" Default: false

### Sankey Diagrams
-  **sankeyAxes**: Description: "Axes to include in the alluvial plots. It must sample annotations of the string type in the x object" Type: "array" Default: []
-  **sankeyTextColor**: Description: "Color for the text in sankey diagram labels" Type: "color" Default: "rgb(0,0,0)"
-  **sankeyTextFontStyle**: Description: "Font style for the sankey diagram labels" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **sankeyTextScaleFontFactor**: Description: "Scaling factor used to increase or decrease the sankey diagram labels font size in the canvas" Type: "float" Default: 1
-  **sankeyTextShow**: Description: "Flag to show/hide the labels in the Sankey diagrams" Type: "boolean" Default: true
-  **sankeyTitleColor**: Description: "Color for the text in sankey diagram titles" Type: "color" Default: "rgb(0,0,0)"
-  **sankeyTitleFontStyle**: Description: "Font style for the sankey diagram titles" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **sankeyTitleScaleFontFactor**: Description: "Scaling factor used to increase or decrease the sankey diagram titles font size in the canvas" Type: "float" Default: 1
-  **sankeyTitleShow**: Description: "Flag to show/hide the titles in the Sankey diagrams" Type: "boolean" Default: true

### Violin Plots
-  **showBoxplotIfViolin**: Description: "Flag to show/hide the boxplots when violin plot are show. It does not affect anything unless violins are shown" Type: "boolean" Default: false
-  **showViolinBoxplot**: Description: "Flag to show/hide the violin plot in boxplots" Type: "boolean" Default: false
-  **showViolinQuantiles**: Description: "Flag to show/hide the quantile 0.25 and 0.75 in violin plots" Type: "boolean" Default: false
-  **violinScale**: Description: "Type for scaling violin plots" Type: "string" Options: ["area", "count", "width"] Default: "width"
-  **violinTrim**: Description: "Flag to trim violin plots" Type: "boolean" Default: true

## General Section

### Aspect Ratio, Space and Width
-  **dataPointSizeScaleFactor**: Description: "Factor used to adjust the size of the dataPointSize" Type: "float" Default: 1
-  **variableSpace**: Description: "Pixels between the data series in one-dimensional plots" Type: "integer" Default: 2
-  **widthFactor**: Description: "Factor to adjust the width of the graph elements in one-dimensional and three-dimensional plots. The greater the number, the wider the elements" Type: "integer" Default: 1

### Colors
-  **colorScheme**: Description: "Color schemes can be user defined which will take the colors in the color property or one provided in canvasXpress. The order of the colors will be used to sequentially select when a different color is needed in a particular visualization" Type: "string" Options: ["AAAS", "Accent", "BMS", "BMSBackground", "BMSBlue", "BMSBrown", "BMSGreen", "BMSPink", "BMSPrimary", "BMSSecondary", "BMSTertiary", "BMSTertiaryDark", "BMSTertiaryLight", "BMSWheat", "Basic", "Behance", "BehancePair", "BehanceQuartet", "BehanceTrio", "Black", "BlackAndWhite", "BlueGrey", "BlueRedGrey", "Blues", "BluesDark", "Bootstrap", "BrBG", "Brand", "Brooklyn99Dark", "Brooklyn99Regular", "BuGn", "BuPu", "CanvasXpress", "CanvasXpressOLD", "CanvasXpressTraditional", "Cividis", "ColorBlind", "ColorSpectrum", "Colorful", "ColorfulAlt", "Complementary", "Dark2", "Default", "Diverging", "DivergingAlt", "Economist", "EconomistBG", "Excel", "Excel2", "Excel3", "Favorite", "GGBlanket", "GGPlot", "GameOfThronesArryn", "GameOfThronesGreyjoy", "GameOfThronesLannister", "GameOfThronesManderly", "GameOfThronesMartell", "GameOfThronesStannis", "GameOfThronesStark", "GameOfThronesTargaryen", "GameOfThronesTully", "GameOfThronesTyrell", "GnBu", "GravityFalls", "Greens", "Grey", "GreyHC", "Greys", "Heat", "Highcharts", "Inferno", "JCO", "Jama", "KimPossible", "Lancet", "LastAirBenderAir", "LastAirBenderEarth", "LastAirBenderFire", "LastAirBenderWater", "Light", "Magma", "Matlab", "NEJM", "NPG", "OrRd", "Oranges", "PRGn", "Paired", "ParksAndRecreation", "Parula", "PaulTol", "PiYG", "Plasma", "Prism", "PrismPair", "PrismTrio", "PuBu", "PuBuGn", "PuOr", "PuRd", "Purples", "Rainbow", "RdBu", "RdGy", "RdPu", "RdYlBu", "RdYlGn", "Reds", "RickyAndMorty", "Simpsons", "Solarized", "SolarizedBase", "Spectral", "SpongeBob", "Stata", "Stata2", "Stata3", "StataMono", "Tableau", "TableauBlueRed", "TableauColorBlind", "TableauCyclic", "TableauGreenOrange", "TableauGrey", "TableauLight", "TableauMedium", "TableauPairSequential", "TableauPurpleGrey", "TableauTrafficLight", "TableauTripleDiverging", "Viridis", "ViridisInv", "WHO", "WallStreetJournal", "WallStreetJournal2", "WallStreetJournal3", "WallStreetJournalBlackGreen", "WallStreetJournalDemRep", "WallStreetJournalRedGreen", "White", "YlGn", "YlGnBu", "YlOrBr", "YlOrRd"] Default: "User"

### Foreground and Background
-  **background**: Description: "Color for the Specifies the default background color for elements in the canvas not covered in a more specific configuration property" Type: "color" Default: "rgb(255,255,255)"

### General
-  **graphType**: Description: "Specifies the type of graph to be rendered" Type: "string" Options: ["Alluvial", "Area", "AreaLine", "Bar", "BarLine", "Boxplot", "Bin", "Binplot", "Bubble", "Bullet", "Bump", "CDF", "Chord", "Circular", "Cleveland", "Contour", "Correlation", "Density", "Distribution", "Donut", "DotLine", "Dotplot", "Dumbbell", "Fish", "Gantt", "Genome", "Heatmap", "Hex", "Hexplot", "Histogram", "KaplanMeier", "Line", "Lollipop", "Map", "Meter", "Network", "ParallelCoordinates", "Pareto", "Pie", "QQ", "Quantile", "Radar", "Ribbon", "Ridgeline", "Sankey", "Scatter2D", "Scatter3D", "ScatterBubble2D", "Spaghetti", "Stacked", "StackedLine", "StackedPercent", "StackedPercentLine", "Streamgraph", "Sunburst", "TagCloud", "TimeSeries", "Tornado", "Tree", "Treemap", "Upset", "Violin", "Volcano", "Venn", "Waterfall", "WordCloud"] Default: "Bar"
-  **theme**: Description: "The style for the plot or theme will control all the non-data elements of the plot including titles, legends, axes, panel and plot background colors and other stylistic elements" Type: "string" Options: ["bw", "classic", "cx", "cxdark", "dark", "economist", "excel", "ggblanket", "ggplot", "gray", "grey", "highcharts", "igray", "light", "linedraw", "minimal", "none", "ptol", "solarized", "stata", "tableau", "void0", "wsj", "cx2"] Default: "none"

### General One Dimensional Graphs
-  **graphOrientation**: Description: "Specifies the orientation of one-dimensional graphs" Type: "string" Options: ["horizontal", "vertical"] Default: "horizontal"

### Plot View
-  **view**: Description: "Specify the initial view or display for the visualization" Type: "string" Options: ["canvas", "table", "layout"] Default: "canvas"

## Metadata Section

### Confidence Intervals
-  **showConfidenceIntervals**: Description: "Flag to show/hide the confidence intervals in the regression plots " Type: "boolean" Default: true

### Decorations
-  **decorations**: Description: "Enables visual annotations on your graph, with its structure depending on the graphType. For network graphs, it is an array of node property names; for one-dimensional graphs, it is an object with primary keys like line, range, point, text, marker, or error; and for scatter plots, it is an object with primary keys such as linear, exponential, logarithmic, power, polynomial, nonlinearfit, regression, normal, line, text, label, point, range, image, or polygon. In the latter two cases, the value for each primary key is an array of objects, where each object specifies the properties of a decoration, for example, for a one-dimensional line: {line: [{value: 5, color: "#ff0000", width: 2, label: "Threshold", align: "right"}]}, or for a scatter plot linear fit: {linear: [{x: 1, y: 2, x2: 3, y2: 4, color: "#ff0000", width: 2, label: "Threshold", align: "right"}]}" Type: "object or array" Default: false

### Loess
-  **showLoessFit**: Description: "Flag to show/hide the Flag to show the loess fit in Scatter plots" Type: "boolean" Default: false

### Overlays
-  **smpOverlays**: Description: "Sample metadata to overlay in one dimensional plots" Type: "array" Default: []
-  **varOverlays**: Description: "Variable metadata to overlay in heatmap plots" Type: "array" Default: []

### Regression
-  **regressionType**: Description: "Type of linear least-squares fitting methods for simple data analysis" Type: "string" Options: ["linear", "exponential", "logarithmic", "power", "polynomial"] Default: "linear"
-  **showRegressionFit**: Description: "Flag to show/hide the Flag to show the regression fit" Type: "boolean" Default: false

## Data Section

### Clustering
-  **samplesClustered**: Description: "Flag to cluster samples" Type: "boolean" Default: false
-  **samplesKmeaned**: Description: "Flag to k-mean samples" Type: "boolean" Default: false
-  **variablesClustered**: Description: "Flag to cluster variables" Type: "boolean" Default: false
-  **variablesKmeaned**: Description: "Flag to k-mean variables" Type: "boolean" Default: false

### Data
-  **groupingFactors**: Description: "An array that holds the group names used for grouping the data. It must be a category in the data.x object" Type: "array" Default: []

### Data Context
-  **stringSampleFactors**: Description: "Array containing sample factors. The numeric sample factors will be treated as strings. This parameter accomplishes the same as the function switchNumericToString for samples at load time. It can be used in conjunction with the parameter asSampleFactors. TO DO: write example" Type: "array" Default: []
-  **stringVariableFactors**: Description: "Array containing variable factors. The numeric variable factors will be treated as strings. This parameter accomplishes the same as the function switchNumericToString for variables at load time. It can be used in conjunction with the parameter asVariableFactors. TO DO: write example" Type: "array" Default: []

### Data Faceting
-  **segregateSamplesBy**: Description: "An array that holds the annotation(s) used to segregate the samples ala Facet way in R. It must be categories in the data.x object" Type: "array" Default: []
-  **segregateVariablesBy**: Description: "An array that holds the annotation(s) used to segregate the variables ala Facet way in R. It must be categories in the data.z object" Type: "array" Default: []
-  **splitSamplesBy**: Description: "Factor (in the x data object) used to split the samples ala split in complex heatmap" Type: "string" Default: ""
-  **splitVariablesBy**: Description: "Factor (in the z data object) used to separate the variables ala split in complex heatmap" Type: "string" Default: ""

### Data Filters
- **filterData**: Description: "Array of arrays with filtering functions. Each function takes four parameters. The fisrt parameter is the type of filter. This could either of: var, smp, series, meta, x, y, z, data, network or guess (if not known). The second parameter is the key that usually correspond to a sample or variable factor name in the x or z object of the data. The third parameter is the operator to use which is one of: >, >=, <, <=, between, exact, like or not like and the four parameter is an array with the value or values that are needed for the corresponding evaluation. Here are some examples: [ x, class, exact, [ A ] ], [ guess, dose, between, [ 0.5, 2 ] ]", Type: "array", Default: []

### Data Point Attributes
-  **colorBy**: Description: "Name of a variable annotation or a sample name or the string variable to color the variables" Type: "string" Options: [false, "variable"] Default: false
-  **pieBy**: Description: "Utility to create pie with a sample annotation" Type: "string" Options: [false] Default: false
-  **pivotBy**: Description: "Utility to pivot data with a sample annotation" Type: "string" Options: [false] Default: false
-  **ridgeBy**: Description: "Utility to create ridgelines in Scatter2D plots" Type: "string" Options: [false] Default: false
-  **shapeBy**: Description: "Name of a variable annotation or a sample name or the string variable to shape the variables. When shapeByData is specified shapeBy is used for the title in the legend" Type: "string" Options: [false, "variable"] Default: false
-  **sizeBy**: Description: "Name of a variable annotation or a sample name or the string variable to size the variables. When sizeByData is specified sizeBy is used for the title in the legend" Type: "string" Options: [false, "variable"] Default: false
-  **stackBy**: Description: "Name of a sample annotation to stack the samples of each variable in Bar graphs" Type: "string" Options: [false] Default: false

### Data Selection
-  **selectedDataPoints**: Description: "Variable / Sample names of data points (in the data object) to initially select" Type: "array" Default: []

### Data Sorting
-  **sortData**: Description: "Array of arrays with sorting functions. Each function takes three parameters. The first parameter must be either smp to identify the parameters are related to the samples, var to identify the parameters are related to the variables, or cat to identify a sample or variable category. The second parameter can be either smp to indicate to sort the sample indices or var to indicate to sort the variable indices. The third parameter is the value for the key referenced by the first parameter. A special case for this parameter could be samples or variables to indicate to sort by the names of the samples or variables respectively. Here are some examples to sort the samples in the data: [ [cat, smp, Factor1] ]   : Sort the samples by the sample category Factor1 [ [var, smp, Variable1] ] : Sort the samples by the value of the Variable1 [ [cat, smp, samples] ]   : Sort the samples by their name.  Important!!!! This parameter will clean the data and remove any variables not used in the dataset at load time" Type: "array" Default: []

### Data Transformation
-  **transformData**: Description: "Default transformation type for ALL the data. Data can also be transformed by axis (x,y,z) to give more flexibility. false, save, reset and undo are NOT real transformations. They are only used in the canvasXpress UIs to save the transformed data" Type: "string" Options: [false, "log2", "log10", "-log2", "-log10", "exp2", "exp10", "sqrt", "percentile", "zscore", "ratio2", "ratio10", "save", "reset", "undo"] Default: false

### Hierarchy
-  **hierarchy**: Description: "Hierarchy for trees and bubble graphs made up of sample annotations present the data x object" Type: "array" Default: []

### Plot Area
-  **binned**: Description: "Flag to bin the data points in dotplots and boxplots" Type: "boolean" Default: false
-  **jitter**: Description: "Flag to jitter the data points in dotplots, boxplots and scatter2D plots" Type: "boolean" Default: false
-  **objectBorderColor**: Description: "Color for the border of all objects in one dimensional graphs. It turns into the non-transparent fill color if set to false" Type: "color" Default: "rgba(0,0,0,0)"

## Legend Section

### Legends
-  **legendColumns**: Description: "Number of columns in legends" Type: "integer" Default: 1
-  **legendInside**: Description: "Flag to position the legend inside the graphs" Type: "boolean" Default: false
-  **legendPosition**: Description: "Position for the the legend" Type: "string" Options: ["topRight", "right", "bottomRight", "bottom", "bottomLeft", "left", "topLeft", "top"] Default: "right"
-  **showLegend**: Description: "Flag to show/hide the legend" Type: "boolean" Default: true

## Titles, Subtitles and Citations Section

### Titles and Subtitles
-  **subtitle**: Description: "Subtitle of the graph" Type: "string" Default: ""
-  **subtitleColor**: Description: "Color for the text in subtitle" Type: "color" Default: "rgb(0,0,0)"
-  **subtitleFontStyle**: Description: "Font style for the subtitle" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **subtitleScaleFontFactor**: Description: "Scaling factor used to increase or decrease the subtitle font size in the canvas" Type: "float" Default: 1
-  **title**: Description: "Title of the graph" Type: "string" Default: ""
-  **titleColor**: Description: "Color for the text in title" Type: "color" Default: "rgb(0,0,0)"
-  **titleFontStyle**: Description: "Font style for the title" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: "bold"
-  **titleScaleFontFactor**: Description: "Scaling factor used to increase or decrease the title font size in the canvas" Type: "float" Default: 1

### Citations or References
-  **citation**: Description: "A reference citation of the graph which is placed at the bottom right corner" Type: "string" Default: ""
-  **citationColor**: Description: "Color for the text in citations" Type: "color" Default: "rgb(0,0,0)"
-  **citationFontStyle**: Description: "Font style for the citations" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **citationScaleFontFactor**: Description: "Scaling factor used to increase or decrease the citations font size in the canvas" Type: "float" Default: 1

## Samples and Variables Section

### Samples
-  **highlightSmp**: Description: "Name of samples to highlight" Type: "array" Default: []
-  **showSampleNames**: Description: "Flag to show/hide the sample names" Type: "boolean" Default: true
-  **smpTextColor**: Description: "Color for the text in sample labels" Type: "color" Default: "rgb(77,77,77)"
-  **smpTextFontStyle**: Description: "Font style for the sample labels" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **smpTextRotate**: Description: "Rotation in degrees for the sample labels" Type: "integer" Default: 0
-  **smpTextScaleFontFactor**: Description: "Scaling factor used to increase or decrease the sample labels font size in the canvas" Type: "float" Default: 1
-  **smpTitle**: Description: "Title for the sample axis in one dimensional plots" Type: "string" Default: ""
-  **smpTitleColor**: Description: "Color for the text in sample title" Type: "color" Default: "rgb(0,0,0)"
-  **smpTitleFontStyle**: Description: "Font style for the sample title" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **smpTitleRotate**: Description: "Rotation in degrees for the sample title" Type: "integer" Default: 0
-  **smpTitleScaleFontFactor**: Description: "Scaling factor used to increase or decrease the sample title font size in the canvas" Type: "float" Default: 1

### Variables
-  **highlightVar**: Description: "Name of variables to highlight" Type: "array" Default: []
-  **showVariableNames**: Description: "Flag to show/hide the variable names" Type: "boolean" Default: true
-  **varTextColor**: Description: "Color for the text in variable text" Type: "color" Default: "rgb(77,77,77)"
-  **varTextFontStyle**: Description: "Font style for the variable text" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **varTextRotate**: Description: "Rotation in degrees for the variable labels" Type: "integer" Default: 0
-  **varTextScaleFontFactor**: Description: "Scaling factor used to increase or decrease the variable text font size in the canvas" Type: "float" Default: 1
-  **varTitle**: Description: "Title for the variables in hetamap plots" Type: "string" Default: ""
-  **varTitleColor**: Description: "Color for the text in variable title" Type: "color" Default: "rgb(0,0,0)"
-  **varTitleFontStyle**: Description: "Font style for the variable title" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **varTitleScaleFontFactor**: Description: "Scaling factor used to increase or decrease the variable title font size in the canvas" Type: "float" Default: 1

## Axes Section

### R-Axis
-  **rAxis**: Description: "Radial axis for circular plots. It must be the name of a variable. Only applicable to 2 Dimensional circular plots" Type: "string" Default: ""
-  **rAxisShow**: Description: "Flag to show/hide the R axis" Type: "boolean" Default: true
-  **rAxisTextColor**: Description: "Color for the text in axis text" Type: "color" Default: "rgb(0,0,0)"
-  **rAxisTextFontStyle**: Description: "Font style for the axis text" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **rAxisTextScaleFontFactor**: Description: "Scaling factor used to increase or decrease the axis text font size in the canvas" Type: "float" Default: 1
-  **rAxisTitle**: Description: "R axis title " Type: "string" Default: ""
-  **rAxisTitleColor**: Description: "Color for the text in axis title" Type: "color" Default: "rgb(0,0,0)"
-  **rAxisTitleFontStyle**: Description: "Font style for the axis title" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **rAxisTitleScaleFontFactor**: Description: "Scaling factor used to increase or decrease the axis title font size in the canvas" Type: "float" Default: 1
-  **rAxisTransform**: Description: "Type of transformation for values in R axis" Type: "string" Options: [false, "log2", "log10", "-log2", "-log10", "exp2", "exp10", "sqrt", "percentile"] Default: false
-  **setMaxR**: Description: "Set the maximum value for data in the R axis" Type: "float" Default: 0
-  **setMinR**: Description: "Set the minimum value for data in the R axis" Type: "float" Default: 0

### X-Axis
-  **setMaxX**: Description: "Set the maximum value for data in the X axis" Type: "float" Default: 0
-  **setMinX**: Description: "Set the minimum value for data in the X axis" Type: "float" Default: 0
-  **xAxis**: Description: "Name of the samples, groups or variables to be displayed in the X axis" Type: "array" Default: []
-  **xAxis2**: Description: "Name of the samples, groups or variables to be displayed in the second X axis" Type: "array" Default: []
-  **xAxis2Show**: Description: "Flag to show/hide the X axis on the top" Type: "boolean" Default: false
-  **xAxis2Title**: Description: "X axis2 title  on the top" Type: "string" Default: ""
-  **xAxisShow**: Description: "Flag to show/hide the X axis on the bottom" Type: "boolean" Default: true
-  **xAxisTextColor**: Description: "Color for the text in axis text" Type: "color" Default: "rgb(0,0,0)"
-  **xAxisTextScaleFontFactor**: Description: "Scaling factor used to increase or decrease the axis text font size in the canvas" Type: "float" Default: 1
-  **xAxisTitle**: Description: "X axis title  on the bottom" Type: "string" Default: ""
-  **xAxisTitleColor**: Description: "Color for the text in axis title" Type: "color" Default: "rgb(0,0,0)"
-  **xAxisTitleFontStyle**: Description: "Font style for the axis title" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **xAxisTitleScaleFontFactor**: Description: "Scaling factor used to increase or decrease the axis title font size in the canvas" Type: "float" Default: 1
-  **xAxisTransform**: Description: "Type of transformation for values in X axis" Type: "string" Options: [false, "log2", "log10", "-log2", "-log10", "exp2", "exp10", "sqrt", "percentile"] Default: false

### Y-Axis
-  **setMaxY**: Description: "Set the maximum value for data in the Y axis" Type: "float" Default: 0
-  **setMinY**: Description: "Set the minimum value for data in the Y axis" Type: "float" Default: 0
-  **yAxis**: Description: "Name of the samples, groups or variables to be displayed in the Y axis" Type: "array" Default: []
-  **yAxisShow**: Description: "Flag to show/hide the Y axis on the left" Type: "boolean" Default: true
-  **yAxisTextColor**: Description: "Color for the text in axis text" Type: "color" Default: "rgb(0,0,0)"
-  **yAxisTextFontStyle**: Description: "Font style for the axis text" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **yAxisTextScaleFontFactor**: Description: "Scaling factor used to increase or decrease the axis text font size in the canvas" Type: "float" Default: 1
-  **yAxisTitle**: Description: "Y axis title  on the left" Type: "string" Default: ""
-  **yAxisTitleColor**: Description: "Color for the text in axis title" Type: "color" Default: "rgb(0,0,0)"
-  **yAxisTitleFontStyle**: Description: "Font style for the axis title" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **yAxisTitleScaleFontFactor**: Description: "Scaling factor used to increase or decrease the axis title font size in the canvas" Type: "float" Default: 1
-  **yAxisTransform**: Description: "Type of transformation for values in Y axis" Type: "string" Options: [false, "log2", "log10", "-log2", "-log10", "exp2", "exp10", "sqrt", "percentile"] Default: false

### Z-Axis
-  **setMaxZ**: Description: "Set the maximum value for data in the Z axis" Type: "float" Default: 0
-  **setMinZ**: Description: "Set the minimum value for data in the Z axis" Type: "float" Default: 0
-  **zAxis**: Description: "Name of the samples, groups or variables to be displayed in the Z axis" Type: "array" Default: []
-  **zAxisShow**: Description: "Flag to show/hide the Z axis" Type: "boolean" Default: true
-  **zAxisTextColor**: Description: "Color for the text in axis text" Type: "color" Default: "rgb(0,0,0)"
-  **zAxisTextFontStyle**: Description: "Font style for the axis text" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **zAxisTextScaleFontFactor**: Description: "Scaling factor used to increase or decrease the axis text font size in the canvas" Type: "float" Default: 1
-  **zAxisTitle**: Description: "Z axis title " Type: "string" Default: ""
-  **zAxisTitleColor**: Description: "Color for the text in axis title" Type: "color" Default: "rgb(0,0,0)"
-  **zAxisTitleFontStyle**: Description: "Font style for the axis title" Type: "string" Options: ["", "bold", "italic", "bold italic"] Default: false
-  **zAxisTitleScaleFontFactor**: Description: "Scaling factor used to increase or decrease the axis title font size in the canvas" Type: "float" Default: 1
-  **zAxisTransform**: Description: "Type of transformation for values in Z axis" Type: "string" Options: [false, "log2", "log10", "-log2", "-log10", "exp2", "exp10", "sqrt", "percentile"] Default: false

The schema covers the most common aspects of CanvasXpress visualization configuration from basic graph types to advanced features like clustering, filtering, and specialized plot types.