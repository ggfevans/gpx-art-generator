"""
Tests for the Config class that manages configuration loading and validation.
"""

import os
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch

from route_to_art.config import Config, ConfigError


@pytest.fixture
def temp_config_dir(tmpdir):
    """Create a temporary directory for config files."""
    config_dir = tmpdir.mkdir("config")
    return config_dir


@pytest.fixture
def valid_config_file(temp_config_dir):
    """Create a valid configuration file for testing."""
    config_path = temp_config_dir.join("config.yml")
    config_data = {
        "defaults": {
            "thickness": "thick",
            "color": "#FF5500",
            "markers": {
                "unit": "km",
                "interval": 2.0
            },
            "overlay": {
                "fields": ["distance", "elevation"],
                "position": "bottom-right"
            },
            "export": {
                "formats": ["png", "svg"],
                "width": 12,
                "height": 8
            }
        }
    }
    
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    
    return str(config_path)


@pytest.fixture
def invalid_config_file(temp_config_dir):
    """Create an invalid configuration file for testing."""
    config_path = temp_config_dir.join("invalid_config.yml")
    config_data = {
        "defaults": {
            "thickness": "super-thick",  # Invalid value
            "markers": {
                "unit": "meters"  # Invalid value
            },
            "export": {
                "formats": ["jpeg"],  # Invalid value
                "width": -5  # Invalid negative value
            }
        }
    }
    
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    
    return str(config_path)


@pytest.fixture
def malformed_config_file(temp_config_dir):
    """Create a malformed YAML file for testing."""
    config_path = temp_config_dir.join("malformed.yml")
    with open(config_path, "w") as f:
        f.write("defaults:\n  thickness: thick\n  color: '#FF5500'\n  style: 'solid'\n  :")  # Invalid YAML
    
    return str(config_path)


