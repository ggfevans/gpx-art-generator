"""
Tests for the route visualization functionality.
"""

import math
import pytest
import matplotlib
import numpy as np
from datetime import datetime

# Use non-interactive backend for testing
matplotlib.use('Agg')

from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from route_to_art.models import Route, RoutePoint, RouteSegment
from route_to_art.visualizer import RouteVisualizer, mercator_projection


# Test route fixtures

@pytest.fixture
def empty_route():
    """Fixture for an empty route."""
    return Route()


@pytest.fixture
def simple_route():
    """Fixture for a simple route with one segment and two points."""
    segment = RouteSegment(points=[
        RoutePoint(latitude=37.7749, longitude=-122.4194),
        RoutePoint(latitude=37.7750, longitude=-122.4195)
    ])
    return Route(segments=[segment], name="Simple Route")


@pytest.fixture
def complex_route():
    """Fixture for a more complex route with multiple segments."""
    segment1 = RouteSegment(points=[
        RoutePoint(latitude=37.7749, longitude=-122.4194),
        RoutePoint(latitude=37.7750, longitude=-122.4195),
        RoutePoint(latitude=37.7751, longitude=-122.4196)
    ])
    segment2 = RouteSegment(points=[
        RoutePoint(latitude=37.7760, longitude=-122.4200),
        RoutePoint(latitude=37.7765, longitude=-122.4205)
    ])
    return Route(segments=[segment1, segment2], name="Complex Route")


@pytest.fixture
def single_point_route():
    """Fixture for a route with a single point segment."""
    segment = RouteSegment(points=[
        RoutePoint(latitude=37.7749, longitude=-122.4194)
    ])
    return Route(segments=[segment], name="Single Point Route")


# Test the mercator projection function

def test_mercator_projection():
    """Test the mercator projection function."""
    # Test known values
    lat, lon = 0.0, 0.0
    x, y = mercator_projection(lat, lon)
    assert x == 0.0
    assert y == 0.0
    
    # Test that higher latitudes result in higher y values
    x1, y1 = mercator_projection(10.0, 0.0)
    x2, y2 = mercator_projection(20.0, 0.0)
    assert y2 > y1
    
    # Test that eastern longitudes result in higher x values
    x1, y1 = mercator_projection(0.0, 10.0)
    x2, y2 = mercator_projection(0.0, 20.0)
    assert x2 > x1
    
    # Test that the function handles extreme but valid values
    mercator_projection(85.0, 180.0)
    mercator_projection(-85.0, -180.0)


# Test the RouteVisualizer class

def test_create_figure_default(simple_route):
    """Test creating a figure with default parameters."""
    visualizer = RouteVisualizer(simple_route)
    figure = visualizer.create_figure()
    
    assert isinstance(figure, Figure)
    assert figure.get_figwidth() == 9.0
    assert figure.get_figheight() == 6.0
    assert figure.get_dpi() == 300


def test_create_figure_custom_dimensions(simple_route):
    """Test creating a figure with custom dimensions."""
    visualizer = RouteVisualizer(simple_route)
    width, height, dpi = 12.0, 8.0, 150
    figure = visualizer.create_figure(width=width, height=height, dpi=dpi)
    
    assert isinstance(figure, Figure)
    assert figure.get_figwidth() == width
    assert figure.get_figheight() == height
    assert figure.get_dpi() == dpi


def test_render_route_default(simple_route):
    """Test rendering a route with default parameters."""
    visualizer = RouteVisualizer(simple_route)
    visualizer.create_figure()
    visualizer.render_route()
    
    figure = visualizer.get_figure()
    assert figure is not None
    
    # Check that we have at least one line in the plot
    ax = figure.axes[0]
    lines = ax.get_lines()
    assert len(lines) > 0
    
    # Check default line properties
    line = lines[0]
    assert line.get_color() == '#000000'  # Default color
    assert line.get_linewidth() == 1.0  # Default thickness (medium)


