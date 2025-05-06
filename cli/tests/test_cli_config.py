"""Tests for configuration integration with CLI."""

import os
import yaml
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from pathlib import Path

from gpx_art.main import cli, get_config, get_effective_options
from gpx_art.config import Config, ConfigError


@pytest.fixture
def runner():
    """Fixture providing a CLI test runner."""
    return CliRunner()


@pytest.fixture
def minimal_gpx_content():
    """Minimal valid GPX content for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Test">
<trk>
<trkseg>
<trkpt lat="47.644548" lon="-122.326897">
<ele>4.46</ele><time>2009-10-17T18:37:26Z</time>
</trkpt>
<trkpt lat="47.644548" lon="-122.326697">
<ele>4.94</ele><time>2009-10-17T18:37:31Z</time>
</trkpt>
</trkseg>
</trk>
</gpx>"""


@pytest.fixture
def valid_config_file(tmp_path):
    """Create a valid configuration file for testing."""
    config_path = tmp_path / "config.yml"
    config_data = {
        "defaults": {
            "thickness": "thick",
            "color": "#FF5500",
            "style": "dashed",
            "markers": {
                "enabled": True,
                "unit": "km",
                "interval": 2.0
            },
            "overlay": {
                "enabled": True,
                "fields": ["distance", "elevation"],
                "position": "bottom-right"
            },
            "export": {
                "formats": ["png", "svg"],
                "width": 12,
                "height": 8,
                "dpi": 300
            }
        }
    }
    
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    
    return str(config_path)


@pytest.fixture
def invalid_config_file(tmp_path):
    """Create an invalid configuration file for testing."""
    config_path = tmp_path / "invalid_config.yml"
    config_data = {
        "defaults": {
            "thickness": "super-thick",  # Invalid value
            "markers": {
                "unit": "meters"  # Invalid value
            }
        }
    }
    
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    
    return str(config_path)


@pytest.fixture
def malformed_config_file(tmp_path):
    """Create a malformed YAML file for testing."""
    config_path = tmp_path / "malformed.yml"
    with open(config_path, "w") as f:
        f.write("defaults:\n  thickness: thick\n  color: '#FF5500'\n  style: 'solid'\n  :")  # Invalid YAML
    
    return str(config_path)


@pytest.fixture
def mock_config():
    """Mock Config class for testing."""
    with patch('gpx_art.main._config', None):
        # Reset the global config
        yield


@pytest.fixture
def mock_gpx_parser():
    """Mock GPXParser for testing."""
    with patch('gpx_art.main.GPXParser') as MockParser:
        parser_instance = MagicMock()
        MockParser.return_value = parser_instance
        
        # Set up the mock parser to return a valid route
        parser_instance.parse.return_value = True
        route_mock = MagicMock()
        parser_instance.to_route.return_value = route_mock
        
        # Set up the route to have segments
        route_mock.segments = [MagicMock()]
        
        yield MockParser


@pytest.fixture
def mock_visualizer():
    """Mock RouteVisualizer for testing."""
    with patch('gpx_art.main.RouteVisualizer') as MockVisualizer:
        visualizer_instance = MagicMock()
        MockVisualizer.return_value = visualizer_instance
        
        yield MockVisualizer


@pytest.fixture
def mock_exporter():
    """Mock Exporter for testing."""
    with patch('gpx_art.main.Exporter') as MockExporter:
        exporter_instance = MagicMock()
        MockExporter.return_value = exporter_instance
        
        yield MockExporter


