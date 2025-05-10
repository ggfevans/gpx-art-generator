"""
Visualization functionality for GPX routes.

This module provides classes and functions for rendering GPX routes
as visual artwork using matplotlib.
"""

import math
import re
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Literal, Optional, Set, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.text import Text

from gpx_art.models import Route, RoutePoint, RouteSegment


class OverlayPosition(Enum):
    """Positions for information overlays."""
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()
    
    @classmethod
    def from_string(cls, position: str) -> 'OverlayPosition':
        """Convert string position to enum value."""
        position = position.lower().replace('-', '_')
        
        if position == "top_left":
            return cls.TOP_LEFT
        elif position == "top_right":
            return cls.TOP_RIGHT
        elif position == "bottom_left":
            return cls.BOTTOM_LEFT
        elif position == "bottom_right":
            return cls.BOTTOM_RIGHT
        else:
            valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
            raise ValueError(f"Invalid position: {position}. Valid options: {', '.join(valid_positions)}")


class OverlayField(Enum):
    """Available fields for information overlay."""
    DISTANCE = auto()
    DURATION = auto()
    ELEVATION = auto()
    NAME = auto()
    DATE = auto()
    
    @classmethod
    def from_string(cls, field: str) -> 'OverlayField':
        """Convert string field name to enum value."""
        field = field.upper()
        
        if field == "DISTANCE":
            return cls.DISTANCE
        elif field == "DURATION":
            return cls.DURATION
        elif field == "ELEVATION":
            return cls.ELEVATION
        elif field == "NAME":
            return cls.NAME
        elif field == "DATE":
            return cls.DATE
        else:
            valid_fields = ["distance", "duration", "elevation", "name", "date"]
            raise ValueError(f"Invalid field: {field}. Valid options: {', '.join(valid_fields)}")
            
    @classmethod
    def from_strings(cls, fields: List[str]) -> List['OverlayField']:
        """Convert a list of field names to enum values."""
        return [cls.from_string(field) for field in fields]


