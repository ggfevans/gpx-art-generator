"""
Configuration management for gpx-art.

Handles loading, validation, and access to configuration settings
from YAML files with support for defaults and overrides.
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import yaml


class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass


class Config:
    """
    Configuration manager for gpx-art.
    
    Handles loading configuration from YAML files, validation, and
    providing access to configuration values with appropriate defaults.
    """
    
    # Default configuration structure
    DEFAULT_CONFIG = {
        "defaults": {
            "thickness": "medium",
            "color": "#000000",
            "style": "solid",
            "markers": {
                "enabled": True,
                "unit": "miles",
                "interval": 1.0,
                "size": 6.0,
                "color": None,  # Use route color
                "label_font_size": 8
            },
            "overlay": {
                "enabled": True,
                "fields": ["distance", "date"],
                "position": "top-left",
                "font_size": 10,
                "font_color": "black",
                "background": True,
                "bg_color": "white",
                "bg_alpha": 0.7
            },
            "export": {
                "formats": ["png"],
                "width": 9,
                "height": 6,
                "dpi": 300,
                "page_size": "letter"
            }
        }
    }
    
    # Valid values for enum-like settings
    VALID_VALUES = {
        "thickness": ["thin", "medium", "thick"],
        "style": ["solid", "dashed"],
        "markers.unit": ["miles", "km"],
        "overlay.position": ["top-left", "top-right", "bottom-left", "bottom-right"],
        "overlay.fields": ["distance", "duration", "elevation", "name", "date"],
        "export.formats": ["png", "svg", "pdf"],
        "export.page_size": [
            "letter", "a4", 
            "square-small", "square-medium", "square-large",
            "landscape-small", "landscape-medium", "landscape-large"
        ]
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Optional explicit path to a configuration file.
                         If not provided, will search for config files in default locations.
        """
        self.config_path = config_path
        self.config = self.load_config()
    
    def get_default_path(self) -> str:
        """
        Get the default configuration file path.
        
        Checks multiple locations in order:
        1. GPX_ART_CONFIG environment variable
        2. ~/.gpx-art/config.yml in user's home directory
        3. ./gpx-art.yml in the current working directory
        
        Returns:
            Path to the default configuration file
        """
        # Check environment variable first
        if env_path := os.environ.get("GPX_ART_CONFIG"):
            return env_path
            
        # Check user home directory
        home_config = os.path.expanduser("~/.gpx-art/config.yml")
        if os.path.exists(home_config):
            return home_config
            
        # Check current directory
        cwd_config = "./gpx-art.yml"
        if os.path.exists(cwd_config):
            return cwd_config
            
        # Return default path for potential writing
        return home_config
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file, falling back to defaults when necessary.
        
        Returns:
            Dictionary containing the merged and validated configuration
            
        Raises:
            ConfigError: If configuration file exists but can't be loaded or contains invalid values
        """
        # Start with default configuration
        config = self._deep_copy(self.DEFAULT_CONFIG)
        
        # Determine config path
        path = self.config_path or self.get_default_path()
        
        # Try to load configuration file if it exists
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    
                if user_config is None:
                    # Empty file
                    logging.warning(f"Config file {path} is empty. Using defaults.")
                    return config
                    
                if not isinstance(user_config, dict):
                    raise ConfigError(f"Config file {path} is not a valid YAML dictionary.")
                    
                # Merge with defaults
                config = self.merge_with_defaults(user_config)
                
                # Validate configuration
                self._validate_config(config)
                    
            except yaml.YAMLError as e:
                raise ConfigError(f"Error parsing config file {path}: {str(e)}")
            except Exception as e:
                if isinstance(e, ConfigError):
                    raise
                raise ConfigError(f"Error loading config from {path}: {str(e)}")
        else:
            logging.info(f"No config file found at {path}. Using defaults.")
            
        return config
    
    def merge_with_defaults(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge user configuration with default values.
        
        Args:
            user_config: User-provided configuration dictionary
            
        Returns:
            Dictionary with user values merged into defaults
        """
        # Make a deep copy of defaults to avoid modifying the class constant
        result = self._deep_copy(self.DEFAULT_CONFIG)
        
        # Recursively merge user config into defaults
        self._merge_dicts(result, user_config)
        
        return result
    
    def _merge_dicts(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """
        Recursively merge dictionaries, modifying base in place.
        
        Args:
            base: Base dictionary to merge into
            override: Dictionary with values to override base
        """
        for key, value in override.items():
            # Handle nested dictionaries
            if (
                key in base and 
                isinstance(base[key], dict) and 
                isinstance(value, dict)
            ):
                self._merge_dicts(base[key], value)
            else:
                # Direct value assignment for non-dict values or mismatched types
                base[key] = value
    
    def _deep_copy(self, obj: Any) -> Any:
        """
        Create a deep copy of an object.
        
        Args:
            obj: Object to copy
            
        Returns:
            Deep copy of the object
        """
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            # For primitive values, return as is
            return obj
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration values.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ConfigError: If configuration contains invalid values
        """
        if "defaults" not in config:
            raise ConfigError("Configuration must contain a 'defaults' section")
            
        defaults = config["defaults"]
        
        # Check enum values
        self._validate_enum_value(defaults, "thickness")
        self._validate_enum_value(defaults, "style")
        
        # Check markers config
        if "markers" in defaults:
            markers = defaults["markers"]
            if not isinstance(markers, dict):
                raise ConfigError("markers must be a dictionary")
                
            if "enabled" in markers and not isinstance(markers["enabled"], bool):
                raise ConfigError("markers.enabled must be a boolean")
                
            self._validate_enum_value(markers, "unit", prefix="markers.")
            
            # Validate numeric values
            self._validate_positive_number(markers, "interval")
            self._validate_positive_number(markers, "size")
            self._validate_positive_int(markers, "label_font_size")
        
        # Check overlay config
        if "overlay" in defaults:
            overlay = defaults["overlay"]
            if not isinstance(overlay, dict):
                raise ConfigError("overlay must be a dictionary")
                
            if "enabled" in overlay and not isinstance(overlay["enabled"], bool):
                raise ConfigError("overlay.enabled must be a boolean")
                
            self._validate_enum_value(overlay, "position", prefix="overlay.")
            
            if "fields" in overlay:
                if not isinstance(overlay["fields"], list):
                    raise ConfigError("overlay.fields must be a list")
                    
                for field in overlay["fields"]:
                    if field not in self.VALID_VALUES["overlay.fields"]:
                        valid_values = ", ".join(self.VALID_VALUES["overlay.fields"])
                        raise ConfigError(f"Invalid overlay field: {field}. Valid values: {valid_values}")
                
            # Validate numeric and color values
            self._validate_positive_int(overlay, "font_size")
            
            if "background" in overlay and not isinstance(overlay["background"], bool):
                raise ConfigError("overlay.background must be a boolean")
                
            self._validate_float_range(overlay, "bg_alpha", 0.0, 1.0)
        
        # Check export config
        if "export" in defaults:
            export = defaults["export"]
            if not isinstance(export, dict):
                raise ConfigError("export must be a dictionary")
                
            if "formats" in export:
                if not isinstance(export["formats"], list):
                    raise ConfigError("export.formats must be a list")
                    
                for fmt in export["formats"]:
                    if fmt not in self.VALID_VALUES["export.formats"]:
                        valid_values = ", ".join(self.VALID_VALUES["export.formats"])
                        raise ConfigError(f"Invalid export format: {fmt}. Valid values: {valid_values}")
            
            # Validate numeric values
            self._validate_positive_number(export, "width")
            self._validate_positive_number(export, "height")
            self._validate_positive_int(export, "dpi")
            
            # Validate page size
            self._validate_enum_value(export, "page_size", prefix="export.")
    
    def _validate_enum_value(self, config: Dict[str, Any], key: str, prefix: str = "") -> None:
        """
        Validate that a value is one of the allowed enum values.
        
        Args:
            config: Configuration dictionary
            key: Key to validate
            prefix: Optional prefix for error messages and valid values lookup
            
        Raises:
            ConfigError: If value is not in the allowed set
        """
        full_key = f"{prefix}{key}"
        if key in config and full_key in self.VALID_VALUES:
            value = config[key]
            valid_values = self.VALID_VALUES[full_key]
            if value not in valid_values:
                valid_options = ", ".join(valid_values)
                raise ConfigError(f"Invalid {full_key}: {value}. Valid options: {valid_options}")
    
    def _validate_positive_number(self, config: Dict[str, Any], key: str) -> None:
        """
        Validate that a value is a positive number.
        
        Args:
            config: Configuration dictionary
            key: Key to validate
            
        Raises:
            ConfigError: If value is not a positive number
        """
        if key in config:
            value = config[key]
            if not isinstance(value, (int, float)):
                raise ConfigError(f"{key} must be a number")
                
            if value <= 0:
                raise ConfigError(f"{key} must be positive")
    
    def _validate_positive_int(self, config: Dict[str, Any], key: str) -> None:
        """
        Validate that a value is a positive integer.
        
        Args:
            config: Configuration dictionary
            key: Key to validate
            
        Raises:
            ConfigError: If value is not a positive integer
        """
        if key in config:
            value = config[key]
            if not isinstance(value, int):
                raise ConfigError(f"{key} must be an integer")
                
            if value <= 0:
                raise ConfigError(f"{key} must be positive")
    
    def _validate_float_range(self, config: Dict[str, Any], key: str, min_val: float, max_val: float) -> None:
        """
        Validate that a value is a float within the specified range.
        
        Args:
            config: Configuration dictionary
            key: Key to validate
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)
            
        Raises:
            ConfigError: If value is not in the allowed range
        """
        if key in config:
            value = config[key]
            if not isinstance(value, (int, float)):
                raise ConfigError(f"{key} must be a number")
                
            if value < min_val or value > max_val:
                raise ConfigError(f"{key} must be between {min_val} and {max_val}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by its key.
        
        Supports dot notation for nested values (e.g., 'defaults.export.formats').
        
        Args:
            key: Configuration key to retrieve
            default: Default value to return if key is not found
            
        Returns:
            Configuration value or default if not found
        """
        # Start with the full config
        current = self.config
        
        # Split the key path
        parts = key.split('.')
        
        # Navigate through the path
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def get_defaults(self) -> Dict[str, Any]:
        """
        Get the defaults section of the configuration.
        
        Returns:
            Dictionary containing default values
        """
        return self.config.get("defaults", {})
    
    def generate_sample(self) -> str:
        """
        Generate a sample configuration file content.
        
        Returns:
            YAML string with sample configuration
        """
        return yaml.dump(self.DEFAULT_CONFIG, sort_keys=False, default_flow_style=False)

