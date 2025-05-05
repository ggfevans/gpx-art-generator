"""
Tests for CLI commands.
"""

import os
import tempfile
import re
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from PIL import Image

from gpx_art.exporters import ExportError
from gpx_art.main import cli, convert, info, validate
from gpx_art.models import Route, RoutePoint, RouteSegment


@pytest.fixture
def runner():
    """Provide a CLI test runner."""
    return CliRunner()


@pytest.fixture
def valid_gpx_file():
    """Create a valid GPX file for testing."""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="gpx-art-test">
  <metadata>
    <name>Test Route</name>
  </metadata>
  <trk>
    <name>Test Track</name>
    <trkseg>
      <trkpt lat="37.7749" lon="-122.4194">
        <ele>10</ele>
        <time>2023-01-01T12:00:00Z</time>
      </trkpt>
      <trkpt lat="37.7750" lon="-122.4195">
        <ele>11</ele>
        <time>2023-01-01T12:01:00Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gpx") as temp:
        temp.write(content.encode())
        temp_path = temp.name

    yield temp_path
    
    # Cleanup after test
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def invalid_gpx_file():
    """Create an invalid GPX file for testing."""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="gpx-art-test">
  <metadata>
    <name>Invalid Route</name>
  </metadata>
  <trk>
    <name>Invalid Track
    <!-- Missing closing tag -->
    <trkseg>
      <trkpt lat="invalid" lon="-122.4194">
        <ele>10</ele>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gpx") as temp:
        temp.write(content.encode())
        temp_path = temp.name

    yield temp_path
    
    # Cleanup after test
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def empty_gpx_file():
    """Create an empty but valid GPX file for testing."""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="gpx-art-test">
  <metadata>
    <name>Empty Route</name>
  </metadata>
</gpx>
"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gpx") as temp:
        temp.write(content.encode())
        temp_path = temp.name

    yield temp_path
    
    # Cleanup after test
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def gpx_file_with_validation_issues():
    """Create a GPX file with validation issues for testing."""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="gpx-art-test">
  <metadata>
    <name>Issues Route</name>
  </metadata>
  <trk>
    <name>Problem Track</name>
    <trkseg>
      <!-- Single point segment - not enough for route -->
      <trkpt lat="37.7749" lon="-122.4194">
        <ele>10</ele>
        <time>2023-01-01T12:00:00Z</time>
      </trkpt>
    </trkseg>
    <trkseg>
      <!-- Out of order timestamps -->
      <trkpt lat="37.7750" lon="-122.4195">
        <ele>11</ele>
        <time>2023-01-01T12:02:00Z</time>
      </trkpt>
      <trkpt lat="37.7751" lon="-122.4196">
        <ele>12</ele>
        <time>2023-01-01T12:01:00Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gpx") as temp:
        temp.write(content.encode())
        temp_path = temp.name

    yield temp_path
    
    # Cleanup after test
    if os.path.exists(temp_path):
        os.unlink(temp_path)


# Tests for the info command

def test_info_valid_file(runner, valid_gpx_file):
    """Test info command with a valid GPX file."""
    result = runner.invoke(info, [valid_gpx_file])
    assert result.exit_code == 0
    
    # Check for expected sections in output
    assert "=== GPX File Information ===" in result.output
    assert "=== Route Statistics ===" in result.output
    assert "=== Route Structure ===" in result.output
    assert "=== Elevation Profile ===" in result.output
    assert "=== Geographic Bounds ===" in result.output
    
    # Check for expected data
    assert "Test Track" in result.output
    assert "Distance:" in result.output
    assert "km" in result.output
    assert "miles" in result.output
    assert "Segments: 1" in result.output
    assert "Points: 2" in result.output


def test_info_nonexistent_file(runner):
    """Test info command with a non-existent file."""
    result = runner.invoke(info, ["/nonexistent/path.gpx"])
    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "File not found" in result.output


def test_info_invalid_file(runner, invalid_gpx_file):
    """Test info command with an invalid GPX file."""
    result = runner.invoke(info, [invalid_gpx_file])
    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "Error parsing GPX file" in result.output


def test_info_empty_file(runner, empty_gpx_file):
    """Test info command with an empty but valid GPX file."""
    result = runner.invoke(info, [empty_gpx_file])
    assert result.exit_code == 0
    assert "Unnamed route" in result.output
    assert "Segments: 0" in result.output
    assert "Points: 0" in result.output
    assert "Distance: 0.00 km (0.00 miles)" in result.output


# Tests for the validate command

def test_validate_valid_file(runner, valid_gpx_file):
    """Test validate command with a valid GPX file."""
    result = runner.invoke(validate, [valid_gpx_file])
    assert result.exit_code == 0
    assert "GPX file is valid" in result.output
    assert "No issues found" in result.output


def test_validate_nonexistent_file(runner):
    """Test validate command with a non-existent file."""
    result = runner.invoke(validate, ["/nonexistent/path.gpx"])
    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "File not found" in result.output


def test_validate_invalid_file(runner, invalid_gpx_file):
    """Test validate command with an invalid GPX file."""
    result = runner.invoke(validate, [invalid_gpx_file])
    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "Error parsing GPX file" in result.output


