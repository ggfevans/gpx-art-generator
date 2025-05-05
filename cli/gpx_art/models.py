"""
Data models for GPX route representation.

This module contains dataclasses for representing GPS routes including points,
segments, and complete routes, with methods for calculating metrics.
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth.
    
    Uses the haversine formula to calculate the distance in meters.
    
    Args:
        lat1: Latitude of the first point in degrees
        lon1: Longitude of the first point in degrees
        lat2: Latitude of the second point in degrees
        lon2: Longitude of the second point in degrees
        
    Returns:
        Distance between the points in meters
    """
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth radius in meters
    earth_radius = 6371000
    
    # Calculate the distance
    distance = earth_radius * c
    return distance


@dataclass
class RoutePoint:
    """A single point in a GPS route with coordinates and optional metadata."""
    
    latitude: float
    longitude: float
    elevation: Optional[float] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate coordinates after initialization."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {self.longitude}")


@dataclass
class RouteSegment:
    """
    A segment of a GPS route consisting of an ordered series of points.
    
    A segment typically represents a continuous track or part of a track.
    """
    
    points: List[RoutePoint] = field(default_factory=list)
    name: Optional[str] = None
    
    def calculate_distance(self) -> float:
        """
        Calculate the total distance of the segment in meters.
        
        Returns:
            Total distance in meters, 0 if the segment has less than 2 points
        """
        if len(self.points) < 2:
            return 0.0
            
        total_distance = 0.0
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            total_distance += haversine_distance(
                p1.latitude, p1.longitude, p2.latitude, p2.longitude
            )
            
        return total_distance
    
    def calculate_duration(self) -> Optional[timedelta]:
        """
        Calculate the duration of the segment based on timestamps.
        
        Returns:
            Duration as timedelta if timestamps are available, None otherwise
        """
        # Check if we have timestamps on at least the first and last points
        if (len(self.points) < 2 or 
            self.points[0].timestamp is None or 
            self.points[-1].timestamp is None):
            return None
            
        # Find the first and last points with valid timestamps
        first_ts = None
        last_ts = None
        
        for point in self.points:
            if point.timestamp is not None:
                if first_ts is None:
                    first_ts = point.timestamp
                last_ts = point.timestamp
                
        if first_ts is None or last_ts is None:
            return None
            
        return last_ts - first_ts


@dataclass
class Route:
    """
    A complete GPS route consisting of one or more segments.
    
    A route represents a full GPS track with metadata.
    """
    
    segments: List[RouteSegment] = field(default_factory=list)
    name: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def get_total_distance(self) -> float:
        """
        Get the total distance of all segments in meters.
        
        Returns:
            Total distance in meters
        """
        return sum(segment.calculate_distance() for segment in self.segments)
    
    def get_total_duration(self) -> Optional[timedelta]:
        """
        Get the total duration of the route.
        
        This is calculated as the difference between the timestamp of the first point
        and the timestamp of the last point across all segments.
        
        Returns:
            Total duration as timedelta if timestamps are available, None otherwise
        """
        first_timestamp = None
        last_timestamp = None
        
        for segment in self.segments:
            for point in segment.points:
                if point.timestamp is not None:
                    if first_timestamp is None or point.timestamp < first_timestamp:
                        first_timestamp = point.timestamp
                    if last_timestamp is None or point.timestamp > last_timestamp:
                        last_timestamp = point.timestamp
        
        if first_timestamp is None or last_timestamp is None:
            return None
            
        return last_timestamp - first_timestamp
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """
        Get the geographical bounds of the route.
        
        Returns:
            Tuple of (min_lat, max_lat, min_lon, max_lon)
            If the route has no points, returns (0, 0, 0, 0)
        """
        min_lat = min_lon = float('inf')
        max_lat = max_lon = float('-inf')
        has_points = False
        
        for segment in self.segments:
            for point in segment.points:
                has_points = True
                min_lat = min(min_lat, point.latitude)
                max_lat = max(max_lat, point.latitude)
                min_lon = min(min_lon, point.longitude)
                max_lon = max(max_lon, point.longitude)
        
        if not has_points:
            return (0.0, 0.0, 0.0, 0.0)
            
        return (min_lat, max_lat, min_lon, max_lon)
    
    def get_elevation_stats(self) -> Optional[Dict[str, float]]:
        """
        Calculate elevation statistics for the route.
        
        Returns:
            Dictionary with elevation stats (min, max, gain, loss)
            Returns None if no elevation data is available
        """
        elevations = []
        
        for segment in self.segments:
            for point in segment.points:
                if point.elevation is not None:
                    elevations.append(point.elevation)
        
        if not elevations:
            return None
            
        # Calculate elevation gain and loss
        gain = 0.0
        loss = 0.0
        
        for i in range(1, len(elevations)):
            diff = elevations[i] - elevations[i-1]
            if diff > 0:
                gain += diff
            else:
                loss -= diff
                
        return {
            'min': min(elevations),
            'max': max(elevations),
            'gain': gain,
            'loss': loss
        }
    
    def get_total_points(self) -> int:
        """
        Get the total number of points in the route.
        
        Returns:
            Total number of points across all segments
        """
        return sum(len(segment.points) for segment in self.segments)

