"""
Export functionality for GPX visualizations.

This module provides classes and functions for exporting visualizations
to various file formats.
"""

import io
import os
import tempfile
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PIL import Image
from reportlab.lib.utils import ImageReader


class ExportError(Exception):
    """Exception raised for errors during the export process."""
    pass


class ExportFormat(Enum):
    """Supported export formats."""
    PNG = auto()
    SVG = auto()
    PDF = auto()
    
    @classmethod
    def from_extension(cls, path: Union[str, Path]) -> 'ExportFormat':
        """
        Determine the export format from a file extension.
        
        Args:
            path: Path to the output file
            
        Returns:
            ExportFormat enum value
            
        Raises:
            ExportError: If the file extension is not recognized
        """
        if isinstance(path, str):
            path = Path(path)
            
        ext = path.suffix.lower()
        
        if ext == '.png':
            return cls.PNG
        elif ext == '.svg':
            return cls.SVG
        elif ext == '.pdf':
            return cls.PDF
        else:
            valid_exts = '.png, .svg, .pdf'
            raise ExportError(f"Unsupported file extension: {ext}. Must be one of: {valid_exts}")
    
    @property
    def extension(self) -> str:
        """Get the file extension for this format."""
        if self == ExportFormat.PNG:
            return '.png'
        elif self == ExportFormat.SVG:
            return '.svg'
        elif self == ExportFormat.PDF:
            return '.pdf'
        else:
            return ''  # Should never happen


