#!/usr/bin/env python3
"""
Mistral CLI - Formatting
Functions for formatted output

Version: 1.5.2
"""

import sys
from typing import Dict, Any
from ..core.logging_config import logger


# ============================================================================
# Formatted Output
# ============================================================================

def print_error(message: str) -> None:
    """Prints a formatted error message."""
    print(f"❌ Error: {message}", file=sys.stderr)
    logger.error(message)


def print_warning(message: str) -> None:
    """Prints a formatted warning."""
    print(f"⚠️  Warning: {message}", file=sys.stderr)
    logger.warning(message)


def print_success(message: str) -> None:
    """Prints a formatted success message."""
    print(f"✅ {message}")
    logger.info(message)


def print_info(message: str) -> None:
    """Prints a formatted info message."""
    print(f"ℹ️  {message}")
    logger.info(message)


def format_risk_warning(risk_info: Dict[str, Any]) -> str:
    """
    Formats a risk warning for console output.

    Args:
        risk_info: Dictionary with risk details

    Returns:
        Formatted warning
    """
    risk_level = risk_info["risk_level"]

    icons = {
        "CRITICAL": "🚨",
        "HIGH": "⛔",
        "MEDIUM": "⚠️",
        "LOW": "ℹ️",
        "SAFE": "✅"
    }

    icon = icons.get(risk_level, "❓")

    return f"""
{icon} Security warning: {risk_level}
   Category: {risk_info['category']}
   Description: {risk_info['description']}
   Recommendation: {risk_info['recommendation']}
"""