def test_validate_file_with_issues(runner, gpx_file_with_validation_issues):
    """Test validate command with a file that has validation issues."""
    result = runner.invoke(validate, [gpx_file_with_validation_issues])
    assert result.exit_code == 1
    assert "Found" in result.output
    assert "issues" in result.output
    
    # Check for specific issues
    assert "Segment Issues:" in result.output
    assert "only one point" in result.output
    
    assert "Timestamp Issues:" in result.output
    assert "out-of-order timestamps" in result.output


def test_validate_empty_file(runner, empty_gpx_file):
    """Test validate command with an empty but valid GPX file."""
    result = runner.invoke(validate, [empty_gpx_file])
    assert result.exit_code == 1  # Should fail with "no segments" issue
    assert "Route has no segments" in result.output


# Tests for the convert command

def test_convert_invalid_extension(runner, valid_gpx_file):
    """Test convert command with invalid output file extension."""
    # Use .jpg extension which is not supported
    result = runner.invoke(convert, [valid_gpx_file, "output.jpg"])
    assert result.exit_code == 1
    assert "Error: Output file must have .png extension" in result.output


def test_convert_nonexistent_file(runner, tmp_path):
    """Test convert command with non-existent input file."""
    output_file = str(tmp_path / "output.png")
    result = runner.invoke(convert, ["/nonexistent/path.gpx", output_file])
    assert result.exit_code == 2  # Click path validation error
    assert "does not exist" in result.output


def test_convert_invalid_file(runner, invalid_gpx_file, tmp_path):
    """Test convert command with invalid GPX file."""
    output_file = str(tmp_path / "output.png")
    result = runner.invoke(convert, [invalid_gpx_file, output_file])
    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "Error parsing GPX file" in result.output


@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Requires graphical libraries")
def test_convert_success(runner, valid_gpx_file, tmp_path):
    """Test successful conversion with default options."""
    output_file = str(tmp_path / "output.png")
    
    # Run the command
    result = runner.invoke(convert, [valid_gpx_file, output_file])
    
    # Check command result
    assert result.exit_code == 0
    assert "Parsing GPX file..." in result.output
    assert "Rendering route..." in result.output
    assert "Exporting PNG..." in result.output
    assert "Conversion complete" in result.output
    
    # Check that file was created
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0
    
    # Verify it's a valid PNG
    try:
        img = Image.open(output_file)
        assert img.format == "PNG"
        img.close()
    except Exception as e:
        pytest.fail(f"Failed to open output as PNG: {e}")


@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Requires graphical libraries")
def test_convert_with_options(runner, valid_gpx_file, tmp_path):
    """Test conversion with custom options."""
    output_file = str(tmp_path / "output.png")
    
    # Run with custom options
    result = runner.invoke(convert, [
        valid_gpx_file,
        output_file,
        "--color", "#FF0000",
        "--thickness", "thick",
        "--dpi", "150"
    ])
    
    # Check command result
    assert result.exit_code == 0
    assert "Conversion complete" in result.output
    assert "Resolution: 150 DPI" in result.output
    
    # Check that file was created
    assert os.path.exists(output_file)


@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Requires graphical libraries")
def test_convert_different_dpi(runner, valid_gpx_file, tmp_path):
    """Test that different DPI settings produce different file sizes."""
    low_dpi_file = str(tmp_path / "low_dpi.png")
    high_dpi_file = str(tmp_path / "high_dpi.png")
    
    # Create files with different DPI
    runner.invoke(convert, [valid_gpx_file, low_dpi_file, "--dpi", "72"])
    runner.invoke(convert, [valid_gpx_file, high_dpi_file, "--dpi", "300"])
    
    # Higher DPI should result in larger file
    low_size = os.path.getsize(low_dpi_file)
    high_size = os.path.getsize(high_dpi_file)
    assert high_size > low_size


def test_convert_export_error(runner, valid_gpx_file, tmp_path):
    """Test handling of export errors."""
    output_file = str(tmp_path / "output.png")
    
    # Mock the export_png method to raise an error
    with patch('gpx_art.exporters.Exporter.export_png', 
              side_effect=ExportError("Mock export error")):
        result = runner.invoke(convert, [valid_gpx_file, output_file])
        
        # Check error handling
        assert result.exit_code == 1
        assert "Error: Mock export error" in result.output
        
        # File should not exist
        assert not os.path.exists(output_file)


def test_convert_progress_messages(runner, valid_gpx_file, tmp_path):
    """Test progress messages during conversion."""
    output_file = str(tmp_path / "output.png")
    
    # Mock the export to avoid actual file creation
    with patch('gpx_art.exporters.Exporter.export_png'):
        result = runner.invoke(convert, [valid_gpx_file, output_file])
        
        # Check specific progress messages
        assert "Parsing GPX file..." in result.output
        assert "Rendering route..." in result.output
        assert "Exporting PNG..." in result.output
        
        # Order of messages should be correct
        parse_pos = result.output.find("Parsing")
        render_pos = result.output.find("Rendering")
        export_pos = result.output.find("Exporting")
        
        assert parse_pos < render_pos < export_pos

