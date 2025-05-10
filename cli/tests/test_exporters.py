"""
Tests for the exporter functionality.
"""

import os
import stat
import re
import xml.etree.ElementTree as ET
import pytest
import matplotlib.pyplot as plt
from pathlib import Path
from unittest.mock import patch

from matplotlib.figure import Figure
import PyPDF2

from route_to_art.exporters import Exporter, ExportError, ExportFormat, PageSize


@pytest.fixture
def test_figure():
    """Create a simple matplotlib figure for testing."""
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    ax.plot([1, 2, 3], [1, 2, 3])
    return fig


@pytest.fixture
def exporter():
    """Create an exporter instance."""
    return Exporter()


def test_export_png_success(exporter, test_figure, tmp_path):
    """Test successful PNG export."""
    output_path = tmp_path / "output.png"
    
    # Export the figure
    exporter.export_png(test_figure, output_path)
    
    # Check that the file exists
    assert output_path.exists()
    
    # Check that the file has content
    assert output_path.stat().st_size > 0


def test_export_png_with_custom_dpi(exporter, test_figure, tmp_path):
    """Test PNG export with custom DPI."""
    output_path = tmp_path / "output.png"
    
    # Export the figure with high DPI
    high_dpi = 600
    exporter.export_png(test_figure, output_path, dpi=high_dpi)
    
    # Check that the file exists
    assert output_path.exists()
    
    # Get file size with high DPI
    high_dpi_size = output_path.stat().st_size
    
    # Export with low DPI
    low_dpi = 72
    exporter.export_png(test_figure, output_path, dpi=low_dpi)
    
    # Get file size with low DPI
    low_dpi_size = output_path.stat().st_size
    
    # Higher DPI should result in larger file size
    assert high_dpi_size > low_dpi_size


def test_export_png_invalid_directory(exporter, test_figure, tmp_path):
    """Test export to non-existent directory."""
    # Path to non-existent directory
    output_path = tmp_path / "nonexistent" / "output.png"
    
    # Export should fail with ExportError
    with pytest.raises(ExportError) as exc_info:
        exporter.export_png(test_figure, output_path)
    
    # Check error message
    assert "directory does not exist" in str(exc_info.value)


def test_export_png_invalid_extension(exporter, test_figure, tmp_path):
    """Test export with invalid extension."""
    # Path with wrong extension
    output_path = tmp_path / "output.jpg"
    
    # Export should fail with ExportError
    with pytest.raises(ExportError) as exc_info:
        exporter.export_png(test_figure, output_path)
    
    # Check error message
    assert "extension" in str(exc_info.value)
    assert "png" in str(exc_info.value)


@pytest.mark.skipif(os.name == 'nt', reason="Permission tests unreliable on Windows")
def test_export_png_permission_error(exporter, test_figure, tmp_path):
    """Test export to directory without write permission."""
    # Create a subdirectory
    subdir = tmp_path / "noperm"
    subdir.mkdir()
    
    # Remove write permission
    subdir.chmod(stat.S_IREAD | stat.S_IEXEC)
    
    try:
        # Attempt export
        output_path = subdir / "output.png"
        
        # Should fail with permission error
        with pytest.raises(ExportError) as exc_info:
            exporter.export_png(test_figure, output_path)
        
        # Check error message
        assert "not writable" in str(exc_info.value)
    finally:
        # Restore permissions for cleanup
        subdir.chmod(stat.S_IRWXU)


def test_export_png_overwrites_existing(exporter, test_figure, tmp_path):
    """Test that export overwrites existing files."""
    output_path = tmp_path / "output.png"
    
    # Create a dummy file
    with open(output_path, 'w') as f:
        f.write("dummy content")
    
    # Get initial size
    initial_size = output_path.stat().st_size
    
    # Export should overwrite
    exporter.export_png(test_figure, output_path)
    
    # Check that file exists and content changed
    assert output_path.exists()
    assert output_path.stat().st_size != initial_size


def test_export_png_savefig_error(exporter, test_figure, tmp_path):
    """Test error handling when matplotlib savefig fails."""
    output_path = tmp_path / "output.png"
    
    # Mock savefig to raise an exception
    with patch.object(Figure, 'savefig', side_effect=ValueError("Mock savefig error")):
        # Export should fail and wrap the error
        with pytest.raises(ExportError) as exc_info:
            exporter.export_png(test_figure, output_path)
        
        # Check error message
        assert "Failed to export PNG" in str(exc_info.value)
        assert "Mock savefig error" in str(exc_info.value)
    
    # Check that no file was created
    assert not output_path.exists()


