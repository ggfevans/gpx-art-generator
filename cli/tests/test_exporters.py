"""
Tests for the exporter functionality.
"""

import os
import stat
import pytest
import matplotlib.pyplot as plt
from pathlib import Path
from unittest.mock import patch

from matplotlib.figure import Figure

from gpx_art.exporters import Exporter, ExportError


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