def test_render_route_custom(simple_route):
    """Test rendering a route with custom parameters."""
    visualizer = RouteVisualizer(simple_route)
    visualizer.create_figure()
    visualizer.render_route(color='#FF0000', thickness='thick')
    
    figure = visualizer.get_figure()
    assert figure is not None
    
    # Check line properties
    ax = figure.axes[0]
    line = ax.get_lines()[0]
    assert line.get_color() == '#FF0000'
    assert line.get_linewidth() == 2.0  # thick


def test_render_complex_route(complex_route):
    """Test rendering a route with multiple segments."""
    visualizer = RouteVisualizer(complex_route)
    visualizer.create_figure()
    visualizer.render_route()
    
    figure = visualizer.get_figure()
    assert figure is not None
    
    # We should have at least two lines (one per segment)
    ax = figure.axes[0]
    lines = ax.get_lines()
    assert len(lines) >= 2


def test_render_empty_route(empty_route):
    """Test rendering an empty route."""
    visualizer = RouteVisualizer(empty_route)
    visualizer.create_figure()
    visualizer.render_route()
    
    figure = visualizer.get_figure()
    assert figure is not None
    
    # Should have no lines
    ax = figure.axes[0]
    lines = ax.get_lines()
    assert len(lines) == 0


def test_render_single_point_route(single_point_route):
    """Test rendering a route with a single point."""
    visualizer = RouteVisualizer(single_point_route)
    visualizer.create_figure()
    visualizer.render_route()
    
    figure = visualizer.get_figure()
    assert figure is not None
    
    # Single points don't create lines in matplotlib's plot
    ax = figure.axes[0]
    lines = ax.get_lines()
    assert len(lines) == 0


def test_figure_properties(simple_route):
    """Test that figure has the expected properties."""
    visualizer = RouteVisualizer(simple_route)
    visualizer.create_figure()
    visualizer.render_route()
    
    figure = visualizer.get_figure()
    assert figure is not None
    
    # Check that axes are off
    ax = figure.axes[0]
    assert not ax.get_xaxis().get_visible()
    assert not ax.get_yaxis().get_visible()
    
    # Check aspect ratio is equal
    assert ax.get_aspect() == 'equal'


def test_get_projected_coordinates(simple_route):
    """Test the internal method for getting projected coordinates."""
    visualizer = RouteVisualizer(simple_route)
    segment = simple_route.segments[0]
    
    x_coords, y_coords = visualizer._get_projected_coordinates(segment)
    
    # Should have same number of coordinates as points
    assert len(x_coords) == len(segment.points)
    assert len(y_coords) == len(segment.points)
    
    # Manually calculate projected coordinates for comparison
    expected_x = []
    expected_y = []
    for point in segment.points:
        x, y = mercator_projection(point.latitude, point.longitude)
        expected_x.append(x)
        expected_y.append(y)
    
    # Check coordinates match
    for i in range(len(x_coords)):
        assert x_coords[i] == pytest.approx(expected_x[i])
        assert y_coords[i] == pytest.approx(expected_y[i])


def test_render_auto_creates_figure(simple_route):
    """Test that render_route creates a figure if none exists."""
    visualizer = RouteVisualizer(simple_route)
    # Don't call create_figure explicitly
    visualizer.render_route()
    
    figure = visualizer.get_figure()
    assert figure is not None
    assert isinstance(figure, Figure)


# Tests for OverlayFormatter

def test_overlay_formatter_distance():
    """Test distance formatting in OverlayFormatter."""
    from route_to_art.visualizer import OverlayFormatter
    
    # Test with zero
    assert "0.0 km (0.0 miles)" in OverlayFormatter.format_distance(0)
    
    # Test with positive value
    distance_m = 5000  # 5 km
    formatted = OverlayFormatter.format_distance(distance_m)
    assert "5.0 km" in formatted
    assert "3.1 miles" in formatted


def test_overlay_formatter_duration():
    """Test duration formatting in OverlayFormatter."""
    from route_to_art.visualizer import OverlayFormatter
    from datetime import timedelta
    
    # Test with None
    assert "Unknown" in OverlayFormatter.format_duration(None)
    
    # Test with zero
    assert "0m" in OverlayFormatter.format_duration(timedelta(seconds=0))
    
    # Test with complex duration
    duration = timedelta(days=1, hours=2, minutes=30, seconds=15)
    formatted = OverlayFormatter.format_duration(duration)
    assert "1d" in formatted
    assert "2h" in formatted
    assert "30m" in formatted
    
    # Test with just seconds
    seconds_only = timedelta(seconds=45)
    assert "45s" in OverlayFormatter.format_duration(seconds_only)


