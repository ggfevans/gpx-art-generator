"""
Exception hierarchy for route-to-art.

This module defines a comprehensive exception hierarchy for the route-to-art tool,
including specialized exceptions for different error types and error message
templates for common errors.
"""

from typing import Dict, Optional, Any, List, Tuple, Union
import os
import traceback


# Error message templates for common error scenarios
ERROR_MESSAGES = {
    # File-related errors
    'file_not_found': "Cannot find file: {path}. Please check the path and try again.",
    'file_not_readable': "Cannot read file: {path}. Check permissions or file integrity.",
    'file_not_writable': "Cannot write to file: {path}. Check permissions or disk space.",
    'invalid_file_type': "Invalid file type for {path}. Expected {expected_types}.",
    'empty_file': "File is empty: {path}. Please provide a valid file.",
    
    # Route parsing errors
    'invalid_route_file': "Invalid route file: {error}. The file may be corrupted.",
    'missing_track': "No track data found in route file: {path}.",
    'no_coordinates': "No coordinate data found in route file: {path}.",
    'malformed_route_file': "Malformed route file: {path}. {error}",
    
    # Validation errors
    'invalid_color': "Invalid color value: {value}. Use hex format (e.g., #FF5500) or named colors.",
    'invalid_thickness': "Invalid thickness: {value}. Valid values are: {valid_values}.",
    'invalid_markers_unit': "Invalid markers unit: {value}. Valid values are: {valid_values}.",
    'invalid_overlay_position': "Invalid overlay position: {value}. Valid values are: {valid_values}.",
    'invalid_format': "Invalid output format: {value}. Valid formats are: {valid_formats}.",
    'invalid_numeric_range': "{parameter} must be between {min_value} and {max_value}, got {value}.",
    'negative_number': "{parameter} must be positive, got {value}.",
    
    # Rendering errors
    'rendering_failure': "Failed to render route: {error}.",
    'empty_route': "Cannot render empty route. No track points found.",
    'matplotlib_error': "Matplotlib error during rendering: {error}.",
    
    # Export errors
    'export_failure': "Failed to export to {format}: {error}.",
    'missing_dependency': "Missing dependency for {format} export: {dependency}. Install with: {install_command}.",
    'permission_denied': "Cannot write to {path}. Check write permissions.",
    'disk_full': "Not enough disk space to write file: {path}.",
    
    # Configuration errors
    'config_not_found': "Configuration file not found: {path}.",
    'config_parse_error': "Error parsing configuration file: {path}. {error}",
    'invalid_config_value': "Invalid configuration value for {key}: {value}. {details}",
    'invalid_config_structure': "Invalid configuration structure: {error}.",
    
    # System errors
    'memory_error': "Not enough memory to complete operation: {operation}.",
    'timeout_error': "Operation timed out: {operation}.",
    'unexpected_error': "An unexpected error occurred: {error}."
}


