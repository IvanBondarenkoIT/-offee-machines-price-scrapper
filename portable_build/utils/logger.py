"""
Logging utility for the scraper
"""
import logging
import sys
from pathlib import Path
from config import LOG_CONFIG


def setup_logger(name: str = "scraper") -> logging.Logger:
    """
    Setup and configure logger
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_CONFIG["level"])
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_CONFIG["format"])
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(
        LOG_CONFIG["filename"],
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_CONFIG["format"])
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

