"""Logging configuration for Word Cloud Generator."""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = 'wordcloud_generator',
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup and configure a logger for the application.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        format_string: Custom format string for log messages
        
    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = '[%(levelname)s]  %(message)s'
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding multiple handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger

