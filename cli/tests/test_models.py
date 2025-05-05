"""
Tests for the route data models.
"""

import math
import pytest
from datetime import datetime, timedelta

from gpx_art.models import Route, RoutePoint, RouteSegment, haversine_distance


class TestHaversineDistance:
    """Tests for the haversine_distance function."""

    def test_same_point(self):
        """Distance between the same point should be zero."""
        assert haversine_distance(45.0, -122.0, 45.0, -122.0) == 0.0
    
    def test_known_distance(self):
        """Test against a known distance calculation."""
        # San Francisco to Los Angeles, ~550-560km
        sf_lat, sf_lon = 37.7749, -122.4194
        la_lat, la_lon = 34.0522, -118.2437
        
        distance = haversine_distance(sf_lat, sf_lon, la_lat, la_lon)
        assert 550000 < distance < 560000  # ~550-560 km


class TestRoutePoint:
    """Tests for the RoutePoint class."""
    
    def test_create_valid_point(self):
        """Test creating a point with valid coordinates."""
        point = RoutePoint(latitude=37.7749, longitude=-122.4194)
        assert point.latitude == 37.7749
        assert point.longitude == -122.4194
        assert point.elevation is None
        assert point.timestamp is None
    
    def test_create_with_optional_fields(self):
        """Test creating a point with optional fields."""
        now = datetime.now()
        point = RoutePoint(
            latitude=37.7749, 
            longitude=-122.4194,
            elevation=100.5,
            timestamp=now
        )
        assert point.latitude == 37.7749
        assert point.longitude == -122.4194
        assert point.elevation == 100.5
        assert point.timestamp == now
    
    def test_invalid_latitude(self):
        """Test that invalid latitude raises ValueError."""
        with pytest.raises(ValueError):
            RoutePoint(latitude=91.0, longitude=0.0)
        
        with pytest.raises(ValueError):
            RoutePoint(latitude=-91.0, longitude=0.0)
    
    def test_invalid_longitude(self):
        """Test that invalid longitude raises ValueError."""
        with pytest.raises(ValueError):
            RoutePoint(latitude=0.0, longitude=181.0)
        
        with pytest.raises(ValueError):
            RoutePoint(latitude=0.0, longitude=-181.0)
    
    def test_boundary_values(self):
        """Test boundary values for coordinates."""
        # These should be valid
        RoutePoint(latitude=90.0, longitude=180.0)
        RoutePoint(latitude=-90.0, longitude=-180.0)
        RoutePoint(latitude=0.0, longitude=0.0)


class TestRouteSegment:
    """Tests for the RouteSegment class."""
    
    @pytest.fixture
    def empty_segment(self):
        """Fixture for an empty segment."""
        return RouteSegment()
    
    @pytest.fixture
    def single_point_segment(self):
        """Fixture for a segment with a single point."""
        return RouteSegment(points=[
            RoutePoint(latitude=37.7749, longitude=-122.4194)
        ])
    
    @pytest.fixture
    def multi_point_segment(self):
        """Fixture for a segment with multiple points."""
        return RouteSegment(points=[
            RoutePoint(latitude=37.7749, longitude=-122.4194),
            RoutePoint(latitude=37.7750, longitude=-122.4195),
            RoutePoint(latitude=37.7751, longitude=-122.4196)
        ])
    
    @pytest.fixture
    def timed_segment(self):
        """Fixture for a segment with timestamps."""
        base_time = datetime(2023, 1, 1, 12, 0, 0)
        return RouteSegment(points=[
            RoutePoint(latitude=37.7749, longitude=-122.4194, timestamp=base_time),
            RoutePoint(latitude=37.7750, longitude=-122.4195, 
                      timestamp=base_time + timedelta(minutes=5)),
            RoutePoint(latitude=37.7751, longitude=-122.4196, 
                      timestamp=base_time + timedelta(minutes=10))
        ])
    
    @pytest.fixture
    def partial_timed_segment(self):
        """Fixture for a segment with some missing timestamps."""
        base_time = datetime(2023, 1, 1, 12, 0, 0)
        return RouteSegment(points=[
            RoutePoint(latitude=37.7749, longitude=-122.4194, timestamp=base_time),
            RoutePoint(latitude=37.7750, longitude=-122.4195, timestamp=None),
            RoutePoint(latitude=37.7751, longitude=-122.4196, 
                      timestamp=base_time + timedelta(minutes=10))
        ])
    
    def test_empty_segment_distance(self, empty_segment):
        """Test that an empty segment has zero distance."""
        assert empty_segment.calculate_distance() == 0.0
    
    def test_single_point_segment_distance(self, single_point_segment):
        """Test that a segment with a single point has zero distance."""
        assert single_point_segment.calculate_distance() == 0.0
    
    def test_multi_point_segment_distance(self, multi_point_segment):
        """Test distance calculation for a segment with multiple points."""
        distance = multi_point_segment.calculate_distance()
        # Since points are very close, distance should be small but non-zero
        assert distance > 0.0
        assert distance < 100.0  # Should be less than 100 meters
    
    def test_empty_segment_duration(self, empty_segment):
        """Test that an empty segment has None duration."""
        assert empty_segment.calculate_duration() is None
    
    def test_single_point_segment_duration(self, single_point_segment):
        """Test that a segment with a single point has None duration."""
        assert single_point_segment.calculate_duration() is None
    
    def test_timed_segment_duration(self, timed_segment):
        """Test duration calculation for a segment with timestamps."""
        duration = timed_segment.calculate_duration()
        assert duration is not None
        assert duration == timedelta(minutes=10)
    
    def test_partial_timed_segment_duration(self, partial_timed_segment):
        """Test duration calculation when some timestamps are missing."""
        duration = partial_timed_segment.calculate_duration()
        assert duration is not None
        assert duration == timedelta(minutes=10)


