#!/usr/bin/env python3
"""
Mistral CLI - URL Validator
Functions for validating URLs

Version: 1.5.2
"""

import ipaddress
from typing import Tuple
from urllib.parse import urlparse

from ..core.config import ALLOWED_URL_SCHEMES, PRIVATE_IP_RANGES
from ..core.logging_config import logger


# ============================================================================
# URL Validation
# ============================================================================

def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validates a URL for security.

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_safe, error_message)
    """
    try:
        parsed = urlparse(url)

        # Check schema
        if parsed.scheme.lower() not in ALLOWED_URL_SCHEMES:
            return (False, f"URL scheme '{parsed.scheme}' not allowed. Allowed: {ALLOWED_URL_SCHEMES}")

        # Check for empty host
        if not parsed.netloc:
            return (False, "URL has no valid host")

        # Check for local/private IPs
        hostname = parsed.hostname
        if hostname:
            # Try to parse as IP
            try:
                ip = ipaddress.ip_address(hostname)
                for private_range in PRIVATE_IP_RANGES:
                    if ip in ipaddress.ip_network(private_range, strict=False):
                        logger.warning(f"URL to private/local IP blocked: {url}")
                        return (False, f"Access to private/local IP address not allowed: {hostname}")
            except ValueError:
                # Not an IP, but a hostname - that's okay
                pass

            # Block localhost variants
            localhost_patterns = ["localhost", "127.0.0.1", "::1", "0.0.0.0"]
            if any(lh in hostname.lower() for lh in localhost_patterns):
                return (False, "Access to localhost not allowed")

        logger.debug(f"URL validated: {url}")
        return (True, "URL is safe")

    except Exception as e:
        logger.error(f"URL validation failed: {e}")
        return (False, f"URL validation failed: {str(e)}")
