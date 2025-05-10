"""
GPX parsing functionality for the gpx-art tool.
Provides classes for loading and validating GPX files.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import gpxpy
import gpxpy.gpx

from gpx_art.models import Route, RoutePoint, RouteSegment


class GPXParser:
    """Parser for GPX files with validation capabilities."""

    def __init__(self, filepath: str):
        """
        Initialize the GPX parser with a file path.

        Args:
            filepath: Path to the GPX file to parse
        """
        self.filepath = filepath
        self._error: Optional[str] = None
        self._gpx: Optional[gpxpy.gpx.GPX] = None
        self._parsed = False

    def parse(self) -> Optional[gpxpy.gpx.GPX]:
        """
        Parse the GPX file and return the parsed object.

        Returns:
            GPX object if parsing was successful, None otherwise
        """
        # Reset state
        self._error = None
        self._gpx = None
        self._parsed = True

        # Check if file exists
        if not os.path.exists(self.filepath):
            self._error = f"File not found: {self.filepath}"
            return None

        # Check file extension
        if not self.filepath.lower().endswith('.gpx'):
            self._error = f"File is not a GPX file: {self.filepath}"
            return None

        # Try to parse the file
        try:
            with open(self.filepath, 'r') as gpx_file:
                self._gpx = gpxpy.parse(gpx_file)
                return self._gpx
        except Exception as e:
            self._error = f"Error parsing GPX file: {str(e)}"
            return None

    def is_valid(self) -> bool:
        """
        Check if the GPX file is valid.

        Returns:
            True if the file is a valid GPX file, False otherwise
        """
        # If we haven't parsed the file yet, do so now
        if not self._parsed:
            self.parse()

        # If there's an error or no GPX object, the file is invalid
        return self._error is None and self._gpx is not None

    def get_error(self) -> Optional[str]:
        """
        Get the error message if parsing failed.

        Returns:
            Error message string if there was an error, None otherwise
        """
        # If we haven't parsed the file yet, do so now
        if not self._parsed:
            self.parse()

        return self._error
        
    @staticmethod
    def _convert_point(gpx_point) -> RoutePoint:
        """
        Convert a gpxpy point to a RoutePoint.
        
        Args:
            gpx_point: A gpxpy point object (TrackPoint, RoutePoint, or Waypoint)
            
        Returns:
            A RoutePoint object with data from the gpxpy point
        """
        return RoutePoint(
            latitude=gpx_point.latitude,
            longitude=gpx_point.longitude,
            elevation=gpx_point.elevation,
            timestamp=gpx_point.time
        )
    
    @classmethod
    def _convert_segment(cls, gpx_segment) -> RouteSegment:
        """
        Convert a gpxpy segment to a RouteSegment.
        
        Args:
            gpx_segment: A gpxpy segment object
            
        Returns:
            A RouteSegment object with data from the gpxpy segment
        """
        points = [cls._convert_point(p) for p in gpx_segment.points]
        return RouteSegment(points=points)
    
    @classmethod
    def _extract_metadata(cls, gpx: gpxpy.gpx.GPX) -> Dict:
        """
        Extract metadata from a gpxpy GPX object.
        
        Args:
            gpx: A gpxpy GPX object
            
        Returns:
            A dictionary containing metadata from the GPX object
        """
        metadata = {}
        
        if gpx.name:
            metadata['name'] = gpx.name
            
        if gpx.description:
            metadata['description'] = gpx.description
            
        if gpx.author_name:
            metadata['author'] = gpx.author_name
            
        if gpx.time:
            metadata['time'] = gpx.time
            
        # Extract any other relevant metadata
        if gpx.keywords:
            metadata['keywords'] = gpx.keywords
            
        # Extract bounds if available
        if gpx.bounds:
            metadata['bounds'] = {
                'min_latitude': gpx.bounds.min_latitude,
                'max_latitude': gpx.bounds.max_latitude,
                'min_longitude': gpx.bounds.min_longitude,
                'max_longitude': gpx.bounds.max_longitude
            }
            
        return metadata
    
    @classmethod
    def to_route(cls, gpx: gpxpy.gpx.GPX) -> Route:
        """
        Convert a gpxpy GPX object to our internal Route model.
        
        Args:
            gpx: A gpxpy GPX object
            
        Returns:
            A Route object containing all data from the GPX object
        """
        segments = []
        route_name = None
        
        # Process tracks (most common in GPX files)
        for track in gpx.tracks:
            # Use the first track name as the route name if available
            if track.name and not route_name:
                route_name = track.name
                
            for gpx_segment in track.segments:
                segment = cls._convert_segment(gpx_segment)
                # Set segment name from track if available
                if track.name:
                    segment.name = track.name
                segments.append(segment)
        
        # Process routes (less common but still supported)
        for route in gpx.routes:
            # Create points from route points
            points = [cls._convert_point(p) for p in route.points]
            
            if points:
                segment = RouteSegment(points=points, name=route.name)
                segments.append(segment)
                
                # Use first route name as route name if no track name was found
                if route.name and not route_name:
                    route_name = route.name
        
        # Process waypoints (convert to single-point segments if present)
        if gpx.waypoints:
            waypoint_segment = RouteSegment(
                points=[cls._convert_point(p) for p in gpx.waypoints],
                name="Waypoints"
            )
            segments.append(waypoint_segment)
        
        # Extract metadata
        metadata = cls._extract_metadata(gpx)
        
        # Create the route object
        return Route(segments=segments, name=route_name, metadata=metadata)

