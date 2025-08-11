"""
Unified logging configuration for TTRPG Session Notes automation.
Replaces colorama-based print statements with proper logging.
"""

import logging
import sys
from typing import Optional
from colorama import Fore, Style, init

# Initialize colorama
init()

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log messages based on level."""
    
    # Color mapping for different log levels
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
    }
    
    def format(self, record):
        """Format the log record with colors."""
        # Get the color for this log level
        color = self.COLORS.get(record.levelname, '')
        reset = Style.RESET_ALL if color else ''
        
        # Format the message
        formatted = super().format(record)
        
        # Add colors
        return f"{color}{formatted}{reset}"

class TTRPGLogger:
    """Centralized logging setup for TTRPG automation system."""
    
    def __init__(self, 
                 name: str = "ttrpg_session_notes",
                 level: str = "INFO",
                 use_colors: bool = True,
                 log_to_file: Optional[str] = None):
        """Initialize the logging system.
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            use_colors: Whether to use colored output for console
            log_to_file: Optional file path to also log to
        """
        self.logger = logging.getLogger(name)
        self.use_colors = use_colors
        
        # Set level
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Add console handler
        self._add_console_handler()
        
        # Add file handler if requested
        if log_to_file:
            self._add_file_handler(log_to_file)
    
    def _add_console_handler(self):
        """Add colored console handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        
        if self.use_colors:
            formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
        
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _add_file_handler(self, log_file: str):
        """Add file handler for persistent logging."""
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger

# Convenience functions for backward compatibility
def setup_logging(level: str = "INFO", 
                 use_colors: bool = True,
                 log_to_file: Optional[str] = None,
                 logger_name: str = "ttrpg_session_notes") -> logging.Logger:
    """Set up logging and return logger instance."""
    logger_manager = TTRPGLogger(
        name=logger_name,
        level=level,
        use_colors=use_colors,
        log_to_file=log_to_file
    )
    return logger_manager.get_logger()

def get_logger(name: str = "ttrpg_session_notes") -> logging.Logger:
    """Get a logger instance (creates default setup if needed)."""
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set up default
    if not logger.handlers:
        logger = setup_logging(logger_name=name)
    
    return logger

# Migration helpers for replacing colorama prints
def print_info(message: str, logger: Optional[logging.Logger] = None):
    """Replace colorama info prints."""
    if logger is None:
        logger = get_logger()
    logger.info(message)

def print_success(message: str, logger: Optional[logging.Logger] = None):
    """Replace colorama success prints."""
    if logger is None:
        logger = get_logger()
    logger.info(f"✓ {message}")

def print_warning(message: str, logger: Optional[logging.Logger] = None):
    """Replace colorama warning prints."""
    if logger is None:
        logger = get_logger()
    logger.warning(message)

def print_error(message: str, logger: Optional[logging.Logger] = None):
    """Replace colorama error prints."""
    if logger is None:
        logger = get_logger()
    logger.error(message)

def print_progress(current: int, total: int, message: str = "", 
                  logger: Optional[logging.Logger] = None):
    """Print progress information."""
    if logger is None:
        logger = get_logger()
    
    percentage = (current / total * 100) if total > 0 else 0
    progress_msg = f"Progress: {current}/{total} ({percentage:.1f}%)"
    if message:
        progress_msg += f" - {message}"
    
    logger.info(progress_msg)