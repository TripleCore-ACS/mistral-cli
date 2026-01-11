#!/usr/bin/env python3
"""
Mistral CLI - Transfer Tools
FTP and SFTP file uploads

Version: 1.5.2
"""

import os
from typing import Dict, Any, Optional
from ftplib import FTP

from ..core.config import DEFAULT_TIMEOUT
from ..core.logging_config import logger
from ..security.path_validator import validate_path
from ..security.sanitizers import sanitize_path
from .system import _get_user_confirmation, _create_result


# ============================================================================
# FTP Upload
# ============================================================================

def upload_ftp(
    local_file: str,
    host: str,
    username: Optional[str],
    password: Optional[str],
    remote_path: str,
    auto_confirm: bool = False
) -> Dict[str, Any]:
    """Uploads a file via FTP with security checks."""
    # Use environment variables as fallback for credentials
    ftp_user = username or os.environ.get('FTP_USER', '')
    ftp_pass = password or os.environ.get('FTP_PASS', '')

    logger.info(f"FTP Upload: {local_file} -> {host}:{remote_path}")

    print(f"\n[Tool Call] FTP Upload:")
    print(f"  Local file: {local_file}")
    print(f"  Server: {host}")
    print(f"  Remote path: {remote_path}")
    print(f"  User: {ftp_user or '(not set)'}")

    # Path validation for local file
    is_safe, message = validate_path(local_file)
    if not is_safe:
        logger.warning(f"Path validation failed: {local_file} - {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    if not ftp_user or not ftp_pass:
        logger.error("FTP credentials missing")
        return _create_result(
            success=False,
            error="FTP credentials missing. Set FTP_USER and FTP_PASS environment variables or pass them directly."
        )

    if not auto_confirm and not _get_user_confirmation("Upload?"):
        logger.info("User declined upload")
        return _create_result(success=False, error="User declined upload")

    try:
        local = sanitize_path(local_file)

        if not os.path.exists(local):
            return _create_result(success=False, error=f"Local file not found: {local_file}")

        with FTP(host, timeout=DEFAULT_TIMEOUT) as ftp:
            ftp.login(ftp_user, ftp_pass)

            with open(local, 'rb') as f:
                ftp.storbinary(f'STOR {remote_path}', f)

        logger.info("FTP upload successful")
        return _create_result(
            success=True,
            message=f"File uploaded successfully to {host}:{remote_path}"
        )
    except Exception as e:
        logger.error(f"FTP upload failed: {e}")
        return _create_result(success=False, error=f"FTP upload failed: {str(e)}")


# ============================================================================
# SFTP Upload
# ============================================================================

def upload_sftp(
    local_file: str,
    host: str,
    port: int,
    username: Optional[str],
    password: Optional[str],
    key_path: Optional[str],
    remote_path: str,
    auto_confirm: bool = False
) -> Dict[str, Any]:
    """
    Uploads a file securely via SFTP.

    Supports authentication via:
    - Password (SFTP_PASS or password parameter)
    - SSH Private Key (SFTP_KEY_PATH or key_path parameter)

    Args:
        local_file: Path to the local file
        host: SFTP server hostname
        port: SFTP server port (default: 22)
        username: Username (or SFTP_USER env variable)
        password: Password (or SFTP_PASS env variable)
        key_path: Path to SSH private key (or SFTP_KEY_PATH env variable)
        remote_path: Destination path on the server
        auto_confirm: Automatic confirmation

    Returns:
        Result dictionary
    """
    # Use environment variables as fallback for credentials
    sftp_user = username or os.environ.get('SFTP_USER', '')
    sftp_pass = password or os.environ.get('SFTP_PASS', '')
    sftp_key = key_path or os.environ.get('SFTP_KEY_PATH', '')

    logger.info(f"SFTP Upload: {local_file} -> {host}:{port}{remote_path}")

    print(f"\n[Tool Call] SFTP Upload (encrypted):")
    print(f"  Local file: {local_file}")
    print(f"  Server: {host}:{port}")
    print(f"  Remote path: {remote_path}")
    print(f"  User: {sftp_user or '(not set)'}")
    print(f"  Auth method: {'SSH-Key' if sftp_key else 'Password'}")

    # Check if paramiko is available
    try:
        import paramiko
    except ImportError:
        logger.error("paramiko not installed")
        return _create_result(
            success=False,
            error="SFTP requires the 'paramiko' library. Install with: pip install paramiko"
        )

    # Path validation for local file
    is_safe, message = validate_path(local_file)
    if not is_safe:
        logger.warning(f"Path validation failed: {local_file} - {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    if not sftp_user:
        logger.error("SFTP username missing")
        return _create_result(
            success=False,
            error="SFTP username missing. Set SFTP_USER environment variable or pass username."
        )

    # Check auth method
    if not sftp_pass and not sftp_key:
        logger.error("SFTP authentication missing")
        return _create_result(
            success=False,
            error="SFTP auth missing. Set SFTP_PASS or SFTP_KEY_PATH environment variable."
        )

    if not auto_confirm and not _get_user_confirmation("Upload?"):
        logger.info("User declined SFTP upload")
        return _create_result(success=False, error="User declined upload")

    try:
        local = sanitize_path(local_file)

        if not os.path.exists(local):
            return _create_result(success=False, error=f"Local file not found: {local_file}")

        # Establish SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connection parameters
        connect_kwargs = {
            'hostname': host,
            'port': port,
            'username': sftp_user,
            'timeout': DEFAULT_TIMEOUT
        }

        # Authentication
        if sftp_key:
            # SSH-Key authentication
            key_file = sanitize_path(sftp_key)
            if not os.path.exists(key_file):
                return _create_result(success=False, error=f"SSH-Key not found: {sftp_key}")

            # Try different key types
            try:
                private_key = paramiko.RSAKey.from_private_key_file(key_file)
            except paramiko.SSHException:
                try:
                    private_key = paramiko.Ed25519Key.from_private_key_file(key_file)
                except paramiko.SSHException:
                    try:
                        private_key = paramiko.ECDSAKey.from_private_key_file(key_file)
                    except paramiko.SSHException:
                        return _create_result(
                            success=False,
                            error="SSH-Key could not be read. Supported: RSA, Ed25519, ECDSA"
                        )

            connect_kwargs['pkey'] = private_key
            logger.info("SFTP: Using SSH-Key authentication")
        else:
            # Password authentication
            connect_kwargs['password'] = sftp_pass
            logger.info("SFTP: Using password authentication")

        # Connect
        ssh.connect(**connect_kwargs)

        # Open SFTP session
        sftp = ssh.open_sftp()

        # Upload file
        file_size = os.path.getsize(local)
        sftp.put(local, remote_path)

        # Close connection
        sftp.close()
        ssh.close()

        logger.info(f"SFTP upload successful: {file_size} bytes")
        return _create_result(
            success=True,
            message=f"File uploaded securely to {host}:{remote_path}",
            file_size=file_size,
            protocol="SFTP",
            encrypted=True
        )

    except Exception as e:
        # Specific error handling
        if 'paramiko' in str(type(e).__module__):
            if 'Authentication' in str(type(e).__name__):
                logger.error("SFTP authentication failed")
                return _create_result(success=False, error="SFTP authentication failed. Check username/password/key.")
            elif 'SSH' in str(type(e).__name__):
                logger.error(f"SSH error: {e}")
                return _create_result(success=False, error=f"SSH error: {str(e)}")

        logger.error(f"SFTP upload failed: {e}")
        return _create_result(success=False, error=f"SFTP upload failed: {str(e)}")
