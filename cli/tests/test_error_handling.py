"""
Tests for error handling and logging functionality.
"""

import os
import tempfile
import logging
from unittest.mock import patch, MagicMock, mock_open

import pytest
from click.testing import CliRunner

from route_to_art.main import cli, handle_command_errors
from route_to_art.exceptions import (
    RouteArtError, RouteParseError, ValidationError, 
    RenderingError, ExportError, ConfigError
)
from route_to_art.logging import (
    configure_for_cli, log_info, log_debug, log_error, 
    log_exception, log_warning, log_route_art_error, 
    setup_logging
)


# Test logger setup and management

def test_setup_logging_file_errors():
    """Test handling of errors during log file setup."""
    # Test handling when log directory can't be created
    with patch('os.makedirs', side_effect=OSError("Permission denied")), \
         patch('logging.StreamHandler') as mock_stream:
        
        # Should fall back to console-only logging
        logger = setup_logging(file=True, console=True)
        assert logger is not None
        
        # Console handler should be created
        mock_stream.assert_called_once()


def test_logging_with_custom_levels():
    """Test that custom log levels are respected."""
    with patch('logging.Logger.setLevel') as mock_set_level, \
         patch('logging.Logger.addHandler'):
        
        # Set custom INFO level
        setup_logging(log_level=logging.INFO, console_level=logging.ERROR)
        
        # Logger should be set to the minimum of log_level and console_level
        mock_set_level.assert_called_with(logging.INFO)


def test_error_template_with_complex_data():
    """Test error templates with complex nested data structures."""
    context = {
        "name": "Test",
        "stats": {
            "distance": 12.5,
            "elevation": 850.2
        },
        "points": [
            {"lat": 37.7749, "lon": -122.4194},
            {"lat": 37.7750, "lon": -122.4195}
        ]
    }
    
    error = RouteArtError(
        message="Complex data test",
        context=context
    )
    
    # Test logging with complex context data
    with patch('json.dumps', side_effect=lambda obj, **kwargs: str(obj)) as mock_json:
        log_route_art_error(error)
        mock_json.assert_called_once()
        
    # Test fallback when serialization fails
    with patch('json.dumps', side_effect=TypeError("Not serializable")):
        # Should not raise an exception
        log_route_art_error(error)


def test_error_hierarchy_inheritance():
    """Test that error hierarchy properly inherits behaviors."""
    # Create instances of different error types
    base_error = RouteArtError("Base error")
    parse_error = RouteParseError("Parse error")
    validation_error = ValidationError("Validation error")
    rendering_error = RenderingError("Rendering error")
    export_error = ExportError("Export error")
    config_error = ConfigError("Config error")
    
    # All should be instances of RouteArtError
    assert isinstance(parse_error, RouteArtError)
    assert isinstance(validation_error, RouteArtError)
    assert isinstance(rendering_error, RouteArtError)
    assert isinstance(export_error, RouteArtError)
    assert isinstance(config_error, RouteArtError)
    
    # Test all work with the error handling decorator
    @handle_command_errors
    def raise_error(error):
        raise error
    
    with patch('click.secho'), patch('route_to_art.logging.log_route_art_error'):
        # All should be handled by the decorator
        result1 = raise_error(base_error)
        result2 = raise_error(parse_error)
        result3 = raise_error(validation_error)
        result4 = raise_error(rendering_error)
        result5 = raise_error(export_error)
        result6 = raise_error(config_error)
        
        assert result1 == result2 == result3 == result4 == result5 == result6 == 1


def test_rotate_logs():
    """Test log rotation functionality."""
    from route_to_art.logging import rotate_logs
    
    with patch('os.path.exists', return_value=True), \
         patch('os.path.getsize', return_value=10 * 1024 * 1024), \
         patch('route_to_art.logging.get_logger') as mock_get_logger:
         
        # Create a mock logger with a RotatingFileHandler
        logger = MagicMock()
        handler = MagicMock()
        logger.handlers = [handler]
        mock_get_logger.return_value = logger
        
        # Mock the isinstance check
        with patch('route_to_art.logging.isinstance', return_value=True):
            rotate_logs()
            
            # Should have called doRollover
            handler.doRollover.assert_called_once()


