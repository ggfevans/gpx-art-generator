# Phase 3: Basic Visualization Prompts

## Step 8: Route Rendering

```text
Create basic route visualization in cli/gpx_art/visualizer.py:

1. Create RouteVisualizer class:
   - __init__(self, route: Route)
   - create_figure(self, width: float = 36, height: float = 12, dpi: int = 300)
   - render_route(self, color: str = '#000000', thickness: str = 'medium')
   - get_figure(self) -> matplotlib.figure.Figure

2. Implement rendering logic:
   - Create matplotlib figure with specified dimensions
   - Set up coordinate system (equal aspect ratio)
   - Convert lat/lon to appropriate projection
   - Draw route segments as lines
   - Remove axes for clean artwork
   - Set proper margins

3. Add thickness mapping:
   thickness_map = {
       'thin': 0.5,
       'medium': 1.0, 
       'thick': 2.0
   }

4. Add coordinate projection helper:
   - Use simple mercator projection for now
   - Consider route bounds for scaling

5. Create tests for visualizer:
   - Test figure creation
   - Test route rendering
   - Test coordinate transformations
   - Test thickness options

Success criteria:
- Can create matplotlib figure from Route object
- Route is rendered correctly as a line
- Coordinate system properly scaled
```

## Step 9: PNG Export

```text
Implement PNG export functionality in cli/gpx_art/exporters.py:

1. Create Exporter class:
   - __init__(self)
   - export_png(self, figure: matplotlib.figure.Figure, output_path: str, dpi: int = 300)

2. Implement PNG export:
   - Use matplotlib's savefig()
   - Set proper DPI
   - Ensure transparent background
   - Handle file write errors
   - Verify output file was created

3. Add validation:
   - Check output directory exists
   - Check write permissions
   - Verify file extension

4. Create tests for exporter:
   - Test successful PNG export
   - Test error handling
   - Test file creation
   - Test DPI setting

5. Update visualizer to work with exporter:
   - Add method to save directly to PNG
   - Handle the full workflow from route to file

Success criteria:
- PNG files are created with correct dimensions
- File has correct DPI metadata
- Error handling works properly
```

## Step 10: Basic Convert Command

```text
Implement minimal convert command in cli/gpx_art/main.py:

1. Update convert command signature:
   @cli.command()
   @click.argument('input_file', type=click.Path(exists=True))
   @click.argument('output_file', type=click.Path())
   @click.option('--color', default='#000000', help='Line color in hex format')
   @click.option('--thickness', type=click.Choice(['thin', 'medium', 'thick']), default='medium')
   def convert(input_file, output_file, color, thickness):
       """Convert GPX file to artwork."""

2. Implement convert workflow:
   - Parse GPX file
   - Convert to Route model
   - Create RouteVisualizer
   - Render route with options
   - Export to PNG
   - Display success message

3. Add error handling:
   - Validate output file extension (.png only for now)
   - Handle all possible errors with helpful messages
   - Clean up partial files on error

4. Create tests for convert command:
   - Test successful conversion
   - Test various options
   - Test error conditions
   - Verify output file

5. Add progress indication:
   - Use click.echo() for simple progress messages
   - "Parsing GPX file..."
   - "Rendering route..."
   - "Exporting PNG..."
   - "Conversion complete!"

Success criteria:
- `gpx-art convert input.gpx output.png` creates valid PNG file
- Options (color, thickness) work correctly
- Error messages are helpful
```