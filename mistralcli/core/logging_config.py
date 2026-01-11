#!/usr/bin/env python3
"""
Mistral CLI - Logging Configuration
Configuration of the logging system

Version: 1.5.2
"""

import sys
import logging
from pathlib import Path
from .config import LOG_FILE


# ============================================================================
# Logging Configuration
# ============================================================================

def setup_logging(
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = False
) -> logging.Logger:
    """
    Configures and returns a logger for the Mistral CLI.

    Args:
        level: Log level (default: INFO)
        log_to_file: Whether to log to file (default: True)
        log_to_console: Whether to log to console (default: False)

    Returns:
        Configured logger
    """
    logger = logging.getLogger("mistral-cli")

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Format for log entries
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File Handler
    if log_to_file:
        try:
            file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file: {e}", file=sys.stderr)

    # Console Handler (optional)
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# Global logger
logger = setup_logging()