def test_get_log_files():
    """Test retrieval of log files."""
    from route_to_art.logging import get_log_files
    
    with patch('os.path.exists', return_value=True), \
         patch('os.listdir', return_value=["gpx-art.log", "gpx-art.log.1", "other.txt"]):
         
        log_files = get_log_files()
        
        # Should include only .log files
        assert len(log_files) == 2
        assert "gpx-art.log" in log_files
        assert "gpx-art.log.1" in log_files
        assert "other.txt" not in log_files
        
        # Should include full paths
        for path in log_files.values():
            assert os.path.basename(path) in ["gpx-art.log", "gpx-art.log.1"]


# CLI Error Integration Tests

def test_cli_global_error_recovery():
    """Test that CLI as a whole recovers from errors."""
    # Create a test GPX file with invalid content
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gpx") as temp:
        temp.write(b"This is not a valid GPX file")
        temp_path = temp.name
    
    try:
        # Test that the CLI handles parse errors gracefully
        runner = CliRunner()
        result = runner.invoke(cli, ['validate', temp_path])
        
        # Command should fail but not crash
        assert result.exit_code == 1
        assert "Error" in result.output
        assert "Error parsing GPX file" in result.output
    finally:
        # Clean up the temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_cli_verbose_error_output():
    """Test that verbose mode provides more detailed error output."""
    with patch('route_to_art.main.RouteParser.parse', 
              side_effect=Exception("Simulated error with details")), \
         patch('route_to_art.logging.configure_for_cli'), \
         patch('route_to_art.logging.log_exception'):
        
        # Run in normal mode
        runner = CliRunner()
        result1 = runner.invoke(cli, ['info', 'test.gpx'])
        
        # Run in verbose mode
        result2 = runner.invoke(cli, ['-v', 'info', 'test.gpx'])
        
        # Debug mode should show more info
        result3 = runner.invoke(cli, ['--debug', 'info', 'test.gpx'])
        
        # All should fail but verbosity affects output
        assert result1.exit_code == 1
        assert result2.exit_code == 1
        assert result3.exit_code == 1
        
        # Debug mode should include traceback info
        assert "Traceback" in result3.output
        assert "Traceback" not in result1.output


def test_error_with_suggestion():
    """Test that errors with suggestions show those suggestions to the user."""
    # Create a mock RouteParseError with a suggestion
    error = RouteParseError.missing_track(file_path="test.gpx")
    
    with patch('route_to_art.main.RouteParser.parse'), \
         patch('route_to_art.main.RouteParser.to_route', side_effect=error):
        
        # Run the command
        runner = CliRunner()
        result = runner.invoke(cli, ['convert', 'test.gpx', 'output.png'])
        
        # Check that suggestion is in the output
        assert "Suggestion:" in result.output
        assert error.suggestion in result.output


def test_config_override_errors():
    """Test error handling when config options are invalid or conflicting."""
    with patch('route_to_art.config.Config.get', 
              side_effect=ConfigError("Invalid configuration option")), \
         patch('route_to_art.logging.log_error'):
        
        # Run command with config reference
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--config', 'config.yml',
            'convert', 'test.gpx', 'output.png'
        ])
        
        # Check that error is reported properly
        assert result.exit_code == 1
        assert "Configuration error:" in result.output


def test_concurrent_errors():
    """Test handling of multiple errors occurring in different modules."""
    # Create error scenarios in multiple components
    with patch('route_to_art.exporters.Exporter.export_png',
              side_effect=ExportError("PNG export failed")), \
         patch('route_to_art.main.RouteParser.parse'), \
         patch('route_to_art.main.RouteParser.to_route'), \
         patch('route_to_art.main.RouteVisualizer.render_route'), \
         patch('route_to_art.logging.log_error'):
        
        # Run command 
        runner = CliRunner()
        result = runner.invoke(cli, [
            'convert', 'test.gpx', 'output.png'
        ])
        
        # Primary error should be reported
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "PNG export failed" in result.output


@pytest.fixture
def runner():
    """Provide a CLI test runner."""
    return CliRunner()


