#!/usr/bin/env python3
"""
Mistral CLI - Token Manager
Functions for estimating and managing token limits

Version: 1.5.2
"""

from ..core.logging_config import logger


# ============================================================================
# Token Management
# ============================================================================

def estimate_tokens(text: str) -> int:
    """
    Estimates the number of tokens in a text.
    Rough estimate: ~4 characters per token for German/English.

    Args:
        text: The text

    Returns:
        Estimated token count
    """
    return len(text) // 4


def trim_messages(
    messages: list,
    max_tokens: int = 8000,
    keep_system: bool = True
) -> list:
    """
    Trims the message list to not exceed the token limit.
    Keeps the newest messages and optionally the system message.

    Args:
        messages: List of messages
        max_tokens: Maximum token count
        keep_system: Whether to keep system messages

    Returns:
        Trimmed message list
    """
    if not messages:
        return messages

    # Separate system messages
    system_messages = []
    other_messages = []

    for msg in messages:
        if msg.get("role") == "system" and keep_system:
            system_messages.append(msg)
        else:
            other_messages.append(msg)

    # Estimate tokens for system messages
    system_tokens = sum(
        estimate_tokens(msg.get("content", ""))
        for msg in system_messages
    )

    remaining_tokens = max_tokens - system_tokens

    # Add messages from the back (newest first)
    trimmed = []
    current_tokens = 0

    for msg in reversed(other_messages):
        msg_tokens = estimate_tokens(str(msg.get("content", "")))
        if current_tokens + msg_tokens <= remaining_tokens:
            trimmed.insert(0, msg)
            current_tokens += msg_tokens
        else:
            break

    # Combine system messages with trimmed messages
    result = system_messages + trimmed

    if len(result) < len(messages):
        logger.info(f"Messages trimmed: {len(messages)} -> {len(result)}")

    return result
