"""
Export functionality for GPX visualizations.

This module provides classes and functions for exporting visualizations
to various file formats.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Union

import matplotlib.figure
import matplotlib.pyplot as plt


class ExportError(Exception):
    """Exception raised for errors during the export process."""
    pass


class Exporter:
    """
    Handles exporting matplotlib figures to various file formats.
    """
    
    def __init__(self):
        """Initialize the exporter."""
        pass
    
    def _validate_output_directory(self, output_path: Union[str, Path]) -> None:
        """
        Validate that the output directory exists and is writable.
        
        Args:
            output_path: Path to the output file
            
        Raises:
            ExportError: If the directory doesn't exist or isn't writable
        """
        # Convert to Path object if string
        if isinstance(output_path, str):
            output_path = Path(output_path)
            
        # Get the directory
        output_dir = output_path.parent
        
        # Check if directory exists
        if not output_dir.exists():
            raise ExportError(f"Output directory does not exist: {output_dir}")
            
        # Check if directory is writable
        if not os.access(output_dir, os.W_OK):
            raise ExportError(f"Output directory is not writable: {output_dir}")
    
    def _validate_file_extension(self, output_path: Union[str, Path], expected_ext: str) -> None:
        """
        Validate that the file has the expected extension.
        
        Args:
            output_path: Path to the output file
            expected_ext: Expected file extension (without the dot)
            
        Raises:
            ExportError: If the file doesn't have the expected extension
        """
        # Convert to Path object if string
        if isinstance(output_path, str):
            output_path = Path(output_path)
            
        # Check extension
        if output_path.suffix.lower() != f".{expected_ext.lower()}":
            raise ExportError(
                f"Output file must have .{expected_ext} extension, got: {output_path.suffix}"
            )
    
    def _verify_output_file(self, output_path: Union[str, Path]) -> None:
        """
        Verify that the output file was created and has a non-zero size.
        
        Args:
            output_path: Path to the output file
            
        Raises:
            ExportError: If the file wasn't created or has zero size
        """
        # Convert to Path object if string
        if isinstance(output_path, str):
            output_path = Path(output_path)
            
        # Check if file exists
        if not output_path.exists():
            raise ExportError(f"Output file was not created: {output_path}")
            
        # Check if file has content
        if output_path.stat().st_size == 0:
            raise ExportError(f"Output file is empty: {output_path}")
    
    def export_png(
        self, 
        figure: matplotlib.figure.Figure, 
        output_path: Union[str, Path], 
        dpi: int = 300
    ) -> None:
        """
        Export a matplotlib figure to a PNG file.
        
        Args:
            figure: The matplotlib figure to export
            output_path: Path to the output PNG file
            dpi: Resolution in dots per inch
            
        Raises:
            ExportError: If export fails for any reason
        """
        # Convert to Path object if string
        if isinstance(output_path, str):
            output_path = Path(output_path)
            
        # Validate output path
        self._validate_output_directory(output_path)
        self._validate_file_extension(output_path, "png")
        
        # Use a temporary file to avoid partial writes on error
        temp_file = None
        try:
            # Create a temporary file in the same directory
            fd, temp_path = tempfile.mkstemp(dir=output_path.parent, suffix='.png')
            os.close(fd)  # Close the file descriptor
            temp_file = Path(temp_path)
            
            # Save figure to temporary file
            figure.savefig(
                temp_file,
                dpi=dpi,
                bbox_inches='tight',
                pad_inches=0,
                transparent=True
            )
            
            # Verify the temporary file
            self._verify_output_file(temp_file)
            
            # Move the temporary file to the destination
            if output_path.exists():
                output_path.unlink()  # Remove existing file
            temp_file.rename(output_path)
            temp_file = None  # Don't delete in finally block
            
            # Final verification
            self._verify_output_file(output_path)
            
        except Exception as e:
            # Handle matplotlib or file system errors
            if isinstance(e, ExportError):
                # Re-raise our custom errors
                raise
            else:
                # Wrap other errors
                raise ExportError(f"Failed to export PNG: {str(e)}") from e
                
        finally:
            # Clean up temporary file if it exists
            if temp_file is not None and temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass  # Ignore errors in cleanup