def test_overlay_formatter_elevation():
    """Test elevation formatting in OverlayFormatter."""
    from route_to_art.visualizer import OverlayFormatter
    
    # Test with None
    assert "No elevation data" in OverlayFormatter.format_elevation(None)
    
    # Test with stats
    stats = {
        'min': 100.0,
        'max': 500.0,
        'gain': 450.0,
        'loss': 50.0
    }
    formatted = OverlayFormatter.format_elevation(stats)
    assert "100" in formatted
    assert "500" in formatted
    assert "450m" in formatted
    assert "50m" in formatted


def test_overlay_formatter_name():
    """Test name formatting in OverlayFormatter."""
    from route_to_art.visualizer import OverlayFormatter
    
    # Test with None
    assert "Unnamed route" in OverlayFormatter.format_name(None)
    
    # Test with empty string
    assert "Unnamed route" in OverlayFormatter.format_name("")
    
    # Test with short name
    assert "Test Route" == OverlayFormatter.format_name("Test Route")
    
    # Test with very long name (should be truncated)
    long_name = "This is an extremely long route name that should be truncated in the formatting process"
    formatted = OverlayFormatter.format_name(long_name)
    assert "..." in formatted
    assert len(formatted) < len(long_name)


def test_overlay_formatter_date():
    """Test date formatting in OverlayFormatter."""
    from route_to_art.visualizer import OverlayFormatter
    from datetime import datetime
    
    # Test with None
    assert "No date" in OverlayFormatter.format_date(None)
    
    # Test with date
    date = datetime(2023, 5, 15, 12, 30, 45)
    formatted = OverlayFormatter.format_date(date)
    assert "2023-05-15" in formatted


# Tests for overlay functionality

def test_add_overlay_basic(simple_route):
    """Test adding basic overlay to figure."""
    from route_to_art.visualizer import OverlayField
    
    visualizer = RouteVisualizer(simple_route)
    visualizer.create_figure()
    visualizer.render_route()
    
    # Add basic overlay
    visualizer.add_overlay(fields=[OverlayField.DISTANCE, OverlayField.NAME])
    
    # Check that text was added (can't easily check content)
    ax = visualizer.get_figure().axes[0]
    texts = ax.texts
    assert len(texts) > 0


def test_add_overlay_with_string_fields(simple_route):
    """Test adding overlay with string field names."""
    visualizer = RouteVisualizer(simple_route)
    visualizer.create_figure()
    visualizer.render_route()
    
    # Add overlay with string fields
    visualizer.add_overlay(fields=["distance", "name"])
    
    # Check that text was added
    ax = visualizer.get_figure().axes[0]
    texts = ax.texts
    assert len(texts) > 0


def test_add_overlay_positions(simple_route):
    """Test different overlay positions."""
    from route_to_art.visualizer import OverlayPosition
    
    visualizer = RouteVisualizer(simple_route)
    visualizer.create_figure()
    visualizer.render_route()
    
    # Test each position
    positions = [
        OverlayPosition.TOP_LEFT,
        OverlayPosition.TOP_RIGHT,
        OverlayPosition.BOTTOM_LEFT,
        OverlayPosition.BOTTOM_RIGHT
    ]
    
    for position in positions:
        # Create new figure for each test
        visualizer.create_figure()
        visualizer.render_route()
        
        # Add overlay with this position
        visualizer.add_overlay(
            fields=["distance"],
            position=position
        )
        
        # Check that text was added
        ax = visualizer.get_figure().axes[0]
        texts = ax.texts
        assert len(texts) > 0
        
        # Could check text alignment but that's implementation-specific