@pytest.mark.skipif(os.name == 'nt', reason="File locking tests unreliable on Windows")
def test_export_png_cleanup_on_error(exporter, test_figure, tmp_path):
    """Test temporary file cleanup on error."""
    output_path = tmp_path / "output.png"
    
    # Create a patch that will succeed for the temporary file but fail
    # during verification to trigger cleanup
    original_verify = exporter._verify_output_file
    
    def mock_verify(path):
        # If this is the final verification, raise an error
        if str(path) == str(output_path):
            raise ValueError("Mock verification error")
        # Otherwise, proceed normally
        return original_verify(path)
    
    # Apply the patch
    with patch.object(exporter, '_verify_output_file', side_effect=mock_verify):
        # Export should fail
        with pytest.raises(ExportError):
            exporter.export_png(test_figure, output_path)
    
    # The output file shouldn't exist
    assert not output_path.exists()
    
    # Temp files should be cleaned up
    temp_files = list(tmp_path.glob("*.png"))
    assert len(temp_files) == 0


def test_exporter_input_string_path(exporter, test_figure, tmp_path):
    """Test that exporter accepts string paths."""
    output_path = str(tmp_path / "output.png")
    
    # Export should succeed with string path
    exporter.export_png(test_figure, output_path)
    
    # Check that file exists
    assert os.path.exists(output_path)


# Tests for SVG export

