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

from gpx_art.models import Route, RoutePoint, RouteSegment
from gpx_art.visualizer import RouteVisualizer, mercator_projection


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


def test_thickness_map():
    """Test the thickness map values."""
    assert RouteVisualizer.thickness_map['thin'] == 0.5
    assert RouteVisualizer.thickness_map['medium'] == 1.0
    assert RouteVisualizer.thickness_map['thick'] == 2.0