def test_overlay_position_from_string():
    """Test converting string position to enum."""
    from route_to_art.visualizer import OverlayPosition
    
    # Test valid positions
    assert OverlayPosition.from_string("top-left") == OverlayPosition.TOP_LEFT
    assert OverlayPosition.from_string("top_left") == OverlayPosition.TOP_LEFT
    assert OverlayPosition.from_string("TOP-LEFT") == OverlayPosition.TOP_LEFT
    
    # Test invalid position
    with pytest.raises(ValueError):
        OverlayPosition.from_string("invalid-position")


def test_overlay_field_from_string():
    """Test converting string field to enum."""
    from route_to_art.visualizer import OverlayField
    
    # Test valid fields
    assert OverlayField.from_string("distance") == OverlayField.DISTANCE
    assert OverlayField.from_string("DISTANCE") == OverlayField.DISTANCE
    
    # Test invalid field
    with pytest.raises(ValueError):
        OverlayField.from_string("invalid-field")


def test_add_overlay_styling(simple_route):
    """Test overlay styling options."""
    visualizer = RouteVisualizer(simple_route)
    visualizer.create_figure()
    visualizer.render_route()
    
    # Add overlay with custom styling
    visualizer.add_overlay(
        fields=["distance"],
        font_size=12,
        font_color="red",
        background=True,
        bg_color="yellow",
        bg_alpha=0.5
    )
    
    # Check that text was added with properties
    ax = visualizer.get_figure().axes[0]
    text = ax.texts[0]
    
    assert text.get_fontsize() == 12
    assert text.get_color() == "red"
    assert text.get_bbox() is not None  # Has background
    assert text.get_bbox().get_facecolor()[0:3] == (1.0, 1.0, 0.0)  # yellow
    assert text.get_bbox().get_alpha() == 0.5


def test_add_overlay_no_background(simple_route):
    """Test overlay without background."""
    visualizer = RouteVisualizer(simple_route)
    visualizer.create_figure()
    visualizer.render_route()
    
    # Add overlay without background
    visualizer.add_overlay(
        fields=["distance"],
        background=False
    )
    
    # Check text properties
    ax = visualizer.get_figure().axes[0]
    text = ax.texts[0]
    
    # Should have no background or an invisible one
    bbox = text.get_bbox()
    if bbox is not None:
        # If bbox exists, it should be invisible
        assert bbox.get_alpha() == 0 or bbox.get_facecolor()[3] == 0


def test_add_overlay_errors(simple_route):
    """Test error conditions for add_overlay."""
    visualizer = RouteVisualizer(simple_route)
    
    # Should fail without a figure
    with pytest.raises(ValueError):
        visualizer.add_overlay(fields=["distance"])
        
    # Create figure for remaining tests
    visualizer.create_figure()
    
    # Should fail with invalid field
    with pytest.raises(ValueError):
        visualizer.add_overlay(fields=["invalid-field"])
        
    # Should fail with invalid position
    with pytest.raises(ValueError):
        visualizer.add_overlay(fields=["distance"], position="invalid-position")


def test_thickness_map():
    """Test the thickness map values."""
    assert RouteVisualizer.thickness_map['thin'] == 0.5
    assert RouteVisualizer.thickness_map['medium'] == 1.0
    assert RouteVisualizer.thickness_map['thick'] == 2.0


def test_style_map():
    """Test the style map values."""
    assert RouteVisualizer.style_map['solid'] == '-'
    assert RouteVisualizer.style_map['dashed'] == '--'


def test_unit_factors():
    """Test the unit conversion factors."""
    assert RouteVisualizer._UNIT_FACTORS['km'] == 0.001
    assert RouteVisualizer._UNIT_FACTORS['miles'] == 0.000621371


# Tests for style validation

def test_validate_color_valid_hex(simple_route):
    """Test that valid hex colors are accepted."""
    visualizer = RouteVisualizer(simple_route)
    
    # Standard 6-digit hex
    assert visualizer._validate_color('#000000') == '#000000'
    assert visualizer._validate_color('#FFFFFF') == '#FFFFFF'
    assert visualizer._validate_color('#ff00ff') == '#ff00ff'
    
    # Shorthand 3-digit hex
    assert visualizer._validate_color('#000') == '#000'
    assert visualizer._validate_color('#FFF') == '#FFF'
    assert visualizer._validate_color('#f0f') == '#f0f'