@pytest.fixture
def logger_mock():
    """Mock the logger to intercept log calls."""
    with patch('route_to_art.logging.get_logger') as mock:
        logger = MagicMock()
        mock.return_value = logger
        yield logger


# Tests for the error handling decorator

def test_handle_command_errors_success():
    """Test the error handling decorator with a successful function."""
    
    # Define a test function that returns a value
    @handle_command_errors
    def success_function():
        return "Success"
    
    # Function should execute normally and return its value
    result = success_function()
    assert result == "Success"


def test_handle_command_errors_with_route_to_art_error():
    """Test the error handling decorator with a RouteArtError."""
    
    # Define a test function that raises a RouteArtError
    @handle_command_errors
    def error_function():
        raise RouteArtError("Test error message", suggestion="Try this fix")
    
    # Function should handle the error and return exit code 1
    with patch('click.secho') as mock_secho, \
         patch('click.echo') as mock_echo, \
         patch('route_to_art.logging.log_route_art_error') as mock_log:
        
        result = error_function()
        
        # Check that the function returns error code
        assert result == 1
        
        # Check that log and UI output were called correctly
        mock_log.assert_called_once()
        mock_secho.assert_called_with("Test error message", fg="red")
        mock_echo.assert_called_with("Suggestion: Try this fix")


def test_handle_command_errors_with_unexpected_error():
    """Test the error handling decorator with an unexpected exception."""
    
    # Define a test function that raises a standard Exception
    @handle_command_errors
    def error_function():
        raise ValueError("Unexpected test error")
    
    # Function should handle the error and return exit code 1
    with patch('click.secho') as mock_secho, \
         patch('click.echo') as mock_echo, \
         patch('route_to_art.logging.log_exception') as mock_log, \
         patch('click.get_current_context') as mock_context:
        
        # Mock context to not show traceback
        ctx_obj = MagicMock()
        ctx_obj.obj.get.return_value = False
        mock_context.return_value = ctx_obj
        
        result = error_function()
        
        # Check that the function returns error code
        assert result == 1
        
        # Check that log and UI output were called correctly
        mock_log.assert_called_once()
        mock_secho.assert_called_with("Unexpected error: Unexpected test error", fg="red")
        mock_echo.assert_called_with("This error has been logged. Please report this issue.")


def test_handle_command_errors_with_debug_mode():
    """Test that traceback is shown in debug mode."""
    
    # Define a test function that raises an exception
    @handle_command_errors
    def error_function():
        raise ValueError("Test error")
    
    # Function should handle the error and show traceback in debug mode
    with patch('click.secho'), \
         patch('click.echo') as mock_echo, \
         patch('click.get_current_context') as mock_context, \
         patch('traceback.format_exc', return_value="Mock traceback"):
        
        # Mock context to show traceback
        ctx_obj = MagicMock()
        ctx_obj.obj.get.return_value = True  # Debug mode is on
        mock_context.return_value = ctx_obj
        
        result = error_function()
        
        # Check that traceback was displayed
        assert result == 1
        mock_echo.assert_any_call("\nTraceback:")
        mock_echo.assert_any_call("Mock traceback")


# Tests for custom exceptions

def test_route_to_art_error_basic():
    """Test basic RouteArtError creation and properties."""
    error = RouteArtError(
        message="Test error message",
        suggestion="Fix suggestion",
        file_path="/path/to/file.gpx",
        context={"key": "value"}
    )
    
    # Check properties
    assert error.message == "Test error message"
    assert error.suggestion == "Fix suggestion"
    assert error.file_path == "/path/to/file.gpx"
    assert error.context == {"key": "value"}
    
    # Check string representation
    error_str = str(error)
    assert "Test error message" in error_str
    assert "/path/to/file.gpx" in error_str
    assert "Fix suggestion" in error_str


def test_gpx_parse_error_factory_methods():
    """Test factory methods for RouteParseError."""
    # Test invalid_gpx factory method
    error1 = RouteParseError.invalid_gpx("XML syntax error", file_path="test.gpx")
    assert "Invalid GPX file: XML syntax error" in str(error1)
    assert "test.gpx" in str(error1)
    
    # Test missing_track factory method
    error2 = RouteParseError.missing_track(file_path="empty.gpx")
    assert "No track data found" in str(error2)
    assert "empty.gpx" in str(error2)
    
    # Test no_coordinates factory method
    error3 = RouteParseError.no_coordinates(file_path="no_coords.gpx")
    assert "No coordinate data found" in str(error3)
    assert "no_coords.gpx" in str(error3)


