# Phase 2: Core GPX Processing Prompts

## Step 4: GPX Parser

```text
Implement GPX parsing functionality in cli/gpx_art/parsers.py:

1. Create GPXParser class with methods:
   - __init__(self, filepath: str)
   - parse(self) -> gpxpy.gpx.GPX | None
   - is_valid(self) -> bool
   - get_error(self) -> str | None

2. Implement parse method:
   - Open file with error handling
   - Use gpxpy.parse() to read file
   - Store any exceptions as error message
   - Return parsed GPX object or None

3. Add validation logic:
   - Check file exists
   - Check file extension is .gpx
   - Attempt to parse file
   - Catch and store parsing errors

4. Create simple test in tests/test_parsers.py:
   - Test with valid GPX file (create fixture)
   - Test with non-existent file
   - Test with invalid GPX content
   - Test error messages are clear

Example usage:
parser = GPXParser("route.gpx")
gpx = parser.parse()
if gpx is None:
    print(parser.get_error())
```

## Step 5: Data Models

```text
Create data models for internal route representation in cli/gpx_art/models.py:

1. Create RoutePoint dataclass:
   - latitude: float
   - longitude: float  
   - elevation: float | None
   - timestamp: datetime | None

2. Create RouteSegment dataclass:
   - points: list[RoutePoint]
   - name: str | None
   - calculate_distance(self) -> float
   - calculate_duration(self) -> timedelta | None

3. Create Route dataclass:
   - segments: list[RouteSegment]
   - name: str | None
   - metadata: dict
   - get_total_distance(self) -> float
   - get_total_duration(self) -> timedelta | None
   - get_bounds(self) -> tuple[float, float, float, float]  # min_lat, max_lat, min_lon, max_lon

4. Update parser to convert gpxpy objects to internal models:
   - Add method to GPXParser: to_route(gpx: gpxpy.gpx.GPX) -> Route

5. Create tests for data models:
   - Test point creation and attributes
   - Test segment distance calculation
   - Test route bounds calculation
   - Test conversion from gpxpy to internal models
```

## Step 6: GPX Info Command

```text
Implement the `info` command in cli/gpx_art/main.py:

1. Update info command signature:
   @cli.command()
   @click.argument('input_file', type=click.Path(exists=True))
   def info(input_file):
       """Display GPX file information."""

2. Implement info command logic:
   - Parse GPX file using GPXParser
   - Convert to Route model
   - Display formatted information:
     * File name
     * Route name (if available)
     * Total distance (miles and km)
     * Total duration (if available)
     * Number of segments
     * Number of points
     * Elevation gain/loss (if available)
     * Bounds (lat/lon range)

3. Add error handling:
   - Check for parsing errors
   - Display helpful error messages
   - Exit with appropriate error code

4. Create tests for info command:
   - Test with valid GPX file
   - Test with invalid file
   - Verify output format
   - Test error conditions

Success criteria:
- `gpx-art info route.gpx` displays comprehensive route information
- Error messages are clear and helpful
```

## Step 7: GPX Validation

```text
Implement the `validate` command in cli/gpx_art/main.py:

1. Update validate command signature:
   @cli.command()
   @click.argument('input_file', type=click.Path(exists=True))
   def validate(input_file):
       """Validate GPX file."""

2. Implement validation logic:
   - Parse GPX file using GPXParser
   - Check for common issues:
     * Missing required elements
     * Empty segments
     * Invalid coordinates (lat/lon range)
     * Duplicate timestamps
     * Malformed data
   
3. Display validation results:
   - Show success message for valid files
   - List all issues found in invalid files
   - Use colored output (click.style()) for better visibility
   - Exit with appropriate status code (0 for valid, 1 for invalid)

4. Create validation helper functions:
   - validate_coordinates(route: Route) -> list[str]
   - validate_segments(route: Route) -> list[str]
   - validate_timestamps(route: Route) -> list[str]

5. Create tests for validate command:
   - Test with valid GPX file
   - Test with various invalid files
   - Test error detection
   - Verify exit codes

Success criteria:
- `gpx-art validate route.gpx` correctly identifies valid/invalid files
- Validation errors are specific and actionable
```