class TestConfigLoading:
    """Tests for config file loading in the CLI."""
    
    def test_global_config_option(self, runner, valid_config_file, mock_config):
        """Test that the --config option works at the global level."""
        with patch('gpx_art.main.get_config') as mock_get_config:
            result = runner.invoke(cli, ["--config", valid_config_file, "--help"])
            
            assert result.exit_code == 0
            mock_get_config.assert_called_once_with(valid_config_file)
    
    def test_nonexistent_config_file(self, runner, mock_config):
        """Test behavior with non-existent config file."""
        result = runner.invoke(cli, ["--config", "/nonexistent/config.yml", "--help"])
        
        assert result.exit_code == 1
        assert "Error loading configuration" in result.output
    
    def test_invalid_config_file(self, runner, invalid_config_file, mock_config):
        """Test behavior with invalid config file."""
        result = runner.invoke(cli, ["--config", invalid_config_file, "--help"])
        
        assert result.exit_code == 1
        assert "Error loading configuration" in result.output
        assert "Invalid thickness" in result.output
    
    def test_malformed_config_file(self, runner, malformed_config_file, mock_config):
        """Test behavior with malformed YAML config file."""
        result = runner.invoke(cli, ["--config", malformed_config_file, "--help"])
        
        assert result.exit_code == 1
        assert "Error loading configuration" in result.output
        assert "Error parsing config file" in result.output


class TestEffectiveOptions:
    """Tests for resolving config values with CLI options."""
    
    def test_get_config_function(self, mock_config):
        """Test the get_config function."""
        # First call creates a new config
        config1 = get_config()
        assert config1 is not None
        
        # Second call returns the same instance
        config2 = get_config()
        assert config2 is config1
        
        # Call with path creates a new config
        config3 = get_config("some/path")
        assert config3 is not config1
    
    def test_config_defaults_used(self):
        """Test that config default values are used correctly."""
        # Mock the Config class to return known defaults
        mock_config = MagicMock()
        mock_config.get_defaults.return_value = {
            "thickness": "thick",
            "color": "#FF5500",
            "markers": {
                "enabled": True,
                "unit": "km"
            },
            "export": {
                "formats": ["png", "svg"]
            }
        }
        mock_config.get.side_effect = lambda key, default=None: {
            "defaults.thickness": "thick",
            "defaults.color": "#FF5500",
            "defaults.markers.enabled": True,
            "defaults.markers.unit": "km",
            "defaults.export.formats": ["png", "svg"]
        }.get(key, default)
        
        with patch('gpx_art.main.get_config', return_value=mock_config):
            options = get_effective_options(None, {
                "color": None,
                "thickness": None,
                "formats": None,
                "markers": None,
                "markers_unit": None
            })
            
            # Check that config values are used
            assert options["color"] == "#FF5500"
            assert options["thickness"] == "thick"
            assert options["formats"] == "png,svg"
            assert options["markers"] is True
            assert options["markers_unit"] == "km"
    
    def test_cli_overrides_config(self):
        """Test that CLI options override config values."""
        # Mock the Config class to return known defaults
        mock_config = MagicMock()
        mock_config.get_defaults.return_value = {
            "thickness": "thick",
            "color": "#FF5500"
        }
        mock_config.get.side_effect = lambda key, default=None: {
            "defaults.thickness": "thick",
            "defaults.color": "#FF5500"
        }.get(key, default)
        
        with patch('gpx_art.main.get_config', return_value=mock_config):
            options = get_effective_options(None, {
                "color": "#0000FF",  # CLI override
                "thickness": None    # Use config default
            })
            
            # Check that CLI value overrides config for color
            assert options["color"] == "#0000FF"
            # But thickness still comes from config
            assert options["thickness"] == "thick"
    
    def test_overlay_fields_conversion(self):
        """Test that overlay fields list is converted to comma-separated string."""
        mock_config = MagicMock()
        mock_config.get_defaults.return_value = {}
        mock_config.get.side_effect = lambda key, default=None: {
            "defaults.overlay.fields": ["distance", "elevation", "name"]
        }.get(key, default)
        
        with patch('gpx_art.main.get_config', return_value=mock_config):
            options = get_effective_options(None, {
                "overlay": None  # Use config default
            })
            
            # Check that list is converted to comma-separated string
            assert options["overlay"] == "distance,elevation,name"
    
    def test_formats_conversion(self):
        """Test that export formats list is converted to comma-separated string."""
        mock_config = MagicMock()
        mock_config.get_defaults.return_value = {}
        mock_config.get.side_effect = lambda key, default=None: {
            "defaults.export.formats": ["png", "svg", "pdf"]
        }.get(key, default)
        
        with patch('gpx_art.main.get_config', return_value=mock_config):
            options = get_effective_options(None, {
                "formats": None  # Use config default
            })
            
            # Check that list is converted to comma-separated string
            assert options["formats"] == "png,svg,pdf"