def test_validate_color_invalid_hex(simple_route):
    """Test that invalid hex colors are rejected."""
    visualizer = RouteVisualizer(simple_route)
    
    with pytest.raises(ValueError) as exc_info:
        visualizer._validate_color('#12345')  # Wrong length
    assert "Invalid hex color code" in str(exc_info.value)
    
    with pytest.raises(ValueError) as exc_info:
        visualizer._validate_color('#GHIJKL')  # Invalid characters
    assert "Invalid hex color code" in str(exc_info.value)
    
    with pytest.raises(ValueError) as exc_info:
        visualizer._validate_color('##000000')  # Double #
    assert "Invalid hex color code" in str(exc_info.value)


def test_validate_color_named_colors(simple_route):
    """Test that named colors pass validation."""
    visualizer = RouteVisualizer(simple_route)
    
    # Named colors should pass validation
    assert visualizer._validate_color('red') == 'red'
    assert visualizer._validate_color('blue') == 'blue'
    assert visualizer._validate_color('green') == 'green'


def test_validate_thickness_valid(simple_route):
    """Test that valid thickness values are accepted."""
    visualizer = RouteVisualizer(simple_route)
    
    assert visualizer._validate_thickness('thin') == 0.5
    assert visualizer._validate_thickness('medium') == 1.0
    assert visualizer._validate_thickness('thick') == 2.0


def test_validate_thickness_invalid(simple_route):
    """Test that invalid thickness values are rejected."""
    visualizer = RouteVisualizer(simple_route)
    
    with pytest.raises(ValueError) as exc_info:
        visualizer._validate_thickness('super-thick')
    assert "Invalid thickness" in str(exc_info.value)
    assert "Valid options are" in str(exc_info.value)
    assert "thin" in str(exc_info.value)
    assert "medium" in str(exc_info.value)
    assert "thick" in str(exc_info.value)


def test_validate_line_style_valid(simple_route):
    """Test that valid line style values are accepted."""
    visualizer = RouteVisualizer(simple_route)
    
    assert visualizer._validate_line_style('solid') == '-'
    assert visualizer._validate_line_style('dashed') == '--'


def test_validate_line_style_invalid(simple_route):
    """Test that invalid line style values are rejected."""
    visualizer = RouteVisualizer(simple_route)
    
    with pytest.raises(ValueError) as exc_info:
        visualizer._validate_line_style('dotted')
    assert "Invalid line style" in str(exc_info.value)
    assert "Valid options are" in str(exc_info.value)
    assert "solid" in str(exc_info.value)
    assert "dashed" in str(exc_info.value)


# Tests for line style rendering

def test_render_route_solid_style(simple_route):
    """Test rendering a route with solid line style."""
    visualizer = RouteVisualizer(simple_route)
    visualizer.create_figure()
    visualizer.render_route(line_style='solid')
    
    figure = visualizer.get_figure()
    assert figure is not None
    
    # Get the first line and check its style
    ax = figure.axes[0]
    line = ax.get_lines()[0]
    assert line.get_linestyle() == '-'


def test_render_route_dashed_style(simple_route):
    """Test rendering a route with dashed line style."""
    visualizer = RouteVisualizer(simple_route)
    visualizer.create_figure()
    visualizer.render_route(line_style='dashed')
    
    figure = visualizer.get_figure()
    assert figure is not None
    
    # Get the first line and check its style
    ax = figure.axes[0]
    line = ax.get_lines()[0]
    assert line.get_linestyle() == '--'


def test_combined_styling(simple_route):
    """Test all styling options together."""
    visualizer = RouteVisualizer(simple_route)
    visualizer.create_figure()
    visualizer.render_route(
        color='#FF0000',
        thickness='thick',
        line_style='dashed'
    )
    
    figure = visualizer.get_figure()
    assert figure is not None
    
    # Get the first line and check all style properties
    ax = figure.axes[0]
    line = ax.get_lines()[0]
    assert line.get_color() == '#FF0000'
    assert line.get_linewidth() == 2.0  # thick
    assert line.get_linestyle() == '--'  # dashed