class PageSize:
    """Common page sizes for PDF export."""
    
    # Dictionary mapping size names to dimensions in points (width, height)
    SIZES: Dict[str, Tuple[float, float]] = {
        'letter': (8.5 * inch, 11 * inch),  # US Letter
        'a4': (8.27 * inch, 11.69 * inch),  # A4
        'square-small': (5 * inch, 5 * inch),  # Small square
        'square-medium': (8 * inch, 8 * inch),  # Medium square
        'square-large': (12 * inch, 12 * inch),  # Large square
        'landscape-small': (6 * inch, 4 * inch),  # Small landscape
        'landscape-medium': (10 * inch, 8 * inch),  # Medium landscape
        'landscape-large': (14 * inch, 11 * inch),  # Large landscape
    }
    
    @classmethod
    def get_size(cls, name: str) -> Tuple[float, float]:
        """Get page dimensions for a named size."""
        name = name.lower()
        if name not in cls.SIZES:
            valid_sizes = ', '.join(cls.SIZES.keys())
            raise ValueError(f"Unknown page size: {name}. Valid sizes: {valid_sizes}")
        return cls.SIZES[name]


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
    
    def _validate_file_extension(self, output_path: Union[str, Path], expected_format: ExportFormat) -> None:
        """
        Validate that the file has the expected extension.
        
        Args:
            output_path: Path to the output file
            expected_format: Expected export format
            
        Raises:
            ExportError: If the file doesn't have the expected extension
        """
        # Convert to Path object if string
        if isinstance(output_path, str):
            output_path = Path(output_path)
            
        # Check extension
        if output_path.suffix.lower() != expected_format.extension:
            raise ExportError(
                f"Output file must have {expected_format.extension} extension, got: {output_path.suffix}"
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
    
    def get_format(self, output_path: Union[str, Path]) -> ExportFormat:
        """
        Determine the export format from the output path.
        
        Args:
            output_path: Path to the output file
            
        Returns:
            ExportFormat enum value
        """
        return ExportFormat.from_extension(output_path)
    
    def export(
        self,
        figure: matplotlib.figure.Figure,
        output_path: Union[str, Path],
        dpi: int = 300,
        page_size: str = 'letter'
    ) -> None:
        """
        Export a matplotlib figure to the appropriate format based on file extension.
        
        Args:
            figure: The matplotlib figure to export
            output_path: Path to the output file
            dpi: Resolution in dots per inch (for raster formats)
            page_size: Page size for PDF export
            
        Raises:
            ExportError: If export fails for any reason
        """
        # Determine format from file extension
        export_format = self.get_format(output_path)
        
        # Call the appropriate export method
        if export_format == ExportFormat.PNG:
            self.export_png(figure, output_path, dpi)
        elif export_format == ExportFormat.SVG:
            self.export_svg(figure, output_path)
        elif export_format == ExportFormat.PDF:
            self.export_pdf(figure, output_path, page_size)
        else:
            # This should never happen due to the check in get_format
            raise ExportError(f"Unsupported export format: {export_format}")
            
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
        self._validate_file_extension(output_path, ExportFormat.PNG)
        
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
                transparent=True,
                format='png'
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
    
    def export_svg(
        self,
        figure: matplotlib.figure.Figure,
        output_path: Union[str, Path]
    ) -> None:
        """
        Export a matplotlib figure to an SVG file.
        
        Args:
            figure: The matplotlib figure to export
            output_path: Path to the output SVG file
            
        Raises:
            ExportError: If export fails for any reason
        """
        # Convert to Path object if string
        if isinstance(output_path, str):
            output_path = Path(output_path)
            
        # Validate output path
        self._validate_output_directory(output_path)
        self._validate_file_extension(output_path, ExportFormat.SVG)
        
        # Use a temporary file to avoid partial writes on error
        temp_file = None
        try:
            # Create a temporary file in the same directory
            fd, temp_path = tempfile.mkstemp(dir=output_path.parent, suffix='.svg')
            os.close(fd)  # Close the file descriptor
            temp_file = Path(temp_path)
            
            # Save figure to temporary file
            figure.savefig(
                temp_file,
                bbox_inches='tight',
                pad_inches=0,
                format='svg'
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
                raise ExportError(f"Failed to export SVG: {str(e)}") from e
                
        finally:
            # Clean up temporary file if it exists
            if temp_file is not None and temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass  # Ignore errors in cleanup
    
    def export_pdf(
        self,
        figure: matplotlib.figure.Figure,
        output_path: Union[str, Path],
        page_size: str = 'letter'
    ) -> None:
        """
        Export a matplotlib figure to a PDF file.
        
        Args:
            figure: The matplotlib figure to export
            output_path: Path to the output PDF file
            page_size: Name of the page size ('letter', 'a4', 'square-medium', etc.)
            
        Raises:
            ExportError: If export fails for any reason
        """
        # Convert to Path object if string
        if isinstance(output_path, str):
            output_path = Path(output_path)
            
        # Validate output path
        self._validate_output_directory(output_path)
        self._validate_file_extension(output_path, ExportFormat.PDF)
        
        # Use a temporary file to avoid partial writes on error
        temp_file = None
        try:
            # Create a temporary file in the same directory
            fd, temp_path = tempfile.mkstemp(dir=output_path.parent, suffix='.pdf')
            os.close(fd)  # Close the file descriptor
            temp_file = Path(temp_path)
            
            # Get page dimensions
            try:
                width, height = PageSize.get_size(page_size)
            except ValueError as e:
                raise ExportError(str(e))
            
            # First, save as a PNG to a buffer
            buf = io.BytesIO()
            figure.savefig(
                buf, 
                format='png', 
                dpi=300,
                bbox_inches='tight',
                pad_inches=0
            )
            buf.seek(0)
            
            # Create a PDF with reportlab
            c = canvas.Canvas(str(temp_file), pagesize=(width, height))
            
            # Calculate dimensions of the figure to maintain aspect ratio
            fig_width, fig_height = figure.get_size_inches()
            aspect_ratio = fig_width / fig_height
            
            # Calculate scaling to fit the page while maintaining aspect ratio
            # Leave some margin
            margin = 0.5 * inch
            available_width = width - (2 * margin)
            available_height = height - (2 * margin)
            
            # Scale based on the more constraining dimension
            page_aspect = available_width / available_height
            if aspect_ratio > page_aspect:
                # Width is the constraint
                pdf_width = available_width
                pdf_height = pdf_width / aspect_ratio
            else:
                # Height is the constraint
                pdf_height = available_height
                pdf_width = pdf_height * aspect_ratio
            
            # Center on the page
            x_pos = (width - pdf_width) / 2
            y_pos = (height - pdf_height) / 2
            
            # Add the image to the PDF
            img = plt.imread(buf)
            c.drawImage(
                ImageReader(np.array(img * 255, dtype=np.uint8)),
                x_pos, 
                y_pos, 
                width=pdf_width, 
                height=pdf_height
            )
            
            # Finish the PDF
            c.save()
            
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
            # Handle matplotlib, reportlab or file system errors
            if isinstance(e, ExportError):
                # Re-raise our custom errors
                raise
            else:
                # Wrap other errors
                raise ExportError(f"Failed to export PDF: {str(e)}") from e
                
        finally:
            # Clean up temporary file if it exists
            if temp_file is not None and temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass  # Ignore errors in cleanup
                    
    def export_multiple(
        self,
        figure: matplotlib.figure.Figure,
        base_path: Union[str, Path],
        formats: list[str],
        dpi: int = 300,
        page_size: str = 'letter'
    ) -> list[Path]:
        """
        Export a figure to multiple formats.
        
        Args:
            figure: The matplotlib figure to export
            base_path: Base path/name for output files (extension will be added)
            formats: List of format names ('png', 'svg', 'pdf')
            dpi: Resolution for raster formats
            page_size: Page size for PDF format
            
        Returns:
            List of paths to exported files
            
        Raises:
            ExportError: If any export fails
        """
        base_path = Path(base_path) if isinstance(base_path, str) else base_path
        stem = base_path.stem
        parent = base_path.parent
        
        # Standardize and validate formats
        valid_formats = {'png', 'svg', 'pdf'}
        formats = [fmt.lower().strip() for fmt in formats]
        invalid_formats = set(formats) - valid_formats
        if invalid_formats:
            raise ExportError(
                f"Invalid format(s): {', '.join(invalid_formats)}. "
                f"Supported formats: {', '.join(valid_formats)}"
            )
        
        # Export each format
        output_paths = []
        for fmt in formats:
            output_path = parent / f"{stem}.{fmt}"
            
            if fmt == 'png':
                self.export_png(figure, output_path, dpi)
            elif fmt == 'svg':
                self.export_svg(figure, output_path)
            elif fmt == 'pdf':
                self.export_pdf(figure, output_path, page_size)
                
            output_paths.append(output_path)
            
        return output_paths