class TestRoute:
    """Tests for the Route class."""
    
    @pytest.fixture
    def empty_route(self):
        """Fixture for an empty route."""
        return Route()
    
    @pytest.fixture
    def single_segment_route(self):
        """Fixture for a route with a single segment."""
        segment = RouteSegment(points=[
            RoutePoint(latitude=37.7749, longitude=-122.4194),
            RoutePoint(latitude=37.7750, longitude=-122.4195)
        ])
        return Route(segments=[segment])
    
    @pytest.fixture
    def multi_segment_route(self):
        """Fixture for a route with multiple segments."""
        segment1 = RouteSegment(points=[
            RoutePoint(latitude=37.7749, longitude=-122.4194),
            RoutePoint(latitude=37.7750, longitude=-122.4195)
        ])
        segment2 = RouteSegment(points=[
            RoutePoint(latitude=37.8000, longitude=-122.5000),
            RoutePoint(latitude=37.8001, longitude=-122.5001)
        ])
        return Route(segments=[segment1, segment2])
    
    @pytest.fixture
    def timed_route(self):
        """Fixture for a route with timestamps."""
        base_time = datetime(2023, 1, 1, 12, 0, 0)
        segment1 = RouteSegment(points=[
            RoutePoint(latitude=37.7749, longitude=-122.4194, timestamp=base_time),
            RoutePoint(latitude=37.7750, longitude=-122.4195, 
                      timestamp=base_time + timedelta(minutes=5))
        ])
        segment2 = RouteSegment(points=[
            RoutePoint(latitude=37.8000, longitude=-122.5000, 
                      timestamp=base_time + timedelta(minutes=10)),
            RoutePoint(latitude=37.8001, longitude=-122.5001, 
                      timestamp=base_time + timedelta(minutes=15))
        ])
        return Route(segments=[segment1, segment2])
    
    @pytest.fixture
    def elevation_route(self):
        """Fixture for a route with elevation data."""
        segment = RouteSegment(points=[
            RoutePoint(latitude=37.7749, longitude=-122.4194, elevation=100.0),
            RoutePoint(latitude=37.7750, longitude=-122.4195, elevation=110.0),
            RoutePoint(latitude=37.7751, longitude=-122.4196, elevation=105.0)
        ])
        return Route(segments=[segment])
    
    def test_empty_route_distance(self, empty_route):
        """Test that an empty route has zero distance."""
        assert empty_route.get_total_distance() == 0.0
    
    def test_single_segment_route_distance(self, single_segment_route):
        """Test distance calculation for a route with a single segment."""
        distance = single_segment_route.get_total_distance()
        assert distance > 0.0
    
    def test_multi_segment_route_distance(self, multi_segment_route):
        """Test distance calculation for a route with multiple segments."""
        distance = multi_segment_route.get_total_distance()
        assert distance > 0.0
        
        # Should be sum of segment distances
        segment_sum = sum(seg.calculate_distance() 
                         for seg in multi_segment_route.segments)
        assert distance == segment_sum
    
    def test_empty_route_duration(self, empty_route):
        """Test that an empty route has None duration."""
        assert empty_route.get_total_duration() is None
    
    def test_timed_route_duration(self, timed_route):
        """Test duration calculation for a route with timestamps."""
        duration = timed_route.get_total_duration()
        assert duration is not None
        assert duration == timedelta(minutes=15)  # Total time span
    
    def test_empty_route_bounds(self, empty_route):
        """Test that an empty route has default bounds."""
        bounds = empty_route.get_bounds()
        assert bounds == (0.0, 0.0, 0.0, 0.0)
    
    def test_route_bounds(self, multi_segment_route):
        """Test bounds calculation for a route."""
        min_lat, max_lat, min_lon, max_lon = multi_segment_route.get_bounds()
        assert min_lat == 37.7749
        assert max_lat == 37.8001
        assert min_lon == -122.5001
        assert max_lon == -122.4194
    
    def test_empty_route_elevation_stats(self, empty_route):
        """Test that an empty route has None elevation stats."""
        assert empty_route.get_elevation_stats() is None
    
    def test_route_elevation_stats(self, elevation_route):
        """Test elevation stats calculation for a route."""
        stats = elevation_route.get_elevation_stats()
        assert stats is not None
        assert stats['min'] == 100.0
        assert stats['max'] == 110.0
        assert stats['gain'] == 10.0  # From 100 to 110
        assert stats['loss'] == 5.0   # From 110 to 105
    
    def test_route_total_points(self, multi_segment_route):
        """Test total points calculation for a route."""
        assert multi_segment_route.get_total_points() == 4