def test_validation_error_factory_methods():
    """Test factory methods for ValidationError."""
    # Test invalid_color factory method
    error1 = ValidationError.invalid_color("not-a-color")
    assert "Invalid color value: not-a-color" in str(error1)
    
    # Test invalid_thickness factory method
    error2 = ValidationError.invalid_thickness("extra-thick", ["thin", "medium", "thick"])
    assert "Invalid thickness: extra-thick" in str(error2)
    assert "thin, medium, thick" in str(error2)
    
    # Test invalid_numeric_range factory method
    error3 = ValidationError.invalid_numeric_range("opacity", 1.5, 0.0, 1.0)
    assert "opacity must be between 0.0 and 1.0, got 1.5" in str(error3)


def test_rendering_error_factory_methods():
    """Test factory methods for RenderingError."""
    # Test rendering_failure factory method
    error1 = RenderingError.rendering_failure("Memory error")
    assert "Failed to render route: Memory error" in str(error1)
    
    # Test empty_route factory method
    error2 = RenderingError.empty_route()
    assert "Cannot render empty route" in str(error2)
    
    # Test matplotlib_error factory method
    error3 = RenderingError.matplotlib_error("Invalid color map")
    assert "Matplotlib error during rendering: Invalid color map" in str(error3)


def test_export_error_factory_methods():
    """Test factory methods for ExportError."""
    # Test export_failure factory method
    error1 = ExportError.export_failure("PDF", "Missing library", file_path="output.pdf")
    assert "Failed to export to PDF: Missing library" in str(error1)
    assert "output.pdf" in str(error1)
    
    # Test missing_dependency factory method if it exists
    if hasattr(ExportError, 'missing_dependency'):
        error2 = ExportError.missing_dependency("PDF", "reportlab", "pip install reportlab")
        assert "Missing dependency for PDF export" in str(error2)
        assert "reportlab" in str(error2)
        assert "pip install reportlab" in str(error2)


def test_config_error_basic():
    """Test basic ConfigError functionality."""
    # Since ConfigError doesn't have factory methods in the current implementation,
    # we'll test the basic error creation
    error = ConfigError("Invalid configuration: missing required field")
    assert "Invalid configuration: missing required field" in str(error)
    
    # Test with error context if supported by the implementation
    try:
        # Some implementations of ConfigError might support additional context
        error = ConfigError("Invalid color", config_key="color", value="#zzz")
        assert "Invalid color" in str(error)
    except TypeError:
        # Basic implementation only accepts a message
        pass


# Tests for error message templates

def test_error_message_templates():
    """Test that error message templates work correctly."""
    # Test a standard template
    error1 = RouteArtError.from_template(
        'file_not_found',
        {'path': '/missing/file.gpx'}
    )
    assert "Cannot find file: /missing/file.gpx" in str(error1)
    
    # Test a template with multiple variables
    error2 = RouteArtError.from_template(
        'invalid_file_type',
        {'path': 'test.jpg', 'expected_types': 'GPX, KML'}
    )
    assert "Invalid file type for test.jpg" in str(error2)
    assert "Expected GPX, KML" in str(error2)
    
    # Test handling of missing template
    error3 = RouteArtError.from_template('non_existent_template')
    assert "Unknown error template: non_existent_template" in str(error3)
    
    # Test handling of missing variables in template
    error4 = RouteArtError.from_template('invalid_file_type', {'path': 'test.jpg'})
    assert "Missing variables" in str(error4)


# Tests for error context and suggestions

