#!/usr/bin/env python3
"""
Mistral CLI - Path Validator
Functions for validating file paths

Version: 1.5.2
"""

import os
from typing import Optional, Tuple


# ============================================================================
# Path Validation (v1.2.0)
# ============================================================================

def is_safe_path(path: str, base_dir: Optional[str] = None) -> Tuple[bool, str]:
    """
    Checks if a path is safe (no path traversal attack).

    Args:
        path: The path to check
        base_dir: Optional base directory for relative paths

    Returns:
        Tuple[bool, str]: (is_safe, reason or normalized path)
    """
    if not path or not path.strip():
        return False, "Empty path"

    # Path traversal patterns
    if '..' in path:
        return False, "Path traversal detected (..)"

    # Absolute paths to sensitive areas
    sensitive_prefixes = ['/etc', '/usr', '/var', '/boot', '/root', '/dev', '/proc', '/sys']

    try:
        # Normalize path
        normalized = os.path.normpath(path)

        if base_dir:
            base_normalized = os.path.normpath(base_dir)
            full_path = os.path.normpath(os.path.join(base_normalized, normalized))

            # Check if path stays within base directory
            if not full_path.startswith(base_normalized):
                return False, "Path leaves the allowed directory"

            return True, full_path

        # Without base dir: check sensitive areas
        abs_path = os.path.abspath(os.path.expanduser(normalized))

        for prefix in sensitive_prefixes:
            if abs_path.startswith(prefix):
                return False, f"Access to sensitive area: {prefix}"

        return True, abs_path

    except Exception as e:
        return False, f"Path validation failed: {e}"


def validate_path(path: str, allow_system_paths: bool = False) -> Tuple[bool, str]:
    """
    Validates a file path for security.
    (Alias for is_safe_path for compatibility)

    Args:
        path: The path to validate
        allow_system_paths: Whether system paths are allowed (default: False)

    Returns:
        Tuple of (is_safe, error_message)
    """
    return is_safe_path(path)
