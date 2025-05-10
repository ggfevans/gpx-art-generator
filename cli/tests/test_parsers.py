"""
Tests for the GPX parser functionality.
"""

import os
import tempfile
from pathlib import Path

import pytest

from route_to_art.parsers import GPXParser


@pytest.fixture
def valid_gpx_file():
    """Create a temporary file with valid GPX content for testing."""
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
    """Create a temporary file with invalid GPX content for testing."""
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
def non_gpx_file():
    """Create a temporary file with a non-GPX extension for testing."""
    content = "This is not a GPX file"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp:
        temp.write(content.encode())
        temp_path = temp.name

    yield temp_path
    
    # Cleanup after test
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_parse_valid_gpx(valid_gpx_file):
    """Test parsing a valid GPX file."""
    parser = GPXParser(valid_gpx_file)
    gpx = parser.parse()
    
    assert gpx is not None
    assert parser.is_valid()
    assert parser.get_error() is None
    assert gpx.tracks[0].name == "Test Track"
    assert len(gpx.tracks[0].segments[0].points) == 2


def test_parse_nonexistent_file():
    """Test parsing a non-existent file."""
    parser = GPXParser("/path/to/nonexistent/file.gpx")
    gpx = parser.parse()
    
    assert gpx is None
    assert not parser.is_valid()
    assert "File not found" in parser.get_error()


def test_parse_non_gpx_file(non_gpx_file):
    """Test parsing a file that doesn't have a .gpx extension."""
    parser = GPXParser(non_gpx_file)
    gpx = parser.parse()
    
    assert gpx is None
    assert not parser.is_valid()
    assert "not a GPX file" in parser.get_error()


def test_parse_invalid_gpx(invalid_gpx_file):
    """Test parsing an invalid GPX file."""
    parser = GPXParser(invalid_gpx_file)
    gpx = parser.parse()
    
    assert gpx is None
    assert not parser.is_valid()
    assert "Error parsing GPX file" in parser.get_error()


def test_is_valid_lazy_parsing(valid_gpx_file):
    """Test is_valid triggers parsing if not already done."""
    parser = GPXParser(valid_gpx_file)
    # We haven't called parse() yet
    assert parser.is_valid()  # Should trigger parsing
    assert parser._parsed  # Check that parsing was triggered


def test_get_error_lazy_parsing(invalid_gpx_file):
    """Test get_error triggers parsing if not already done."""
    parser = GPXParser(invalid_gpx_file)
    # We haven't called parse() yet
    error = parser.get_error()  # Should trigger parsing
    assert error is not None
    assert "Error parsing GPX file" in error
    assert parser._parsed  # Check that parsing was triggered

