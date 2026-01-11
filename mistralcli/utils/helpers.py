#!/usr/bin/env python3
"""
Mistral CLI - Helpers
General helper functions

Version: 1.5.2
"""

from typing import Optional, Tuple
from pathlib import Path

from ..security.path_validator import is_safe_path
from ..security.sanitizers import sanitize_path


# ============================================================================
# File Operation Safety
# ============================================================================

def check_file_operation_safety(
    operation: str,
    source: str,
    destination: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Checks if a file operation is safe.

    Args:
        operation: The operation (read, write, copy, move, delete)
        source: Source path
        destination: Destination path (optional)

    Returns:
        Tuple of (is_safe, error_message)
    """
    # Validate source path
    is_safe, message = is_safe_path(source)
    if not is_safe:
        return (False, f"Source path unsafe: {message}")

    # Validate destination path if present
    if destination:
        is_safe, message = is_safe_path(destination)
        if not is_safe:
            return (False, f"Destination path unsafe: {message}")

    # Special checks depending on operation
    if operation == "delete":
        source_path = sanitize_path(source)
        home = str(Path.home())

        # Prevent deletion of important directories
        protected_dirs = [home, "/", "/home", "/etc", "/var", "/usr"]
        if source_path in protected_dirs:
            return (False, f"Deletion of {source_path} not allowed")

    return (True, "Operation is safe")


# ============================================================================
# Version
# ============================================================================

def get_version() -> str:
    """Returns the current version of mistral-cli."""
    return "1.5.2"