class RouteArtError(Exception):
    """
    Base exception class for all route-to-art errors.
    
    This class provides context for errors, including the original error message,
    helpful suggestions, and relevant file paths.
    """
    
    def __init__(
        self, 
        message: str, 
        original_error: Optional[Exception] = None,
        suggestion: Optional[str] = None,
        file_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a RouteArtError.
        
        Args:
            message: The error message
            original_error: The original exception that caused this error
            suggestion: A helpful suggestion for resolving the error
            file_path: The path to the file related to the error
            context: Additional context information as a dictionary
        """
        self.message = message
        self.original_error = original_error
        self.suggestion = suggestion
        self.file_path = file_path
        self.context = context or {}
        self.traceback = traceback.format_exc() if original_error else None
        
        # Build the full error message
        full_message = message
        
        # Add file path information if available
        if file_path:
            full_message += f"\nFile: {os.path.abspath(file_path)}"
        
        # Add original error information if available
        if original_error:
            full_message += f"\nOriginal error: {str(original_error)}"
        
        # Add suggestion if available
        if suggestion:
            full_message += f"\nSuggestion: {suggestion}"
        
        super().__init__(full_message)
    
    @classmethod
    def from_template(
        cls, 
        template_key: str, 
        template_vars: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
        suggestion: Optional[str] = None,
        file_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> 'RouteArtError':
        """
        Create an error using a template from ERROR_MESSAGES.
        
        Args:
            template_key: The key for the error template in ERROR_MESSAGES
            template_vars: Dictionary of variables to format the template with
            original_error: The original exception that caused this error
            suggestion: A helpful suggestion for resolving the error
            file_path: The path to the file related to the error
            context: Additional context information as a dictionary
            
        Returns:
            A RouteArtError instance with the formatted message
            
        Raises:
            KeyError: If the template_key is not found in ERROR_MESSAGES
        """
        template_vars = template_vars or {}
        
        # Add file_path to template variables if provided
        if file_path and 'path' not in template_vars:
            template_vars['path'] = file_path
            
        try:
            message = ERROR_MESSAGES[template_key].format(**template_vars)
        except KeyError:
            if template_key not in ERROR_MESSAGES:
                message = f"Unknown error template: {template_key}"
            else:
                missing_vars = [var for var in cls._get_format_vars(ERROR_MESSAGES[template_key]) 
                               if var not in template_vars]
                message = f"Error formatting template '{template_key}': Missing variables {missing_vars}"
        
        return cls(
            message=message,
            original_error=original_error,
            suggestion=suggestion,
            file_path=file_path,
            context=context
        )
    
    @staticmethod
    def _get_format_vars(format_string: str) -> List[str]:
        """
        Extract the variable names from a format string.
        
        Args:
            format_string: A string with {} placeholders
            
        Returns:
            A list of variable names found in the format string
        """
        import re
        return re.findall(r'\{([^{}]+)\}', format_string)


class RouteParseError(RouteArtError):
    """Exception raised for errors during route file parsing."""
    
    @classmethod
    def invalid_route_file(
        cls, 
        error: str, 
        file_path: Optional[str] = None,
        original_error: Optional[Exception] = None
    ) -> 'RouteParseError':
        """
        Create an error for invalid route file.
        
        Args:
            error: Description of the parsing error
            file_path: Path to the route file
            original_error: The original exception that caused this error
            
        Returns:
            A RouteParseError instance
        """
        suggestion = "Check if the file is a valid route file. Try opening it in a text editor to verify its structure."
        return cls.from_template(
            'invalid_route_file',
            {'error': error},
            original_error=original_error,
            suggestion=suggestion,
            file_path=file_path
        )
    
    @classmethod
    def missing_track(
        cls,
        file_path: str,
        original_error: Optional[Exception] = None
    ) -> 'RouteParseError':
        """
        Create an error for route file with no track data.
        
        Args:
            file_path: Path to the route file
            original_error: The original exception that caused this error
            
        Returns:
            A RouteParseError instance
        """
        suggestion = "Make sure the route file contains track segments (<trkseg>) with track points (<trkpt>)."
        return cls.from_template(
            'missing_track',
            {'path': file_path},
            original_error=original_error,
            suggestion=suggestion,
            file_path=file_path
        )
    
    @classmethod
    def no_coordinates(
        cls,
        file_path: str,
        original_error: Optional[Exception] = None
    ) -> 'RouteParseError':
        """
        Create an error for route file with no coordinate data.
        
        Args:
            file_path: Path to the route file
            original_error: The original exception that caused this error
            
        Returns:
            A RouteParseError instance
        """
        suggestion = "Make sure the route file contains track points with latitude and longitude attributes."
        return cls.from_template(
            'no_coordinates',
            {'path': file_path},
            original_error=original_error,
            suggestion=suggestion,
            file_path=file_path
        )


class ValidationError(RouteArtError):
    """Exception raised for validation errors."""
    
    @classmethod
    def invalid_color(
        cls,
        value: str,
        original_error: Optional[Exception] = None
    ) -> 'ValidationError':
        """
        Create an error for invalid color value.
        
        Args:
            value: The invalid color value
            original_error: The original exception that caused this error
            
        Returns:
            A ValidationError instance
        """
        suggestion = "Use hex format (e.g., #FF5500) or a valid named color like 'red', 'blue', etc."
        return cls.from_template(
            'invalid_color',
            {'value': value},
            original_error=original_error,
            suggestion=suggestion
        )
    
    @classmethod
    def invalid_thickness(
        cls,
        value: str,
        valid_values: List[str],
        original_error: Optional[Exception] = None
    ) -> 'ValidationError':
        """
        Create an error for invalid thickness value.
        
        Args:
            value: The invalid thickness value
            valid_values: List of valid thickness values
            original_error: The original exception that caused this error
            
        Returns:
            A ValidationError instance
        """
        valid_str = ", ".join(valid_values)
        suggestion = f"Use one of the valid thickness values: {valid_str}"
        return cls.from_template(
            'invalid_thickness',
            {'value': value, 'valid_values': valid_str},
            original_error=original_error,
            suggestion=suggestion
        )
    
    @classmethod
    def invalid_numeric_range(
        cls,
        parameter: str,
        value: Union[int, float],
        min_value: Union[int, float],
        max_value: Union[int, float],
        original_error: Optional[Exception] = None
    ) -> 'ValidationError':
        """
        Create an error for value outside of allowed numeric range.
        
        Args:
            parameter: Name of the parameter
            value: The invalid value
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            original_error: The original exception that caused this error
            
        Returns:
            A ValidationError instance
        """
        suggestion = f"Provide a {parameter} value between {min_value} and {max_value}."
        return cls.from_template(
            'invalid_numeric_range',
            {
                'parameter': parameter,
                'value': value,
                'min_value': min_value,
                'max_value': max_value
            },
            original_error=original_error,
            suggestion=suggestion
        )


class RenderingError(RouteArtError):
    """Exception raised for errors during route rendering."""
    
    @classmethod
    def rendering_failure(
        cls,
        error: str,
        original_error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> 'RenderingError':
        """
        Create an error for general rendering failures.
        
        Args:
            error: Description of the rendering error
            original_error: The original exception that caused this error
            context: Additional context information
            
        Returns:
            A RenderingError instance
        """
        suggestion = "Check if matplotlib is installed correctly and try with a different route file."
        return cls.from_template(
            'rendering_failure',
            {'error': error},
            original_error=original_error,
            suggestion=suggestion,
            context=context
        )
    
    @classmethod
    def empty_route(
        cls,
        original_error: Optional[Exception] = None
    ) -> 'RenderingError':
        """
        Create an error for empty route rendering attempt.
        
        Args:
            original_error: The original exception that caused this error
            
        Returns:
            A RenderingError instance
        """
        suggestion = "Make sure the route file contains valid track points with coordinate data."
        return cls.from_template(
            'empty_route',
            {},
            original_error=original_error,
            suggestion=suggestion
        )
    
    @classmethod
    def matplotlib_error(
        cls,
        error: str,
        original_error: Optional[Exception] = None
    ) -> 'RenderingError':
        """
        Create an error for matplotlib-specific errors.
        
        Args:
            error: Description of the matplotlib error
            original_error: The original exception that caused this error
            
        Returns:
            A RenderingError instance
        """
        suggestion = "Try updating matplotlib or check if the figure dimensions are valid."
        return cls.from_template(
            'matplotlib_error',
            {'error': error},
            original_error=original_error,
            suggestion=suggestion
        )


class ExportError(RouteArtError):
    """Exception raised for errors during file export."""
    
    @classmethod
    def export_failure(
        cls,
        format: str,
        error: str,
        original_error: Optional[Exception] = None,
        file_path: Optional[str] = None
    ) -> 'ExportError':
        """
        Create an error for general export failures.
        
        Args:
            format: The export format that failed
            error: Description of the export error
            original_error: The original exception that caused this error
            file_path: Path to the output file
            
        Returns:
            An ExportError instance
        """
        suggestion = f"Check if you have the required libraries for {format} export installed."
        return cls.from_template(
            'export_failure',
            {'format': format, 'error': error},
            original_error=original_error,
            suggestion=suggestion,
            file_path=file_path
        )
    
    @classmethod
    def missing_dependency(
        cls,