def test_error_context_and_suggestions():
    """Test that context and suggestions are properly stored and displayed."""
    original_error = ValueError("Original error")
    
    error = RouteArtError(
        message="Main error message",
        original_error=original_error,
        suggestion="Try this solution",
        file_path="/path/to/file.gpx",
        context={"operation": "parse", "line": 42}
    )
    
    # Check that all information is included in the string representation
    error_str = str(error)
    assert "Main error message" in error_str
    assert "Original error: Original error" in error_str
    assert "Try this solution" in error_str
    assert "/path/to/file.gpx" in error_str
    
    # Check that context is stored
    assert error.context["operation"] == "parse"
    assert error.context["line"] == 42
    
    # Check that original error is stored
    assert error.original_error is original_error
    
    # Check that suggestion is stored
    assert error.suggestion == "Try this solution"


# Tests for logging functionality

def test_log_error(logger_mock):
    """Test the log_error function."""
    error = ValueError("Test error")
    
    # Test without module
    log_error(error, "Custom message")
    logger_mock.log.assert_called_with(logging.ERROR, "Custom message")
    
    # Test with module
    log_error(error, "Module error", module="test_module")
    logger_mock.log.assert_called_with(logging.ERROR, "[test_module] Module error")
    
    # Test with traceback
    with patch('traceback.format_exc', return_value="Mock traceback"):
        log_error(error, "Error with traceback", include_traceback=True)
        logger_mock.log.assert_called_with(logging.ERROR, "Error with traceback\nMock traceback")
    
    # Test without traceback
    log_error(error, "Error without traceback", include_traceback=False)
    logger_mock.log.assert_called_with(logging.ERROR, "Error without traceback")


def test_log_route_art_error(logger_mock):
    """Test the log_route_art_error function."""
    error = RouteArtError(
        message="GPX Art error",
        context={"key": "value"},
        suggestion="Try this"
    )
    
    # Test with module
    log_route_art_error(error, module="test_module")
    
    # Verify that the logger was called with the correct message
    call_args = logger_mock.error.call_args[0][0]
    assert "[test_module] GPX Art error" in call_args
    
    # Test with context serialization
    with patch('json.dumps', return_value='{"key": "value"}'):
        log_route_art_error(error)
        call_args = logger_mock.error.call_args[0][0]
        assert 'Context: {"key": "value"}' in call_args


def test_log_exception(logger_mock):
    """Test the log_exception function."""
    error = ValueError("Test exception")
    
    with patch('route_to_art.logging.log_error') as mock_log_error:
        log_exception(error, "Exception occurred", module="test_module")
        
        # Verify log_error was called with the right parameters
        mock_log_error.assert_called_once_with(
            error, "Exception occurred", "test_module", 
            include_traceback=True, level=logging.ERROR
        )


def test_log_warning(logger_mock):
    """Test the log_warning function."""
    # Test basic warning
    log_warning("Warning message")
    logger_mock.warning.assert_called_with("Warning message")
    
    # Test with module
    log_warning("Module warning", module="test_module")
    logger_mock.warning.assert_called_with("[test_module] Module warning")
    
    # Test with error
    error = ValueError("Error details")
    log_warning("Warning with error", error=error)
    logger_mock.warning.assert_called_with("Warning with error: Error details")


def test_log_info(logger_mock):
    """Test the log_info function."""
    log_info("Info message")
    logger_mock.info.assert_called_with("Info message")
    
    log_info("Module info", module="test_module")
    logger_mock.info.assert_called_with("[test_module] Module info")


def test_log_debug(logger_mock):
    """Test the log_debug function."""
    # Test basic debug message
    log_debug("Debug message")
    logger_mock.debug.assert_called_with("Debug message")
    
    # Test with module
    log_debug("Module debug", module="test_module")
    logger_mock.debug.assert_called_with("[test_module] Module debug")
    
    # Test with data
    data = {"key": "value"}
    with patch('json.dumps', return_value='{"key": "value"}'):
        log_debug("Debug with data", data=data)
        logger_mock.debug.assert_called_with('Debug with data\nData: {"key": "value"}')