class TestConvertCommand:
    """Tests for the convert command with configuration."""
    
    def test_convert_uses_config_defaults(self, runner, tmp_path, mock_gpx_parser, 
                                         mock_visualizer, mock_exporter, minimal_gpx_content):
        """Test that convert command uses config defaults when no CLI options provided."""
        # Create a minimal GPX file
        gpx_file = tmp_path / "test.gpx"
        gpx_file.write_text(minimal_gpx_content)
        
        # Create a config file
        config_file = tmp_path / "config.yml"
        config_data = {
            "defaults": {
                "thickness": "thick",
                "color": "#FF5500",
                "style": "dashed",
                "markers": {"enabled": True, "unit": "km"},
                "export": {"formats": ["png", "svg"]}
            }
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        
        # Mock the Config class
        mock_config = MagicMock()
        mock_config.get_defaults.return_value = config_data["defaults"]
        mock_config.get.side_effect = lambda key, default=None: {
            "defaults.thickness": "thick",
            "defaults.color": "#FF5500",
            "defaults.style": "dashed",
            "defaults.markers.enabled": True,
            "defaults.markers.unit": "km",
            "defaults.export.formats": ["png", "svg"]
        }.get(key, default)
        
        with patch('gpx_art.main.get_config', return_value=mock_config):
            output_path = tmp_path / "output"
            result = runner.invoke(cli, [
                "--config", str(config_file),
                "convert", str(gpx_file), str(output_path)
            ])
            
            # Check if visualizer was called with config values
            visualizer_instance = mock_visualizer.return_value
            visualizer_instance.render_route.assert_called_once()
            # Check color argument
            args, kwargs = visualizer_instance.render_route.call_args
            assert kwargs["color"] == "#FF5500"
            assert kwargs["thickness"] == "thick"
            assert kwargs["line_style"] == "dashed"
            
            # Check exporter was called with formats from config
            exporter_instance = mock_exporter.return_value
            assert exporter_instance.export_multiple.called
    
    def test_convert_cli_overrides_config(self, runner, tmp_path, mock_gpx_parser, 
                                         mock_visualizer, mock_exporter, minimal_gpx_content):
        """Test that CLI options override config values in convert command."""
        # Create a minimal GPX file
        gpx_file = tmp_path / "test.gpx"
        gpx_file.write_text(minimal_gpx_content)
        
        # Create a config file
        config_file = tmp_path / "config.yml"
        config_data = {
            "defaults": {
                "thickness": "thick",
                "color": "#FF5500",
                "style": "dashed"
            }
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        
        # Mock the Config class
        mock_config = MagicMock()
        mock_config.get_defaults.return_value = config_data["defaults"]
        mock_config.get.side_effect = lambda key, default=None: {
            "defaults.thickness": "thick",
            "defaults.color": "#FF5500",
            "defaults.style": "dashed"
        }.get(key, default)
        
        with patch('gpx_art.main.get_config', return_value=mock_config):
            output_path = tmp_path / "output"
            result = runner.invoke(cli, [
                "--config", str(config_file),
                "convert", str(gpx_file), str(output_path),
                "--color", "#0000FF",  # CLI override
                "--thickness", "thin"   # CLI override
            ])
            
            # Check if visualizer was called with CLI values, not config values
            visualizer_instance = mock_visualizer.return_value
            visualizer_instance.render_route.assert_called_once()
            args, kwargs = visualizer_instance.render_route.call_args
            assert kwargs["color"] == "#0000FF"  # CLI override
            assert kwargs["thickness"] == "thin"  # CLI override
            assert kwargs["line_style"] == "dashed"  # From config (not overridden)

