"""
Tests for CLI commands.
"""

import os
import tempfile
from datetime import datetime, timedelta

import pytest
from click.testing import CliRunner

from gpx_art.main import cli, info, validate
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