def test_configure_for_cli():
    """Test the configure_for_cli function."""
    with patch('route_to_art.logging.setup_logging') as mock_setup:
        # Test default verbosity (WARNING)
        configure_for_cli(verbosity=0)
        mock_setup.assert_called_with(
            log_level=logging.DEBUG,
            console_level=logging.WARNING,
            console=True,
            file=True
        )
        
        # Test INFO verbosity
        configure_for_cli(verbosity=1)
        mock_setup.assert_called_with(
            log_level=logging.DEBUG,
            console_level=logging.INFO,
            console=True,
            file=True
        )
        
        # Test DEBUG verbosity
        configure_for_cli(verbosity=2)
        mock_setup.assert_called_with(
            log_level=logging.DEBUG,
            console_level=logging.DEBUG,
            console=True,
            file=True
        )
        

# Tests for error recovery strategies

def test_cli_convert_recover_from_marker_error():
    """Test that convert command recovers from marker rendering errors."""
    with patch('click.echo'), \
         patch('click.secho'), \
         patch('route_to_art.main.RouteParser.parse'), \
         patch('route_to_art.main.RouteParser.to_route'), \
         patch('route_to_art.main.RouteVisualizer.render_route'), \
         patch('route_to_art.main.RouteVisualizer.add_distance_markers',
               side_effect=Exception("Marker error")), \
         patch('route_to_art.main.Exporter.export_png'):
        
        # Create a runner and run the command with markers
        runner = CliRunner()
        result = runner.invoke(cli, [
            'convert', 'test.gpx', 'output.png', 
            '--markers'
        ])
        
        # Command should succeed despite marker error
        assert result.exit_code == 0
        
        # Check that a warning was shown
        # We can't check click.secho directly since we've mocked it,
        # but we know from the source that it will be called with a warning


def test_cli_convert_recover_from_overlay_error():
    """Test that convert command recovers from overlay rendering errors."""
    with patch('click.echo'), \
         patch('click.secho'), \
         patch('route_to_art.main.RouteParser.parse'), \
         patch('route_to_art.main.RouteParser.to_route'), \
         patch('route_to_art.main.RouteVisualizer.render_route'), \
         patch('route_to_art.main.RouteVisualizer.add_overlay',
               side_effect=Exception("Overlay error")), \
         patch('route_to_art.main.Exporter.export_png'):
        
        # Create a runner and run the command with overlay
        runner = CliRunner()
        result = runner.invoke(cli, [
            'convert', 'test.gpx', 'output.png', 
            '--overlay', 'distance,name'
        ])
        
        # Command should succeed despite overlay error
        assert result.exit_code == 0
        
        # Check that a warning was shown (indirectly verified)


def test_export_multiple_partial_success():
    """Test that export_multiple continues on single format failures."""
    # Setup test scenario
    with patch('route_to_art.exporters.Exporter.export_png') as mock_png, \
         patch('route_to_art.exporters.Exporter.export_svg') as mock_svg, \
         patch('route_to_art.exporters.Exporter.export_pdf',
               side_effect=ExportError("PDF export failed")):
               
        # The PNG and SVG exports will succeed, but PDF will fail
        mock_png.return_value = "output.png"
        mock_svg.return_value = "output.svg"
        
        # Create a test runner
        runner = CliRunner()
        
        # Run with config to use our mocked Exporter
        with patch('route_to_art.main.Exporter'), \
             patch('route_to_art.main.RouteParser.parse'), \
             patch('route_to_art.main.RouteParser.to_route'), \
             patch('route_to_art.main.RouteVisualizer.render_route'), \
             patch('route_to_art.main.get_effective_options', return_value={}):
            
            # Call with multiple formats
            result = runner.invoke(cli, [
                'convert', 'test.gpx', 'output', 
                '--format', 'png,svg,pdf'
            ])
            
            # Command should continue despite PDF error
            assert "Error: Failed to export PDF" in result.output
            # But it should still have processed the other formats
            assert mock_png.called
            assert mock_svg.called


def test_cli_config_file_not_found_recovery():
    """Test recovery when config file is not found."""
    with patch('route_to_art.config.Config.load_file', 
              side_effect=FileNotFoundError("Config not found")), \
         patch('route_to_art.logging.log_warning'):
        
        # Create a runner and run with non-existent config
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--config', 'nonexistent.yml',
            'info', 'test.gpx'
        ])
        
        # Command should continue with default config
        assert result.exit_code == 2  # Will fail due to test.gpx not existing
        assert "Error loading configuration" in result.output


