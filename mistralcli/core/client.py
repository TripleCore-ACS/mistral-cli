#!/usr/bin/env python3
"""
Mistral CLI - Client Management
Initialization and management of the Mistral AI Client

Version: 1.5.2
"""

import os
import sys
from typing import Optional
from mistralai import Mistral

from .logging_config import logger
from ..auth.api_key_manager import get_stored_api_key, setup_api_key_interactive


# ============================================================================
# Client Initialization
# ============================================================================

_client_instance: Optional[Mistral] = None


def get_client(api_key: Optional[str] = None) -> Mistral:
    """
    Initializes and returns a Mistral Client.
    Uses Singleton pattern for reuse.

    Searches for API-Key in the following order:
    1. Explicit parameter
    2. Environment variable MISTRAL_API_KEY
    3. Securely stored key (Keyring/AES)
    4. Interactive setup (if not found)

    Args:
        api_key: Optional API-Key (overrides everything else)

    Returns:
        Mistral Client instance

    Raises:
        SystemExit: When no API-Key is available
    """
    global _client_instance

    # If already initialized and no new key, use existing instance
    if _client_instance is not None and api_key is None:
        return _client_instance

    # Determine API-Key (Priority: Parameter > Env > Stored)
    key = api_key or os.environ.get("MISTRAL_API_KEY")

    # Fallback: Securely stored key
    if not key:
        key = get_stored_api_key()

    # Still no key? Offer interactive setup
    if not key:
        print()
        print("🔑 No API-Key found.")
        print()

        try:
            response = input("Do you want to set up an API-Key now? [Y/n]: ").strip().lower()
            if response in ['', 'j', 'ja', 'y', 'yes']:
                if setup_api_key_interactive():
                    key = get_stored_api_key()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")

    if not key:
        error_msg = """
╔══════════════════════════════════════════════════════════════════╗
║  ERROR: MISTRAL_API_KEY not found                               ║
╠══════════════════════════════════════════════════════════════════╣
║  Please set up the API-Key in one of the following ways:        ║
║                                                                  ║
║  Option 1: Interactive setup (recommended, secure)              ║
║    ./mistral auth setup                                          ║
║                                                                  ║
║  Option 2: Environment variable (temporary)                      ║
║    export MISTRAL_API_KEY='your-api-key'                        ║
║                                                                  ║
║  Get API-Key: https://console.mistral.ai/                       ║
╚══════════════════════════════════════════════════════════════════╝
"""
        print(error_msg, file=sys.stderr)
        logger.error("MISTRAL_API_KEY not found")
        sys.exit(1)

    try:
        client = Mistral(api_key=key)
        logger.info("Mistral Client successfully initialized")

        # Store instance only if no explicit key was passed
        if api_key is None:
            _client_instance = client

        return client

    except Exception as e:
        logger.error(f"Error during client initialization: {e}")
        print(f"Error initializing Mistral Client: {e}", file=sys.stderr)
        sys.exit(1)


def reset_client() -> None:
    """Resets the client (for tests or reconfiguration)."""
    global _client_instance
    _client_instance = None
    logger.debug("Client instance reset")