"""
Configuration management for the gpx-art tool.

This module handles loading, validation, and merging of configuration
from YAML files, with support for defaults and overrides.
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml


class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass


class Config:
    """
    Configuration manager for the gpx-art tool.
    
    Handles loading configuration from YAML files, discovering configuration
    locations, and merging with default values.
    """
    
    # Default configuration structure
    DEFAULT_CONFIG = {
        "defaults": {
            "thickness": "medium",
            "color": "#000000",
            "style": "solid",
            "markers": {
                "enabled": True,
                "unit": "miles",
                "interval": 1.0,
                "size": 6.0,
                "color": None,  # Use route color
                "label_font_size": 8
            },
            "overlay": {
                "enabled": True,
                "fields": ["distance", "date"],
                "position": "top-left",
                "font_size": 10,
                "font_color": "black",
                "background": True,
                "bg_color": "white",
                "bg_alpha": 0.7
            },
            "export": {
                "formats": ["png"],
                "width": 9,
                "height": 6,
                "dpi": 300,
                "page_size": "letter"
            }
        }
    }
    
    # Valid values for enum-like options
    VALID_VALUES = {
        "thickness": {"thin", "medium", "thick"},
        "style": {"solid", "dashed"},
        "markers.unit": {"miles", "km"},
        "overlay.position": {"top-left", "top-right", "bottom-left", "bottom-right"},
        "overlay.fields": {"distance", "duration", "elevation", "name", "date"},
        "export.formats": {"png", "svg", "pdf"}
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Optional explicit path to a configuration file.
                         If not provided, will search in default locations.
        """
        self.config_path = config_path
        self.config = self.load_config()
        
    def get_default_path(self) -> str:
        """
        Get the default configuration file path.
        
        Returns:
            Path to the default configuration file location
        """
        # Check environment variable first
        if env_path := os.environ.get("GPX_ART_CONFIG"):
            return env_path
            
        # Check user's home directory
        home_config = os.path.expanduser("~/.gpx-art/config.yml")
        if os.path.exists(home_config):
            return home_config
            
        # Check current directory
        current_dir_config = "./gpx-art.yml"
        if os.path.exists(current_dir_config):
            return current_dir_config
            
        # No config file found, return the user home location (for potential writing)
        return home_config
        
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file, falling back to defaults.
        
        Returns:
            Dictionary containing the merged configuration
        
        Raises:
            ConfigError: If the configuration file exists but cannot be loaded
                        or contains invalid values.
        """
        # Start with default configuration
        config = self.DEFAULT_CONFIG.copy()
        
        # Determine config path
        path = self.config_path or self.get_default_path()
        
        # Try to load configuration file if it exists
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    
                if user_config is None:
                    # Empty file
                    logging.warning(f"Config file {path} is empty. Using defaults.")
                    return config
                    
                if not isinstance(user_config, dict):
                    raise ConfigError(f"Config file {path} is not a valid YAML dictionary.")
                    
                # Merge with defaults
                config = self.merge_with_defaults(user_config)
                
                # Validate configuration
                self._validate_config(config)
                    
            except yaml.YAMLError as e:
                raise ConfigError(f"Error parsing config file {path}: {str(e)}")
            except Exception as e:
                if isinstance(e, ConfigError):
                    raise
                raise ConfigError(f"Error loading config from {path}: {str(e)}")
        else:
            logging.info(f"No config file found at {path}. Using defaults.")
            
        return config
    
    def merge_with_defaults(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge user configuration with default values.
        
        Args:
            user_config: User-provided configuration dictionary
            
        Returns:
            Merged configuration dictionary
        """
        # Make a deep copy of defaults to avoid modifying the class constant
        result = self._deep_copy(self.DEFAULT_CONFIG)
        
        # Recursively merge user config into defaults
        self._merge_dicts(result, user_config)
        
        return result
    
    def _merge_dicts(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """
        Recursively merge dictionaries, modifying base in place.
        
        Args:
            base: Base dictionary to merge into
            override: Dictionary with values to override base
        """
        for key, value in override.items():
            # Handle nested dictionaries
            if (
                key in base and 
                isinstance(base[key], dict) and 
                isinstance(value, dict)
            ):
                self._merge_dicts(base[key], value)
            else:
                # Direct value assignment for non-dict values or when keys don't match
                base[key] = value
    
    def _deep_copy(self, obj: Any) -> Any:
        """
        Create a deep copy of an object.
        
        This avoids using copy.deepcopy() which can have issues with some objects.
        
        Args:
            obj: The object to copy
            
        Returns:
            A deep copy of the object
        """
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            # Primitive values are just returned as is
            return obj
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration values.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ConfigError: If the configuration contains invalid values
        """
        if "defaults" not in config:
            raise ConfigError("Configuration must contain a 'defaults' section")
            
        defaults = config["defaults"]
        
        # Check enum values
        if "thickness" in defaults and defaults["thickness"] not in self.VALID_VALUES["thickness"]:
            valid_values = ", ".join(self.VALID_VALUES["thickness"])
            raise ConfigError(f"Invalid thickness: {defaults['thickness']}. Valid values: {valid_values}")
            
        if "style" in defaults and defaults["style"] not in self.VALID_VALUES["style"]:
            valid_values = ", ".join(self.VALID_VALUES["style"])
            raise ConfigError(f"Invalid style: {defaults['style']}. Valid values: {valid_values}")
        
        # Check markers config
        if "markers" in defaults:
            markers = defaults["markers"]
            if not isinstance(markers, dict):
                raise ConfigError("markers must be a dictionary")
                
            if "unit" in markers and markers["unit"] not in self.VALID_VALUES["markers.unit"]:
                valid_values = ", ".join(self.VALID_VALUES["markers.unit"])
                raise ConfigError(f"Invalid markers.unit: {markers['unit']}. Valid values: {valid_values}")
        
        # Check overlay config
        if "overlay" in defaults:
            overlay = defaults["overlay"]
            if not isinstance(overlay, dict):
                raise ConfigError("overlay must be a dictionary")
                
            if "position" in overlay and overlay["position"] not in self.VALID_VALUES["overlay.position"]:
                valid_values = ", ".join(self.VALID_VALUES["overlay.position"])
                raise ConfigError(f"Invalid overlay.position: {overlay['position']}. Valid values: {valid_values}")
                
            if "fields" in overlay:
                if not isinstance(overlay["fields"], list):
                    raise ConfigError("overlay.fields must be a list")
                    
                invalid_fields = set(overlay["fields"]) - self.VALID_VALUES["overlay.fields"]
                if invalid_fields:
                    valid_values = ", ".join(self.VALID_VALUES["overlay.fields"])
                    raise ConfigError(f"Invalid overlay.fields: {', '.join(invalid_fields)}. Valid values: {valid_values}")
        
        # Check export config
        if "export" in defaults:
            export = defaults["export"]
            if not isinstance(export, dict):
                raise ConfigError("export must be a dictionary")
                
            if "formats" in export:
                if not isinstance(export["formats"], list):
                    raise ConfigError("export.formats must be a list")
                    
                invalid_formats = set(export["formats"]) - self.VALID_VALUES["export.formats"]
                if invalid_formats:
                    valid_values = ", ".join(self.VALID_VALUES["export.formats"])
                    raise ConfigError(f"Invalid export.formats: {', '.join(invalid_formats)}. Valid values: {valid_values}")
            
            # Check numeric values
            if "width" in export and not isinstance(export["width"], (int, float)):
                raise ConfigError("export.width must be a number")
                
            if "height" in export and not isinstance(export["height"], (int, float)):
                raise ConfigError("export.height must be a number")
                
            if "dpi" in export and not isinstance(export["dpi"], int):
                raise ConfigError("export.dpi must be an integer")
                
            # Validate numeric ranges
            if "width" in export and export["width"] <= 0:
                raise ConfigError("export.width must be positive")
                
            if "height" in export and export["height"] <= 0:
                raise ConfigError("export.height must be positive")
                
            if "dpi" in export and export["dpi"] <= 0:
                raise ConfigError("export.dpi must be positive")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by its key.
        
        Supports dot notation for nested values (e.g., 'export.formats').
        
        Args:
            key: Configuration key to retrieve
            default: Default value to return if key is not found
            
        Returns:
            Configuration value or default if not found
        """
        # Start with the full config
        current = self.config
        
        # Split the key path
        parts = key.split('.')
        
        # Navigate through the path
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def get_defaults(self) -> Dict[str, Any]:
        """
        Get the defaults section of the configuration.
        
        Returns:
            Dictionary containing default values
        """
        return self.config.get("defaults", {})
    
    def generate_sample(self) -> str:
        """
        Generate a sample configuration file content.
        
        Returns:
            YAML string with sample configuration
        """
        return yaml.dump(self.DEFAULT_CONFIG, sort_keys=False, default_flow_style=False)

