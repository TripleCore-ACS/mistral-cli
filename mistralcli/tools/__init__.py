#!/usr/bin/env python3
"""
Mistral CLI - Tools Module
All 14 tools for Function Calling

Version: 1.5.2
"""

# Tool Definitions
from .definitions import TOOLS

# Tool Executor
from .executor import execute_tool

# System Tools
from .system import execute_bash_command

# Filesystem Tools
from .filesystem import (
    read_file,
    write_file,
    rename_file,
    copy_file,
    move_file
)

# Network Tools
from .network import (
    fetch_url,
    download_file,
    search_web
)

# Transfer Tools
from .transfer import (
    upload_ftp,
    upload_sftp
)

# Data Processing Tools
from .data import (
    parse_json,
    parse_csv
)

# Image Tools
from .image import get_image_info


__all__ = [
    # Definitions & Executor
    'TOOLS',
    'execute_tool',
    # System
    'execute_bash_command',
    # Filesystem
    'read_file',
    'write_file',
    'rename_file',
    'copy_file',
    'move_file',
    # Network
    'fetch_url',
    'download_file',
    'search_web',
    # Transfer
    'upload_ftp',
    'upload_sftp',
    # Data
    'parse_json',
    'parse_csv',
    # Image
    'get_image_info',
]
