"""
Visualization functionality for GPX routes.

This module provides classes and functions for rendering GPX routes
as visual artwork using matplotlib.
"""

import math
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from gpx_art.models import Route, RouteSegment


def mercator_projection(lat: float, lon: float) -> Tuple[float, float]:
    """
    Convert latitude and longitude to Mercator projection coordinates.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        
    Returns:
        Tuple of (x, y) coordinates in Mercator projection
    """
    # Convert to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    # Simple Mercator projection
    x = lon_rad
    y = math.log(math.tan(math.pi/4 + lat_rad/2))
    
    return x, y


class RouteVisualizer:
    """
    Visualizes Route objects as artwork using matplotlib.
    """
    
    # Thickness mapping for line widths
    thickness_map = {
        'thin': 0.5,
        'medium': 1.0,
        'thick': 2.0
    }
    
    def __init__(self, route: Route):
        """
        Initialize the visualizer with a route.
        
        Args:
            route: The Route object to visualize
        """
        self.route = route
        self._figure: Optional[Figure] = None
        self._ax = None
        
    def create_figure(self, width: float = 9, height: float = 6, dpi: int = 300) -> Figure:
        """
        Create a matplotlib figure with specified dimensions.
        
        Args:
            width: Width of the figure in inches
            height: Height of the figure in inches
            dpi: Dots per inch resolution
            
        Returns:
            A matplotlib Figure object
        """
        # Create figure and axes
        self._figure = plt.figure(figsize=(width, height), dpi=dpi)
        self._ax = self._figure.add_subplot(111)
        
        # Set up clean visualization
        self._ax.set_aspect('equal')  # Equal aspect ratio
        self._ax.axis('off')  # Hide axes
        
        # Set tight layout
        self._figure.tight_layout(pad=0)
        
        return self._figure
    
    def _get_projected_coordinates(self, segment: RouteSegment) -> Tuple[List[float], List[float]]:
        """
        Convert route segment coordinates to projected coordinates.
        
        Args:
            segment: The RouteSegment to project
            
        Returns:
            Tuple of (x_coords, y_coords) lists in projected coordinates
        """
        x_coords = []
        y_coords = []
        
        for point in segment.points:
            x, y = mercator_projection(point.latitude, point.longitude)
            x_coords.append(x)
            y_coords.append(y)
            
        return x_coords, y_coords
    
    def render_route(self, color: str = '#000000', thickness: str = 'medium') -> None:
        """
        Render the route on the current figure.
        
        Args:
            color: Line color in hex format or named color
            thickness: Line thickness ('thin', 'medium', or 'thick')
        """
        if self._figure is None or self._ax is None:
            self.create_figure()
            
        # Get line width from thickness map
        line_width = self.thickness_map.get(thickness, self.thickness_map['medium'])
        
        # Get route bounds for scaling
        min_lat, max_lat, min_lon, max_lon = self.route.get_bounds()
        
        # Project bounds
        min_x, min_y = mercator_projection(min_lat, min_lon)
        max_x, max_y = mercator_projection(max_lat, max_lon)
        
        # Add a small buffer (5% of dimensions)
        x_range = max_x - min_x
        y_range = max_y - min_y
        buffer_x = x_range * 0.05
        buffer_y = y_range * 0.05
        
        # Draw each segment
        for segment in self.route.segments:
            if not segment.points:
                continue
                
            # Project coordinates
            x_coords, y_coords = self._get_projected_coordinates(segment)
            
            # Plot the segment
            self._ax.plot(x_coords, y_coords, color=color, linewidth=line_width, solid_capstyle='round')
        
        # Set axis limits with buffer
        self._ax.set_xlim(min_x - buffer_x, max_x + buffer_x)
        self._ax.set_ylim(min_y - buffer_y, max_y + buffer_y)
        
    def get_figure(self) -> Optional[Figure]:
        """
        Get the current figure.
        
        Returns:
            The current matplotlib Figure object, or None if no figure has been created
        """
        return self._figure

