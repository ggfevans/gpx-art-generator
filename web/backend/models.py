"""
Pydantic data models for GPX Art Generator API.

This module defines the data models used for request and response validation
in the FastAPI application.
"""

import re
from typing import List, Optional, Dict, Any, Literal, Union, Set
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, validator


class LineThickness(str, Enum):
    """Line thickness options for route visualization."""
    THIN = "thin"
    MEDIUM = "medium"
    THICK = "thick"


class LineStyle(str, Enum):
    """Line style options for route visualization."""
    SOLID = "solid"
    DASHED = "dashed"


class OverlayPosition(str, Enum):
    """Position options for information overlay."""
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"


class DistanceUnit(str, Enum):
    """Distance unit options."""
    KILOMETERS = "km"
    MILES = "mi"


class ExportFormat(str, Enum):
    """Export format options."""
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"


class OverlayElement(str, Enum):
    """Available overlay information elements."""
    NAME = "name"
    DISTANCE = "distance"
    ELEVATION = "elevation"
    DURATION = "duration"
    PACE = "pace"
    SPEED = "speed"
    DATE = "date"


class GenerateOptions(BaseModel):
    """Options for generating artwork from a GPX file."""
    
    # Styling options
    color: Optional[str] = Field(
        default="#0066CC", 
        description="Route line color as hex code"
    )
    background: Optional[str] = Field(
        default="#FFFFFF", 
        description="Background color as hex code"
    )
    thickness: Optional[LineThickness] = Field(
        default=LineThickness.MEDIUM, 
        description="Route line thickness"
    )
    style: Optional[LineStyle] = Field(
        default=LineStyle.SOLID, 
        description="Route line style"
    )
    
    # Marker options
    markers: Optional[bool] = Field(
        default=False, 
        description="Whether to show distance markers"
    )
    markers_unit: Optional[DistanceUnit] = Field(
        default=DistanceUnit.KILOMETERS, 
        description="Unit for distance markers"
    )
    markers_frequency: Optional[float] = Field(
        default=1.0,
        description="Frequency of distance markers in the selected unit",
        ge=0.1,  # Must be at least 0.1
        le=100.0  # Maximum of 100
    )
    
    # Overlay options
    overlay: Optional[List[str]] = Field(
        default=["name", "distance"], 
        description="Information elements to include in overlay"
    )
    overlay_position: Optional[OverlayPosition] = Field(
        default=OverlayPosition.TOP_RIGHT, 
        description="Position of information overlay"
    )
    
    # Export options
    formats: Optional[List[ExportFormat]] = Field(
        default=[ExportFormat.PNG], 
        description="Output file formats"
    )
    dpi: Optional[int] = Field(
        default=300,
        description="DPI for raster image exports (PNG)",
        ge=72,  # Minimum DPI
        le=1200  # Maximum DPI
    )
    
    # Advanced options
    padding: Optional[float] = Field(
        default=0.1,
        description="Padding around the route as a fraction of size",
        ge=0.0,
        le=0.5
    )
    simplify: Optional[bool] = Field(
        default=False,
        description="Whether to simplify the route for rendering"
    )
    simplify_tolerance: Optional[float] = Field(
        default=0.0001,
        description="Simplification tolerance value",
        ge=0.00001,
        le=0.01
    )
    
    model_config = {
        "use_enum_values": True,
        "extra": "ignore"
    }
    
    @field_validator('color', 'background')
    @classmethod
    def validate_color(cls, value: Optional[str]) -> Optional[str]:
        """Validate hex color codes."""
        if value is None:
            return value
            
        # Check if it's a valid hex color
        hex_pattern = r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$'
        if not re.match(hex_pattern, value):
            raise ValueError(f"Invalid hex color code: {value}. Must be in format #RGB or #RRGGBB")
            
        return value
    
    @field_validator('overlay')
    @classmethod
    def validate_overlay_elements(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        """Validate overlay element values."""
        if value is None:
            return value
            
        valid_elements = {e.value for e in OverlayElement}
        for element in value:
            if element not in valid_elements:
                raise ValueError(
                    f"Invalid overlay element: {element}. "
                    f"Valid options are: {', '.join(valid_elements)}"
                )
                
        return value
    
    @field_validator('formats')
    @classmethod
    def validate_formats(cls, value: Optional[List[ExportFormat]]) -> Optional[List[ExportFormat]]:
        """Validate export formats."""
        if value is None or not value:
            return [ExportFormat.PNG]  # Default to PNG if empty
            
        return value
    
    @model_validator(mode='after')
    def validate_marker_dependencies(self) -> 'GenerateOptions':
        """Validate dependencies between markers options."""
        if self.markers_unit is not None and not self.markers:
            # If markers are disabled but unit is specified, log a warning
            # We'll still accept it, just note the inconsistency
            pass
            
        return self


class FileInfo(BaseModel):
    """Information about a generated file."""
    id: str = Field(..., description="Unique identifier for the file")
    name: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    url: str = Field(..., description="URL to download the file")
    format: str = Field(..., description="File format (png, svg, pdf)")
    
    @field_validator('size')
    @classmethod
    def validate_size(cls, value: int) -> int:
        """Validate file size is positive."""
        if value < 0:
            raise ValueError("File size cannot be negative")
        return value
    
    @field_validator('format')
    @classmethod
    def validate_format(cls, value: str) -> str:
        """Validate file format."""
        valid_formats = {fmt.value for fmt in ExportFormat}
        if value.lower() not in valid_formats:
            raise ValueError(f"Invalid format: {value}. Valid formats: {', '.join(valid_formats)}")
        return value.lower()


class TaskStatus(str, Enum):
    """Status values for generation tasks."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerateResponse(BaseModel):
    """Response model for the generate endpoint."""
    id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(
        ..., description="Task status"
    )
    files: List[FileInfo] = Field(
        default=[], description="Generated file information"
    )
    message: Optional[str] = Field(
        None, description="Additional information about the task"
    )
    
    model_config = {
        "use_enum_values": True
    }


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error detail message")
    code: Optional[str] = Field(None, description="Error code")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "Invalid file type. Only GPX files are supported.",
                    "code": "invalid_file_type"
                }
            ]
        }
    }


class HealthCheck(BaseModel):
    """API health check response."""
    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")

