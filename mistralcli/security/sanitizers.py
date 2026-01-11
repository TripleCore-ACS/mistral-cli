#!/usr/bin/env python3
"""
Mistral CLI - Sanitizers
Functions for sanitizing paths and log data

Version: 1.5.2
"""

import os
import re


# ============================================================================
# Path Sanitization
# ============================================================================

def sanitize_path(path: str) -> str:
    """
    Sanitizes a file path and expands ~ to home directory.

    Args:
        path: The path to sanitize

    Returns:
        Sanitized, absolute path
    """
    return os.path.abspath(os.path.expanduser(path))


# ============================================================================
# Log Sanitization (v1.2.0)
# ============================================================================

def sanitize_for_log(text: str, max_length: int = 500) -> str:
    """
    Sanitizes text for safe logging (removes sensitive data).

    Args:
        text: The text to sanitize
        max_length: Maximum length of output

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Mask API keys and tokens
    patterns = [
        (r'(MISTRAL_API_KEY[=:\s]+)[^\s]+', r'\1[REDACTED]'),
        (r'(api[_-]?key[=:\s]+)[^\s]+', r'\1[REDACTED]'),
        (r'(token[=:\s]+)[^\s]+', r'\1[REDACTED]'),
        (r'(password[=:\s]+)[^\s]+', r'\1[REDACTED]'),
        (r'(secret[=:\s]+)[^\s]+', r'\1[REDACTED]'),
        (r'(Bearer\s+)[^\s]+', r'\1[REDACTED]'),
        (r'(ftp://[^:]+:)[^@]+(@)', r'\1[REDACTED]\2'),
    ]

    sanitized = text
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "... [truncated]"

    return sanitized
