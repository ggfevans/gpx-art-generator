# Phase 4: Visual Enhancements Prompts

## Step 11: Styling Options

```text
Expand styling options in cli/gpx_art/visualizer.py:

1. Add line style support to RouteVisualizer:
   - Add line_style parameter to render_route method
   - Support 'solid' and 'dashed' styles
   - Implement style mapping:
     style_map = {
         'solid': '-',
         'dashed': '--'
     }

2. Update the rendering method:
   - Apply line style to matplotlib plot
   - Combine with color and thickness
   - Ensure proper rendering for different combinations

3. Update convert command to accept line style:
   @click.option('--style', type=click.Choice(['solid', 'dashed']), default='solid')

4. Create tests:
   - Test solid vs dashed rendering
   - Test all style combinations
   - Visual regression if possible

5. Add style validation:
   - Ensure valid color hex codes
   - Validate all options before rendering

Success criteria:
- Can render routes with different line styles
- All styling options work together
- Visual output matches expectations
```

## Step 12: Export Formats

```text
Add SVG and PDF export capabilities in cli/gpx_art/exporters.py:

1. Expand Exporter class with new methods:
   - export_svg(self, figure: matplotlib.figure.Figure, output_path: str)
   - export_pdf(self, figure: matplotlib.figure.Figure, output_path: str, width: float, height: float)

2. Implement SVG export:
   - Use matplotlib's SVG backend
   - Ensure proper scaling
   - Maintain vector quality

3. Implement PDF export:
   - Use reportlab for better control
   - Convert matplotlib figure to PDF
   - Set proper page dimensions
   - Handle multiple page sizes

4. Update convert command:
   - Support multiple formats via --format option
   - Allow comma-separated formats: --format=png,svg,pdf
   - Generate all requested formats

5. Add format detection:
   - Detect format from output file extension
   - Override with --format option if provided

6. Create tests:
   - Test each export format individually
   - Test multiple format generation
   - Verify file creation and validity

Success criteria:
- `gpx-art convert route.gpx output.svg` creates SVG
- Multiple formats can be generated simultaneously
- All formats maintain proper quality
```

## Step 13: Distance Markers

```text
Implement distance markers in cli/gpx_art/visualizer.py:

1. Add marker functionality to RouteVisualizer:
   - Add add_distance_markers method
   - Support miles and kilometers
   - Calculate marker positions along route

2. Implement marker calculation:
   - Calculate distance along route using haversine
   - Place markers at regular intervals
   - Find closest points to desired distances

3. Render markers:
   - Add marker symbols (small circles or ticks)
   - Position markers correctly on route
   - Add optional distance labels

4. Update convert command:
   @click.option('--markers/--no-markers', default=True)
   @click.option('--markers-unit', type=click.Choice(['miles', 'km']), default='miles')

5. Add marker styling options:
   - Marker size
   - Marker color
   - Label font size
   - Label positioning

6. Create tests:
   - Test marker placement accuracy
   - Test unit conversion
   - Test marker rendering

Success criteria:
- Markers appear at correct distances
- Both miles and kilometers work properly
- Markers enhance rather than clutter the artwork
```

## Step 14: Information Overlay

```text
Implement information overlay in cli/gpx_art/visualizer.py:

1. Add overlay functionality to RouteVisualizer:
   - Add add_overlay method
   - Support multiple information fields
   - Position overlay on artwork

2. Implement overlay fields:
   - Distance (total)
   - Duration (if available)
   - Elevation gain/loss (if available)
   - Date (if available)
   - Event name (from route metadata)

3. Create OverlayFormatter class:
   - Format different data types consistently
   - Handle missing data gracefully
   - Create clean text layout

4. Add positioning logic:
   - Support 4 corner positions
   - Calculate proper padding
   - Avoid overlap with route

5. Update convert command:
   @click.option('--overlay', help='Comma-separated fields: distance,duration,elevation,date,name')
   @click.option('--position', type=click.Choice(['top-left', 'top-right', 'bottom-left', 'bottom-right']), default='top-left')

6. Add styling options:
   - Font family
   - Font size
   - Text color
   - Background box option

7. Create tests:
   - Test all overlay fields
   - Test positioning
   - Test formatting
   - Test with missing data

Success criteria:
- Overlay displays requested information clearly
- Positioning works correctly
- Text is readable against route background
```