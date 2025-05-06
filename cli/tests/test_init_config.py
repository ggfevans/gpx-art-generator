"""Tests for the init-config command."""

import os
import yaml
import pytest
from unittest.mock import patch, mock_open, MagicMock
from click.testing import CliRunner
from pathlib import Path

from gpx_art.main import cli, init_config
from gpx_art.config import Config


@pytest.fixture
def runner():
    """Fixture providing a CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_empty_config_file(tmp_path):
    """Create a temporary empty config file."""
    config_path = tmp_path / "empty_config.yml"
    with open(config_path, "w") as f:
        f.write("")
    return str(config_path)


@pytest.fixture
def mock_existing_config_file(tmp_path):
    """Create a temporary existing config file with content."""
    config_path = tmp_path / "existing_config.yml"
    with open(config_path, "w") as f:
        f.write("defaults:\n  thickness: thin\n  color: '#FF0000'\n")
    return str(config_path)


class TestInitConfig:
    """Tests for the init-config command."""

    def test_generate_default_config(self, runner, tmp_path):
        """Test generating a config file at the default location."""
        # Mock the default path to be in our temporary directory
        default_path = os.path.join(str(tmp_path), ".gpx-art/config.yml")
        
        with patch('gpx_art.config.Config.get_default_path', return_value=default_path):
            # Ensure the directory doesn't exist yet
            config_dir = os.path.dirname(default_path)
            if os.path.exists(config_dir):
                os.rmdir(config_dir)
            
            # Run the command
            result = runner.invoke(cli, ["init-config"])
            
            # Check output
            assert result.exit_code == 0
            assert "Config file created" in result.output
            assert default_path in result.output
            
            # Verify file was created
            assert os.path.exists(default_path)
            
            # Verify content is valid YAML and has expected structure
            with open(default_path, "r") as f:
                config = yaml.safe_load(f)
                assert "defaults" in config
                assert "thickness" in config["defaults"]
                assert "color" in config["defaults"]
                assert "markers" in config["defaults"]
                assert "overlay" in config["defaults"]
                assert "export" in config["defaults"]
    
    def test_generate_custom_path_config(self, runner, tmp_path):
        """Test generating a config file at a custom path."""
        custom_path = os.path.join(str(tmp_path), "custom_config.yml")
        
        # Run the command with a custom path
        result = runner.invoke(cli, ["init-config", "--path", custom_path])
        
        # Check output
        assert result.exit_code == 0
        assert "Config file created" in result.output
        assert custom_path in result.output
        
        # Verify file was created
        assert os.path.exists(custom_path)
        
        # Verify content is valid YAML and has expected structure
        with open(custom_path, "r") as f:
            config = yaml.safe_load(f)
            assert "defaults" in config
            assert isinstance(config["defaults"], dict)
    
    def test_directory_creation(self, runner, tmp_path):
        """Test that directories are created if they don't exist."""
        # Create a path with nested directories that don't exist yet
        nested_path = os.path.join(str(tmp_path), "level1/level2/config.yml")
        
        # Run the command
        result = runner.invoke(cli, ["init-config", "--path", nested_path])
        
        # Check output
        assert result.exit_code == 0
        assert "Created directory" in result.output
        assert "Config file created" in result.output
        
        # Verify directories and file were created
        assert os.path.exists(nested_path)
    
    def test_refuse_overwrite_existing(self, runner, mock_existing_config_file):
        """Test that existing config files are not overwritten without force flag."""
        # Run the command without --force
        result = runner.invoke(cli, ["init-config", "--path", mock_existing_config_file])
        
        # Check that operation was refused
        assert result.exit_code == 1
        assert "Config file already exists" in result.output
        assert "Use --force to overwrite" in result.output
        
        # Verify original content is preserved
        with open(mock_existing_config_file, "r") as f:
            content = f.read()
            assert "thickness: thin" in content
            assert "#FF0000" in content
    
    def test_force_overwrite_existing(self, runner, mock_existing_config_file):
        """Test that existing config files are overwritten with force flag."""
        # Run the command with --force
        result = runner.invoke(cli, ["init-config", "--path", mock_existing_config_file, "--force"])
        
        # Check that operation succeeded
        assert result.exit_code == 0
        assert "Config file created" in result.output
        
        # Verify content was replaced
        with open(mock_existing_config_file, "r") as f:
            config = yaml.safe_load(f)
            assert config["defaults"]["thickness"] == "medium"  # Default value, not "thin"
    
    def test_permission_error(self, runner, tmp_path):
        """Test handling of permission errors when writing the file."""
        test_path = os.path.join(str(tmp_path), "protected.yml")
        
        # Mock open to raise a permission error
        m = mock_open()
        m.side_effect = PermissionError("Permission denied")
        
        with patch('builtins.open', m):
            result = runner.invoke(cli, ["init-config", "--path", test_path])
            
            # Check that error was reported
            assert result.exit_code == 1
            assert "Error writing config file" in result.output
            assert "Permission denied" in result.output
    
    def test_directory_creation_failure(self, runner, tmp_path):
        """Test handling of directory creation failures."""
        test_path = os.path.join(str(tmp_path), "impossible/dir/config.yml")
        
        # Mock os.makedirs to raise an error
        with patch('os.makedirs', side_effect=OSError("Failed to create directory")):
            result = runner.invoke(cli, ["init-config", "--path", test_path])
            
            # Check that error was reported
            assert result.exit_code == 1
            assert "Error creating directory" in result.output
            assert "Failed to create directory" in result.output
    
    def test_config_content_validity(self, runner, tmp_path):
        """Test that generated config content is valid and contains all required sections."""
        output_path = os.path.join(str(tmp_path), "config_content_test.yml")
        
        # Run the command
        result = runner.invoke(cli, ["init-config", "--path", output_path])
        
        # Check that operation succeeded
        assert result.exit_code == 0
        
        # Load the config and verify structure
        with open(output_path, "r") as f:
            config = yaml.safe_load(f)
            
            # Check top level structure
            assert "defaults" in config
            defaults = config["defaults"]
            
            # Check basic settings
            assert "thickness" in defaults
            assert defaults["thickness"] in ["thin", "medium", "thick"]
            assert "color" in defaults
            assert "style" in defaults
            assert defaults["style"] in ["solid", "dashed"]
            
            # Check nested sections
            assert "markers" in defaults
            markers = defaults["markers"]
            assert "enabled" in markers
            assert isinstance(markers["enabled"], bool)
            assert "unit" in markers
            assert markers["unit"] in ["miles", "km"]
            
            assert "overlay" in defaults
            overlay = defaults["overlay"]
            assert "enabled" in overlay
            assert isinstance(overlay["enabled"], bool)
            assert "fields" in overlay
            assert isinstance(overlay["fields"], list)
            
            assert "export" in defaults
            export = defaults["export"]
            assert "formats" in export
            assert isinstance(export["formats"], list)
            assert all(fmt in ["png", "svg", "pdf"] for fmt in export["formats"])
            assert "width" in export
            assert isinstance(export["width"], (int, float))
            assert "height" in export
            assert isinstance(export["height"], (int, float))
            assert "dpi" in export
            assert isinstance(export["dpi"], int)

