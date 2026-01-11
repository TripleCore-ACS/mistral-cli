#!/usr/bin/env python3
"""
Mistral CLI - Package Root
Main package for the Mistral CLI

Version: 1.5.2
"""

from .utils.helpers import get_version

__version__ = get_version()
__author__ = "Daniel Thun"
__license__ = "MIT"

# Haupt-Exports für einfachen Import
from .core.logging_config import logger, setup_logging
from .core.config import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT,
    RiskLevel
)

# Lazy imports (require mistralai)
def get_client(*args, **kwargs):
    from .core import get_client as _get_client
    return _get_client(*args, **kwargs)

def reset_client():
    from .core import reset_client as _reset_client
    return _reset_client()

__all__ = [
    # Version
    '__version__',
    # Client
    'get_client',
    'reset_client',
    # Logging
    'logger',
    'setup_logging',
    # Config
    'DEFAULT_MODEL',
    'DEFAULT_TEMPERATURE',
    'DEFAULT_MAX_TOKENS',
    'DEFAULT_TIMEOUT',
    'RiskLevel',
]