class OverlayFormatter:
    """
    Formats route information for display in overlays.
    
    This class handles formatting various types of data (distance, time, etc.)
    in a consistent way, with appropriate handling of missing data.
    """
    
    @staticmethod
    def format_distance(meters: float) -> str:
        """Format distance in both kilometers and miles."""
        km = meters / 1000
        miles = meters / 1609.34
        return f"{km:.1f} km ({miles:.1f} miles)"
    
    @staticmethod
    def format_duration(duration: Optional[timedelta]) -> str:
        """Format duration for display."""
        if not duration:
            return "Unknown duration"
        
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0 or days > 0:
            parts.append(f"{hours}h")
        if minutes > 0 or hours > 0 or days > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 and not (hours > 0 or days > 0):
            parts.append(f"{seconds}s")
            
        if not parts:
            parts = ["0m"]
            
        return " ".join(parts)
    
    @staticmethod
    def format_elevation(stats: Optional[Dict[str, float]]) -> str:
        """Format elevation statistics for display."""
        if not stats:
            return "No elevation data"
        
        gain = stats.get('gain', 0)
        loss = stats.get('loss', 0)
        min_ele = stats.get('min', 0)
        max_ele = stats.get('max', 0)
        
        range_str = f"{min_ele:.0f}-{max_ele:.0f}m"
        change_str = f"↑{gain:.0f}m ↓{loss:.0f}m"
        
        return f"{range_str} ({change_str})"
    
    @staticmethod
    def format_date(timestamp: Optional[datetime]) -> str:
        """Format date for display."""
        if not timestamp:
            return "No date"
        
        return timestamp.strftime("%Y-%m-%d")
    
    @staticmethod
    def format_name(name: Optional[str]) -> str:
        """Format route name for display."""
        if not name:
            return "Unnamed route"
        
        # Truncate long names
        max_length = 30
        if len(name) > max_length:
            return name[:max_length] + "..."
        
        return name
    
    @classmethod
    def format_field(cls, field: OverlayField, route: Route) -> str:
        """
        Format a specific field based on route data.
        
        Args:
            field: The field to format
            route: The Route object containing the data
            
        Returns:
            Formatted field string with label
        """
        if field == OverlayField.DISTANCE:
            value = cls.format_distance(route.get_total_distance())
            return f"Distance: {value}"
            
        elif field == OverlayField.DURATION:
            value = cls.format_duration(route.get_total_duration())
            return f"Duration: {value}"
            
        elif field == OverlayField.ELEVATION:
            value = cls.format_elevation(route.get_elevation_stats())
            return f"Elevation: {value}"
            
        elif field == OverlayField.NAME:
            value = cls.format_name(route.name)
            return f"Route: {value}"
            
        elif field == OverlayField.DATE:
            # Extract date from first point with timestamp
            timestamp = None
            for segment in route.segments:
                for point in segment.points:
                    if point.timestamp:
                        timestamp = point.timestamp
                        break
                if timestamp:
                    break
                    
            value = cls.format_date(timestamp)
            return f"Date: {value}"
            
        else:
            return "Unknown field"


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
    
    # Style mapping for line styles
    style_map = {
        'solid': '-',
        'dashed': '--'
    }
    
    # Marker unit conversion factors (from meters)
    _UNIT_FACTORS = {
        'km': 0.001,      # 1 meter = 0.001 kilometers
        'miles': 0.000621371  # 1 meter = 0.000621371 miles
    }
    
    # Default marker intervals by unit
    _DEFAULT_INTERVALS = {
        'km': 1.0,        # 1 kilometer
        'miles': 1.0      # 1 mile
    }
    
    # Regular expression for validating hex color codes
    _HEX_COLOR_PATTERN = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')
    
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
    
    def _validate_color(self, color: str) -> str:
        """
        Validate and normalize a color value.
        
        Args:
            color: Color string (hex code or named color)
            
        Returns:
            Validated color string
            
        Raises:
            ValueError: If the color is not a valid hex code or named color
        """
        # If it's a hex color code, validate format
        if color.startswith('#'):
            if not self._HEX_COLOR_PATTERN.match(color):
                raise ValueError(f"Invalid hex color code: {color}")
        
        # For named colors, we'll rely on matplotlib's validation
        # when the color is actually used
        
        return color
    
    def _validate_thickness(self, thickness: str) -> float:
        """
        Validate thickness value and return the corresponding line width.
        
        Args:
            thickness: Thickness name ('thin', 'medium', or 'thick')
            
        Returns:
            Line width value
            
        Raises:
            ValueError: If thickness is not a valid option
        """
        if thickness not in self.thickness_map:
            valid_options = ', '.join(self.thickness_map.keys())
            raise ValueError(
                f"Invalid thickness: {thickness}. Valid options are: {valid_options}"
            )
        
        return self.thickness_map[thickness]
    
    def _validate_line_style(self, line_style: str) -> str:
        """
        Validate line style value and return the corresponding matplotlib style.
        
        Args:
            line_style: Line style name ('solid' or 'dashed')
            
        Returns:
            Matplotlib line style string
            
        Raises:
            ValueError: If line_style is not a valid option
        """
        if line_style not in self.style_map:
            valid_options = ', '.join(self.style_map.keys())
            raise ValueError(
                f"Invalid line style: {line_style}. Valid options are: {valid_options}"
            )
        
        return self.style_map[line_style]
        
    def _calculate_point_distances(self, segment: RouteSegment) -> List[float]:
        """
        Calculate cumulative distances from the start of segment for each point.
        
        Args:
            segment: Route segment to calculate distances for
            
        Returns:
            List of distances in meters
        """
        if len(segment.points) < 2:
            return [0.0] * len(segment.points)
            
        distances = [0.0]  # First point is at distance 0
        cumulative_distance = 0.0
        
        for i in range(1, len(segment.points)):
            p1 = segment.points[i-1]
            p2 = segment.points[i]
            
            # Calculate distance between consecutive points
            point_distance = haversine_distance(
                p1.latitude, p1.longitude, p2.latitude, p2.longitude
            )
            
            # Add to cumulative distance
            cumulative_distance += point_distance
            distances.append(cumulative_distance)
            
        return distances
    
    def _find_marker_positions(
        self, 
        segment: RouteSegment, 
        unit: Literal['km', 'miles'] = 'miles',
        interval: float = 1.0
    ) -> List[Tuple[float, float, float]]:
        """
        Find positions along the segment for distance markers.
        
        Args:
            segment: Route segment to place markers on
            unit: Distance unit ('km' or 'miles')
            interval: Distance between markers in the specified unit
            
        Returns:
            List of (projected_x, projected_y, distance_in_unit) tuples
        """
        if len(segment.points) < 2:
            return []
            
        # Calculate distances for each point
        distances_meters = self._calculate_point_distances(segment)
        
        # Convert to the desired unit
        unit_factor = self._UNIT_FACTORS[unit]
        distances_unit = [d * unit_factor for d in distances_meters]
        
        # Calculate target distances for markers
        max_distance = distances_unit[-1]
        marker_distances = []
        
        # Start at the first interval and continue until we exceed the segment length
        current_distance = interval
        while current_distance < max_distance:
            marker_distances.append(current_distance)
            current_distance += interval
        
        # Find positions for each marker distance
        marker_positions = []
        
        for marker_distance in marker_distances:
            # Find the points that bracket this distance
            for i in range(1, len(distances_unit)):
                if distances_unit[i-1] <= marker_distance <= distances_unit[i]:
                    # Found the bracketing points
                    p1 = segment.points[i-1]
                    p2 = segment.points[i]
                    d1 = distances_unit[i-1]
                    d2 = distances_unit[i]
                    
                    # Interpolate between the points
                    ratio = (marker_distance - d1) / (d2 - d1) if d2 != d1 else 0
                    
                    # Linear interpolation of lat/lon
                    marker_lat = p1.latitude + ratio * (p2.latitude - p1.latitude)
                    marker_lon = p1.longitude + ratio * (p2.longitude - p1.longitude)
                    
                    # Project to map coordinates
                    marker_x, marker_y = mercator_projection(marker_lat, marker_lon)
                    
                    marker_positions.append((marker_x, marker_y, marker_distance))
                    break
        
        return marker_positions
    
    def _format_distance_label(self, distance: float, unit: str) -> str:
        """
        Format a distance value for display.
        
        Args:
            distance: Distance value in the specified unit
            unit: Distance unit ('km' or 'miles')
            
        Returns:
            Formatted distance string
        """
        return f"{distance:.1f} {unit}"
        
    def add_distance_markers(
        self,
        unit: Literal['km', 'miles'] = 'miles',
        interval: Optional[float] = None,
        marker_size: float = 6,
        marker_color: Optional[str] = None,
        show_labels: bool = True,
        label_font_size: int = 8,
        label_offset: Tuple[float, float] = (0.0002, 0.0002)
    ) -> None:
        """
        Add distance markers along the route.
        
        Args:
            unit: Distance unit ('km' or 'miles')
            interval: Distance between markers in the specified unit
                      If None, uses default interval for the unit
            marker_size: Size of the marker points
            marker_color: Color of markers (defaults to route color)
            show_labels: Whether to show distance labels
            label_font_size: Font size for distance labels
            label_offset: (x, y) offset for label positioning
        """
        if self._figure is None or self._ax is None:
            raise ValueError("Figure must be created before adding markers")
            
        # Validate unit
        if unit not in self._UNIT_FACTORS:
            valid_units = ', '.join(self._UNIT_FACTORS.keys())
            raise ValueError(f"Invalid unit: {unit}. Valid options: {valid_units}")
            
        # Use default interval if none specified
        if interval is None:
            interval = self._DEFAULT_INTERVALS[unit]
            
        # Process each segment
        for segment in self.route.segments:
            if not segment.points:
                continue
                
            # Find marker positions
            marker_positions = self._find_marker_positions(segment, unit, interval)
            
            if not marker_positions:
                continue
                
            # Extract coordinates and distances
            x_coords, y_coords, distances = zip(*marker_positions)
            
            # Plot markers
            self._ax.scatter(
                x_coords, 
                y_coords,
                s=marker_size**2,  # size is in points^2
                color=marker_color if marker_color else self._current_color,
                zorder=10  # Ensure markers are on top of the line
            )
            
            # Add labels if requested
            if show_labels:
                for x, y, distance in marker_positions:
                    label = self._format_distance_label(distance, unit)
                    self._ax.text(
                        x + label_offset[0],
                        y + label_offset[1],
                        label,
                        fontsize=label_font_size,
                        ha='left',
                        va='bottom',
                        bbox=dict(
                            facecolor='white',
                            alpha=0.7,
                            edgecolor='none',
                            boxstyle='round,pad=0.3'
                        )
                    )

    def render_route(self, color: str = '#000000', thickness: str = 'medium', line_style: str = 'solid') -> None:
        """
        Render the route on the current figure.
        
        Args:
            color: Line color in hex format or named color
            thickness: Line thickness ('thin', 'medium', or 'thick')
            line_style: Line style ('solid' or 'dashed')
            
        Raises:
            ValueError: If any style parameters are invalid
        """
        if self._figure is None or self._ax is None:
            self.create_figure()
        
        # Validate styling parameters
        color = self._validate_color(color)
        line_width = self._validate_thickness(thickness)
        style = self._validate_line_style(line_style)
        
        # Store current color for markers
        self._current_color = color
        
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
            
            # Plot the segment with line style
            self._ax.plot(
                x_coords, 
                y_coords, 
                color=color, 
                linewidth=line_width, 
                linestyle=style,
                solid_capstyle='round'
            )
        
        # Set axis limits with buffer
        self._ax.set_xlim(min_x - buffer_x, max_x + buffer_x)
        self._ax.set_ylim(min_y - buffer_y, max_y + buffer_y)
        
    def _get_overlay_position_coords(
        self, 
        position: OverlayPosition,
        padding: float = 0.02
    ) -> Tuple[str, str, Tuple[float, float]]:
        """
        Calculate coordinates and alignment for overlay positioning.
        
        Args:
            position: Corner position for the overlay
            padding: Padding from the edge as a fraction of the axis size
            
        Returns:
            Tuple of (horizontal_alignment, vertical_alignment, (x, y))
        """
        # Get current axis limits
        xlim = self._ax.get_xlim()
        ylim = self._ax.get_ylim()
        
        # Calculate padding in data coordinates
        x_padding = padding * (xlim[1] - xlim[0])
        y_padding = padding * (ylim[1] - ylim[0])
        
        if position == OverlayPosition.TOP_LEFT:
            return 'left', 'top', (xlim[0] + x_padding, ylim[1] - y_padding)
        elif position == OverlayPosition.TOP_RIGHT:
            return 'right', 'top', (xlim[1] - x_padding, ylim[1] - y_padding)
        elif position == OverlayPosition.BOTTOM_LEFT:
            return 'left', 'bottom', (xlim[0] + x_padding, ylim[0] + y_padding)
        elif position == OverlayPosition.BOTTOM_RIGHT:
            return 'right', 'bottom', (xlim[1] - x_padding, ylim[0] + y_padding)
        else:
            # Default to top left
            return 'left', 'top', (xlim[0] + x_padding, ylim[1] - y_padding)
    
    def add_overlay(
        self,
        fields: Union[List[str], List[OverlayField]],
        position: Union[str, OverlayPosition] = 'top-left',
        font_size: int = 10,
        font_color: str = 'black',
        background: bool = True,
        bg_color: str = 'white',
        bg_alpha: float = 0.7,
        padding: float = 0.02
    ) -> None:
        """
        Add an information overlay to the visualization.
        
        Args:
            fields: List of information fields to include
            position: Corner position ('top-left', 'top-right', 'bottom-left', 'bottom-right')
            font_size: Text font size
            font_color: Text color
            background: Whether to add a background box
            bg_color: Background box color
            bg_alpha: Background box transparency (0-1)
            padding: Padding from the edge as a fraction of the axis size
        """
        if self._figure is None or self._ax is None:
            raise ValueError("Figure must be created before adding overlay")
        
        # Convert position to enum if string
        if isinstance(position, str):
            position = OverlayPosition.from_string(position)
            
        # Convert fields to enum if strings
        if fields and isinstance(fields[0], str):
            fields = OverlayField.from_strings(fields)
            
        # Get positioning information
        ha, va, (x, y) = self._get_overlay_position_coords(position, padding)
        
        # Format each field
        formatter = OverlayFormatter()
        lines = [formatter.format_field(field, self.route) for field in fields]
        text = '\n'.join(lines)
        
        # Create the overlay text
        text_obj = self._ax.text(
            x, y, text,
            fontsize=font_size,
            color=font_color,
            ha=ha,
            va=va,
            transform=self._ax.transData,
            zorder=20  # Ensure overlay is on top
        )
        
        # Add background box if requested
        if background:
            bbox_props = dict(
                boxstyle='round,pad=0.5',
                facecolor=bg_color,
                alpha=bg_alpha,
                edgecolor='none'
            )
            text_obj.set_bbox(bbox_props)
    
    def get_figure(self) -> Optional[Figure]:
        """
        Get the current figure.
        
        Returns:
            The current matplotlib Figure object, or None if no figure has been created
        """
        return self._figure

