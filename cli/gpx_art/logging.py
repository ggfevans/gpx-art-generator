"""
Logging configuration for gpx-art.

This module provides logging configuration and helper functions
for file-based and console logging with proper error handling.
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union, Dict, Any

# Constants for default log configuration
DEFAULT_LOG_DIR = os.path.expanduser("~/.gpx-art/logs")
DEFAULT_LOG_FILE = "gpx-art.log"
DEFAULT_MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
DEFAULT_BACKUP_COUNT = 3  # Keep 3 rotated log files
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
ERROR_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(traceback)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Global logger instance
_logger = None


def get_logger() -> logging.Logger:
    """
    Get the configured logger instance.
    
    If the logger hasn't been initialized yet, it will be initialized
    with default settings.
    
    Returns:
        The configured logger instance
    """
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return _logger


def setup_logging(
    log_dir: Optional[str] = None,
    log_file: Optional[str] = None,
    log_level: int = logging.INFO,
    console_level: int = logging.WARNING,
    max_size: int = DEFAULT_MAX_LOG_SIZE,
    backup_count: int = DEFAULT_BACKUP_COUNT,
    console: bool = True,
    file: bool = True
) -> logging.Logger:
    """
    Set up logging with file and console handlers.
    
    Args:
        log_dir: Directory for log files, defaults to ~/.gpx-art/logs
        log_file: Log file name, defaults to gpx-art.log
        log_level: Log level for file logging
        console_level: Log level for console output
        max_size: Maximum size of log file before rotation in bytes
        backup_count: Number of backup log files to keep
        console: Whether to enable console logging
        file: Whether to enable file logging
        
    Returns:
        Configured logger instance
        
    Raises:
        OSError: If log directory cannot be created or accessed
    """
    global _logger
    
    # Create logger
    logger = logging.getLogger("gpx-art")
    logger.setLevel(min(log_level, console_level) if console else log_level)
    
    # Clear existing handlers (in case of reconfiguration)
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
    
    # Formatter for regular logs
    regular_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(regular_formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if requested
    if file:
        log_dir = log_dir or DEFAULT_LOG_DIR
        log_file = log_file or DEFAULT_LOG_FILE
        log_path = os.path.join(log_dir, log_file)
        
        try:
            # Create log directory if it doesn't exist
            os.makedirs(log_dir, exist_ok=True)
            
            # Create rotating file handler
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=max_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(regular_formatter)
            logger.addHandler(file_handler)
            
            # Log the start of a new session
            logger.info("--- New logging session started ---")
            
        except OSError as e:
            # Log to console if file logging fails
            logger.error(f"Failed to set up file logging: {str(e)}")
            # Raise an exception only if console logging is not enabled
            if not console:
                raise
    
    # Store the logger globally
    _logger = logger
    return logger


def get_log_files() -> Dict[str, str]:
    """
    Get all log files in the log directory.
    
    Returns:
        Dictionary mapping log file names to absolute paths
    """
    log_dir = DEFAULT_LOG_DIR
    log_files = {}
    
    try:
        if os.path.exists(log_dir):
            for file in os.listdir(log_dir):
                if file.endswith('.log'):
                    log_files[file] = os.path.join(log_dir, file)
    except OSError:
        pass
    
    return log_files


def rotate_logs(max_size: int = DEFAULT_MAX_LOG_SIZE) -> None:
    """
    Manually trigger log rotation if the current log file exceeds max_size.
    
    Args:
        max_size: Maximum size in bytes before rotation
    """
    log_file = os.path.join(DEFAULT_LOG_DIR, DEFAULT_LOG_FILE)
    if os.path.exists(log_file) and os.path.getsize(log_file) > max_size:
        logger = get_logger()
        
        # Find and get the file handler
        for handler in logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                handler.doRollover()
                logger.info("Log file manually rotated")
                break


def clear_logs() -> None:
    """
    Clear all log files.
    """
    log_files = get_log_files()
    
    for path in log_files.values():
        try:
            with open(path, 'w') as f:
                pass
        except OSError:
            pass
    
    logger = get_logger()
    logger.info("Log files cleared")


def log_error(
    error: Exception,
    message: Optional[str] = None,
    module: Optional[str] = None,
    include_traceback: bool = True,
    level: int = logging.ERROR
) -> None:
    """
    Log an error with optional traceback and context.
    
    Args:
        error: The exception to log
        message: Optional custom message to include
        module: Module name for context
        include_traceback: Whether to include a traceback
        level: Log level to use
    """
    logger = get_logger()
    
    # Build the log message
    log_message = message or str(error)
    if module:
        log_message = f"[{module}] {log_message}"
    
    # Include traceback if requested
    if include_traceback:
        tb_str = traceback.format_exc()
        if "NoneType: None" not in tb_str:  # Avoid logging empty tracebacks
            log_message += f"\n{tb_str}"
    
    # Log at the specified level
    logger.log(level, log_message)


def log_exception(
    error: Exception,
    message: Optional[str] = None,
    module: Optional[str] = None
) -> None:
    """
    Log an exception at the ERROR level with traceback.
    
    Args:
        error: The exception to log
        message: Optional custom message to include
        module: Module name for context
    """
    log_error(error, message, module, include_traceback=True, level=logging.ERROR)


def log_warning(
    message: str,
    module: Optional[str] = None,
    error: Optional[Exception] = None
) -> None:
    """
    Log a warning message.
    
    Args:
        message: Warning message to log
        module: Module name for context
        error: Optional exception related to the warning
    """
    logger = get_logger()
    
    if module:
        message = f"[{module}] {message}"
    
    if error:
        message += f": {str(error)}"
    
    logger.warning(message)


def log_info(message: str, module: Optional[str] = None) -> None:
    """
    Log an info message.
    
    Args:
        message: Information message to log
        module: Module name for context
    """
    logger = get_logger()
    
    if module:
        message = f"[{module}] {message}"
    
    logger.info(message)


def log_debug(message: str, module: Optional[str] = None, data: Any = None) -> None:
    """
    Log a debug message with optional data.
    
    Args:
        message: Debug message to log
        module: Module name for context
        data: Optional data to include in the log
    """
    logger = get_logger()
    
    if module:
        message = f"[{module}] {message}"
    
    if data is not None:
        try:
            import json
            data_str = json.dumps(data, default=str, indent=2)
            message += f"\nData: {data_str}"
        except (TypeError, ValueError):
            message += f"\nData: {str(data)}"
    
    logger.debug(message)


def get_log_path() -> Optional[str]:
    """
    Get the path to the current log file.
    
    Returns:
        Path to log file or None if logging is not configured
    """
    log_file = os.path.join(DEFAULT_LOG_DIR, DEFAULT_LOG_FILE)
    if os.path.exists(log_file):
        return log_file
    return None


def log_gpx_art_error(
    error: 'GPXArtError',  # Forward reference to avoid circular import
    module: Optional[str] = None
) -> None:
    """
    Log a GPXArtError with its context information.
    
    Args:
        error: The GPXArtError to log
        module: Module name for context
    """
    logger = get_logger()
    
    # Build the log message
    log_message = str(error)
    if module:
        log_message = f"[{module}] {log_message}"
    
    # Add context information
    if hasattr(error, 'context') and error.context:
        try:
            import json
            context_str = json.dumps(error.context, default=str, indent=2)
            log_message += f"\nContext: {context_str}"
        except (TypeError, ValueError):
            pass
    
    # Add traceback if available
    if hasattr(error, 'traceback') and error.traceback:
        log_message += f"\nTraceback:\n{error.traceback}"
    
    logger.error(log_message)


def configure_for_cli(
    verbosity: int = 0,
    log_to_file: bool = True
) -> logging.Logger:
    """
    Configure logging specifically for CLI usage with verbosity levels.
    
    Args:
        verbosity: Verbosity level (0=WARNING, 1=INFO, 2+=DEBUG)
        log_to_file: Whether to log to file
        
    Returns:
        Configured logger instance
    """
    # Map verbosity to log levels
    console_level = logging.WARNING
    if verbosity == 1:
        console_level = logging.INFO
    elif verbosity >= 2:
        console_level = logging.DEBUG
    
    # Configure logger
    return setup_logging(
        log_level=logging.DEBUG,  # Always log all details to file
        console_level=console_level,
        console=True,
        file=log_to_file
    )