class TestConfig:
    """Tests for the Config class."""
    
    def test_default_config(self):
        """Test that default configuration is used when no config file is provided."""
        # Create config with non-existent path to force using defaults
        config = Config(config_path="/non/existent/path.yml")
        
        # Verify defaults are used
        assert config.get("defaults.thickness") == "medium"
        assert config.get("defaults.color") == "#000000"
        assert config.get("defaults.style") == "solid"
        assert config.get("defaults.markers.enabled") is True
        assert config.get("defaults.markers.unit") == "miles"
        assert config.get("defaults.export.formats") == ["png"]
    
    def test_load_valid_config(self, valid_config_file):
        """Test loading a valid configuration file."""
        config = Config(config_path=valid_config_file)
        
        # Check that values from the config file are loaded
        assert config.get("defaults.thickness") == "thick"
        assert config.get("defaults.color") == "#FF5500"
        assert config.get("defaults.markers.unit") == "km"
        assert config.get("defaults.markers.interval") == 2.0
        assert config.get("defaults.overlay.fields") == ["distance", "elevation"]
        assert config.get("defaults.overlay.position") == "bottom-right"
        assert config.get("defaults.export.formats") == ["png", "svg"]
        assert config.get("defaults.export.width") == 12
        assert config.get("defaults.export.height") == 8
        
        # Check that defaults are preserved for values not in the config file
        assert config.get("defaults.style") == "solid"  # Default value
        assert config.get("defaults.markers.enabled") is True  # Default value
    
    def test_config_discovery(self, valid_config_file, monkeypatch):
        """Test configuration file discovery logic."""
        # Test discovery via environment variable
        monkeypatch.setenv("GPX_ART_CONFIG", valid_config_file)
        config = Config()
        assert config.get("defaults.thickness") == "thick"  # Value from our valid config
        
        # Test home directory discovery
        monkeypatch.delenv("GPX_ART_CONFIG")
        home_dir = os.path.expanduser("~")
        home_config_dir = os.path.join(home_dir, ".gpx-art")
        monkeypatch.setattr(os.path, "exists", lambda path: path == os.path.join(home_config_dir, "config.yml"))
        monkeypatch.setattr(Config, "load_config", lambda self: {"defaults": {"thickness": "thin"}})
        config = Config()
        
        # Check that the correct path is used
        assert config.get_default_path() == os.path.join(home_config_dir, "config.yml")
    
    def test_invalid_config(self, invalid_config_file):
        """Test validation of invalid configuration values."""
        # Test thickness validation
        with pytest.raises(ConfigError) as exc_info:
            Config(config_path=invalid_config_file)
        assert "Invalid thickness: super-thick" in str(exc_info.value)
        
        # Fix thickness and test next error (markers.unit)
        with open(invalid_config_file, "r") as f:
            config_data = yaml.safe_load(f)
        
        config_data["defaults"]["thickness"] = "thick"
        
        with open(invalid_config_file, "w") as f:
            yaml.dump(config_data, f)
        
        with pytest.raises(ConfigError) as exc_info:
            Config(config_path=invalid_config_file)
        assert "Invalid markers.unit: meters" in str(exc_info.value)
    
    def test_malformed_yaml(self, malformed_config_file):
        """Test handling of malformed YAML files."""
        with pytest.raises(ConfigError) as exc_info:
            Config(config_path=malformed_config_file)
        assert "Error parsing config file" in str(exc_info.value)
    
    def test_empty_config_file(self, temp_config_dir):
        """Test handling of empty configuration files."""
        empty_config_path = temp_config_dir.join("empty.yml")
        with open(empty_config_path, "w") as f:
            f.write("")
        
        # Should use defaults for empty file
        with patch("logging.warning") as mock_warning:
            config = Config(config_path=str(empty_config_path))
            mock_warning.assert_called_once()
            assert "empty" in mock_warning.call_args[0][0].lower()
        
        # Verify defaults are used
        assert config.get("defaults.thickness") == "medium"
    
    def test_non_dict_config(self, temp_config_dir):
        """Test handling of non-dictionary YAML files."""
        invalid_config_path = temp_config_dir.join("invalid_type.yml")
        with open(invalid_config_path, "w") as f:
            f.write("- item1\n- item2")  # YAML list instead of dict
        
        with pytest.raises(ConfigError) as exc_info:
            Config(config_path=str(invalid_config_path))
        assert "not a valid YAML dictionary" in str(exc_info.value)
    
    def test_merge_with_defaults(self):
        """Test merging user configuration with defaults."""
        user_config = {
            "defaults": {
                "thickness": "thick",
                "markers": {
                    "unit": "km",
                    "size": 10.0
                },
                "new_key": "value"
            }
        }
        
        config = Config()
        merged = config.merge_with_defaults(user_config)
        
        # Check that user values override defaults
        assert merged["defaults"]["thickness"] == "thick"
        assert merged["defaults"]["markers"]["unit"] == "km"
        assert merged["defaults"]["markers"]["size"] == 10.0
        
        # Check that new keys are added
        assert merged["defaults"]["new_key"] == "value"
        
        # Check that default values are preserved for keys not in user config
        assert merged["defaults"]["color"] == "#000000"
        assert merged["defaults"]["markers"]["enabled"] is True
        assert merged["defaults"]["markers"]["interval"] == 1.0
    
    def test_get_method(self, valid_config_file):
        """Test getting configuration values with dot notation."""
        config = Config(config_path=valid_config_file)
        
        # Test getting values with dot notation
        assert config.get("defaults.thickness") == "thick"
        assert config.get("defaults.markers.unit") == "km"
        
        # Test default value for non-existent keys
        assert config.get("non.existent.key") is None
        assert config.get("non.existent.key", "default") == "default"
    
    def test_get_defaults(self, valid_config_file):
        """Test getting the defaults section."""
        config = Config(config_path=valid_config_file)
        defaults = config.get_defaults()
        
        assert defaults["thickness"] == "thick"
        assert defaults["color"] == "#FF5500"
        assert defaults["markers"]["unit"] == "km"
    
    def test_generate_sample(self):
        """Test generating a sample configuration file."""
        config = Config()
        sample = config.generate_sample()
        
        # Verify that the sample can be parsed as YAML
        parsed = yaml.safe_load(sample)
        assert "defaults" in parsed
        assert "thickness" in parsed["defaults"]
        assert "color" in parsed["defaults"]
        assert "markers" in parsed["defaults"]
        assert "overlay" in parsed["defaults"]
        assert "export" in parsed["defaults"]

