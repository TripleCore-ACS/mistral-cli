#!/usr/bin/env python3
"""
Mistral CLI - Core Module
Core functionality: Client, Config, Logging

Version: 1.5.2
"""

from .config import *
from .logging_config import logger, setup_logging

# Lazy import for client (requires mistralai)
def get_client(*args, **kwargs):
    from .client import get_client as _get_client
    return _get_client(*args, **kwargs)

def reset_client():
    from .client import reset_client as _reset_client
    return _reset_client()

__all__ = [
    # Client
    'get_client',
    'reset_client',
    # Logging
    'logger',
    'setup_logging',
]