def is_valid_svg(file_path):
    """Check if a file is a valid SVG by attempting to parse it as XML."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        # Check for SVG namespace
        return 'svg' in root.tag.lower()
    except ET.ParseError:
        return False


def test_export_svg_success(exporter, test_figure, tmp_path):
    """Test successful SVG export."""
    output_path = tmp_path / "output.svg"
    
    # Export the figure
    exporter.export_svg(test_figure, output_path)
    
    # Check that the file exists
    assert output_path.exists()
    
    # Check that the file has content
    assert output_path.stat().st_size > 0
    
    # Verify it's a valid SVG file
    assert is_valid_svg(output_path)


def test_export_svg_invalid_extension(exporter, test_figure, tmp_path):
    """Test export_svg with wrong file extension."""
    output_path = tmp_path / "output.png"  # Should be .svg
    
    with pytest.raises(ExportError) as exc_info:
        exporter.export_svg(test_figure, output_path)
    
    assert "extension" in str(exc_info.value)
    assert "svg" in str(exc_info.value)


def test_export_svg_vector_quality(exporter, test_figure, tmp_path):
    """Test that SVG export contains vector path elements."""
    output_path = tmp_path / "output.svg"
    
    # Export the figure
    exporter.export_svg(test_figure, output_path)
    
    # Read the SVG file
    with open(output_path, 'r') as f:
        svg_content = f.read()
    
    # Check for vector path elements (depends on matplotlib's SVG output)
    assert '<path' in svg_content.lower()
    
    # Should not contain bitmap image elements
    assert '<image' not in svg_content.lower()


# Tests for PDF export

def is_valid_pdf(file_path):
    """Check if a file is a valid PDF by attempting to open it with PyPDF2."""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return len(reader.pages) > 0
    except PyPDF2.errors.PdfReadError:
        return False


def test_export_pdf_success(exporter, test_figure, tmp_path):
    """Test successful PDF export."""
    output_path = tmp_path / "output.pdf"
    
    # Export the figure
    exporter.export_pdf(test_figure, output_path)
    
    # Check that the file exists
    assert output_path.exists()
    
    # Check that the file has content
    assert output_path.stat().st_size > 0
    
    # Verify it's a valid PDF file
    assert is_valid_pdf(output_path)


def test_export_pdf_page_sizes(exporter, test_figure, tmp_path):
    """Test PDF export with different page sizes."""
    # Test a few different page sizes
    page_sizes = ["letter", "a4", "square-medium", "landscape-medium"]
    
    for size in page_sizes:
        output_path = tmp_path / f"output_{size}.pdf"
        
        # Export with the specified page size
        exporter.export_pdf(test_figure, output_path, page_size=size)
        
        # Check that the file exists and is valid
        assert output_path.exists()
        assert is_valid_pdf(output_path)
        
        # Cannot easily check the actual dimensions without more complex PDF parsing


def test_export_pdf_invalid_page_size(exporter, test_figure, tmp_path):
    """Test PDF export with invalid page size."""
    output_path = tmp_path / "output.pdf"
    
    with pytest.raises(ExportError) as exc_info:
        exporter.export_pdf(test_figure, output_path, page_size="nonexistent-size")
    
    assert "Unknown page size" in str(exc_info.value)


def test_export_pdf_invalid_extension(exporter, test_figure, tmp_path):
    """Test export_pdf with wrong file extension."""
    output_path = tmp_path / "output.png"  # Should be .pdf
    
    with pytest.raises(ExportError) as exc_info:
        exporter.export_pdf(test_figure, output_path)
    
    assert "extension" in str(exc_info.value)
    assert "pdf" in str(exc_info.value)


# Tests for format detection and auto-export

def test_get_format(exporter):
    """Test format detection from file extension."""
    assert exporter.get_format("output.png") == ExportFormat.PNG
    assert exporter.get_format("output.svg") == ExportFormat.SVG
    assert exporter.get_format("output.pdf") == ExportFormat.PDF
    
    # Path objects should also work
    assert exporter.get_format(Path("output.png")) == ExportFormat.PNG
    
    # Case insensitivity
    assert exporter.get_format("OUTPUT.PNG") == ExportFormat.PNG
    
    # Invalid extension
    with pytest.raises(ExportError):
        exporter.get_format("output.jpg")


def test_export_auto_format(exporter, test_figure, tmp_path):
    """Test automatic format detection in export method."""
    # Test each format
    formats = [
        ("output.png", ExportFormat.PNG),
        ("output.svg", ExportFormat.SVG),
        ("output.pdf", ExportFormat.PDF)
    ]
    
    for filename, expected_format in formats:
        output_path = tmp_path / filename
        
        # Mock the specific export methods to verify they're called
        with patch.object(exporter, f'export_{expected_format.name.lower()}') as mock_export:
            exporter.export(test_figure, output_path)
            mock_export.assert_called_once()


# Tests for multiple format export

def test_export_multiple_formats(exporter, test_figure, tmp_path):
    """Test exporting to multiple formats."""
    base_path = tmp_path / "output"
    formats = ["png", "svg", "pdf"]
    
    # Export to all formats
    output_paths = exporter.export_multiple(
        figure=test_figure,
        base_path=base_path,
        formats=formats
    )
    
    # Should return the correct number of paths
    assert len(output_paths) == len(formats)
    
    # Each file should exist
    for path in output_paths:
        assert path.exists()
        assert path.stat().st_size > 0
    
    # Verify extensions
    extensions = [p.suffix.lower() for p in output_paths]
    assert ".png" in extensions
    assert ".svg" in extensions
    assert ".pdf" in extensions


def test_export_multiple_formats_validation(exporter, test_figure, tmp_path):
    """Test validation in multiple format export."""
    base_path = tmp_path / "output"
    
    # Test with invalid format
    with pytest.raises(ExportError) as exc_info:
        exporter.export_multiple(
            figure=test_figure,
            base_path=base_path,
            formats=["png", "invalid", "pdf"]
        )
    
    assert "Invalid format" in str(exc_info.value)
    
    # Test with empty format list
    with pytest.raises(ExportError) as exc_info:
        exporter.export_multiple(
            figure=test_figure,
            base_path=base_path,
            formats=[]
        )
    
    assert "Invalid format" in str(exc_info.value)


def test_export_multiple_formats_error_handling(exporter, test_figure, tmp_path):
    """Test error handling in multiple format export."""
    base_path = tmp_path / "output"
    
    # Create a directory with the same name as one of the output files to cause an error
    conflict_path = base_path.with_suffix(".svg")
    conflict_path.mkdir()
    
    # Should fail when trying to export to SVG
    with pytest.raises(ExportError):
        exporter.export_multiple(
            figure=test_figure,
            base_path=base_path,
            formats=["png", "svg", "pdf"]
        )
    
    # PNG should have been created before the error
    assert base_path.with_suffix(".png").exists()
    
    # PDF should not have been created after the error
    assert not base_path.with_suffix(".pdf").exists()

