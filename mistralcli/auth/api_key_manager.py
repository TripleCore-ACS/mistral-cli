#!/usr/bin/env python3
"""
Mistral CLI - API Key Manager
Secure management of API keys with Keyring or AES encryption

Version: 1.5.2
"""

import os
import getpass
import secrets
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

from ..core.config import (
    KEYRING_AVAILABLE,
    CRYPTO_AVAILABLE,
    KEYRING_SERVICE,
    KEYRING_USERNAME,
    ENCRYPTED_KEY_FILE,
    SALT_FILE
)
from ..core.logging_config import logger

# Imports for optional dependencies
if KEYRING_AVAILABLE:
    import keyring

if CRYPTO_AVAILABLE:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64


# ============================================================================
# AES Encryption (Fallback)
# ============================================================================

def _derive_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Derives an AES key from a password (PBKDF2).

    Args:
        password: The master password
        salt: Salt for derivation

    Returns:
        32-byte key for Fernet
    """
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("cryptography not installed")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # OWASP recommendation for 2023+
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def _get_or_create_salt() -> bytes:
    """
    Reads or creates a salt for key derivation.

    Returns:
        16-byte salt
    """
    if SALT_FILE.exists():
        with open(SALT_FILE, 'rb') as f:
            return f.read()
    else:
        salt = secrets.token_bytes(16)
        with open(SALT_FILE, 'wb') as f:
            f.write(salt)
        # Restrict file permissions (owner only)
        os.chmod(SALT_FILE, 0o600)
        return salt


# ============================================================================
# API Key Storage
# ============================================================================

def store_api_key(api_key: str, master_password: Optional[str] = None) -> Tuple[bool, str]:
    """
    Stores the API key securely.

    Method 1 (Keyring): Uses OS-native credential manager
    Method 2 (AES): Encrypts with master password

    Args:
        api_key: The API key to store
        master_password: Optional master password for AES fallback

    Returns:
        Tuple of (success, method/error_message)
    """
    if not api_key or not api_key.strip():
        return (False, "API key must not be empty")

    api_key = api_key.strip()

    # Method 1: Keyring (preferred)
    if KEYRING_AVAILABLE:
        try:
            keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, api_key)
            logger.info("API key securely stored in system keyring")
            return (True, "keyring")
        except Exception as e:
            logger.warning(f"Keyring storage failed: {e}")
            # Fallback to AES

    # Method 2: AES encryption with master password
    if CRYPTO_AVAILABLE:
        if not master_password:
            try:
                master_password = getpass.getpass("Master password for API key encryption: ")
                if not master_password:
                    return (False, "Master password required")
            except (EOFError, KeyboardInterrupt):
                return (False, "Aborted")

        try:
            salt = _get_or_create_salt()
            key = _derive_key_from_password(master_password, salt)
            fernet = Fernet(key)
            encrypted = fernet.encrypt(api_key.encode())

            with open(ENCRYPTED_KEY_FILE, 'wb') as f:
                f.write(encrypted)

            # Restrict file permissions
            os.chmod(ENCRYPTED_KEY_FILE, 0o600)

            logger.info("API key stored encrypted with AES-256")
            return (True, "aes")
        except Exception as e:
            logger.error(f"AES encryption failed: {e}")
            return (False, f"Encryption failed: {e}")

    return (False, "Neither keyring nor cryptography available. Install: pip install keyring")


def get_stored_api_key(master_password: Optional[str] = None) -> Optional[str]:
    """
    Retrieves the securely stored API key.

    Args:
        master_password: Master password for AES decryption (if used)

    Returns:
        API key or None if not found/decryptable
    """
    # Method 1: Keyring
    if KEYRING_AVAILABLE:
        try:
            api_key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
            if api_key:
                logger.debug("API key loaded from system keyring")
                return api_key
        except Exception as e:
            logger.debug(f"Keyring retrieval failed: {e}")

    # Method 2: AES-encrypted file
    if CRYPTO_AVAILABLE and ENCRYPTED_KEY_FILE.exists():
        if not master_password:
            try:
                master_password = getpass.getpass("Master password: ")
            except (EOFError, KeyboardInterrupt):
                return None

        try:
            salt = _get_or_create_salt()
            key = _derive_key_from_password(master_password, salt)
            fernet = Fernet(key)

            with open(ENCRYPTED_KEY_FILE, 'rb') as f:
                encrypted = f.read()

            api_key = fernet.decrypt(encrypted).decode()
            logger.debug("API key loaded from encrypted file")
            return api_key
        except Exception as e:
            logger.warning(f"API key decryption failed: {e}")
            return None

    return None


def delete_stored_api_key() -> Tuple[bool, str]:
    """
    Deletes the stored API key.

    Returns:
        Tuple of (success, message)
    """
    deleted = []

    # Delete keyring
    if KEYRING_AVAILABLE:
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
            deleted.append("keyring")
        except Exception:
            pass  # Not present or error

    # Delete encrypted file
    if ENCRYPTED_KEY_FILE.exists():
        try:
            ENCRYPTED_KEY_FILE.unlink()
            deleted.append("encrypted file")
        except Exception as e:
            logger.error(f"Could not delete encrypted file: {e}")

    # Also delete salt
    if SALT_FILE.exists():
        try:
            SALT_FILE.unlink()
            deleted.append("salt")
        except Exception:
            pass

    if deleted:
        logger.info(f"API key deleted from: {', '.join(deleted)}")
        return (True, f"Deleted from: {', '.join(deleted)}")

    return (False, "No stored API key found")


# ============================================================================
# Interactive Setup
# ============================================================================

def setup_api_key_interactive() -> bool:
    """
    Interactive setup of the API key.

    Returns:
        True if successful, False otherwise
    """
    print()
    print("╔" + "═" * 63 + "╗")
    print("║  Mistral CLI - API Key Setup                                  ║")
    print("╠" + "═" * 63 + "╣")

    # Show available storage methods
    if KEYRING_AVAILABLE:
        print("║  ✅ System keyring available (recommended)                    ║")
    else:
        print("║  ❌ System keyring not available                              ║")
        print("║     → pip install keyring                                     ║")

    if CRYPTO_AVAILABLE:
        print("║  ✅ AES encryption available (fallback)                       ║")
    else:
        print("║  ❌ AES encryption not available                              ║")
        print("║     → pip install cryptography                                ║")

    print("╠" + "═" * 63 + "╣")
    print("║  Get API key: https://console.mistral.ai/                     ║")
    print("╚" + "═" * 63 + "╝")
    print()

    if not KEYRING_AVAILABLE and not CRYPTO_AVAILABLE:
        print("❌ No secure storage method available.")
        print("   Install: pip install keyring")
        return False

    try:
        api_key = getpass.getpass("Enter Mistral API key: ")

        if not api_key or not api_key.strip():
            print("❌ API key must not be empty.")
            return False

        # Simple validation
        if len(api_key) < 10:
            print("⚠️  Warning: API key seems too short.")

        success, method = store_api_key(api_key)

        if success:
            print(f"\n✅ API key successfully stored! (Method: {method})")
            return True
        else:
            print(f"\n❌ Storage failed: {method}")
            return False

    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        return False


def get_api_key_status() -> Dict[str, Any]:
    """
    Returns the status of API key storage.

    Returns:
        Dictionary with status information
    """
    status = {
        "keyring_available": KEYRING_AVAILABLE,
        "crypto_available": CRYPTO_AVAILABLE,
        "keyring_has_key": False,
        "encrypted_file_exists": ENCRYPTED_KEY_FILE.exists(),
        "env_var_set": bool(os.environ.get("MISTRAL_API_KEY")),
    }

    if KEYRING_AVAILABLE:
        try:
            key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
            status["keyring_has_key"] = bool(key)
        except Exception:
            pass

    return status
