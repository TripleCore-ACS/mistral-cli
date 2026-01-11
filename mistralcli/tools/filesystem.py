#!/usr/bin/env python3
"""
Mistral CLI - Filesystem Tools
File and folder operations with security checks

Version: 1.5.2
"""

import os
import shutil
from typing import Dict, Any

from ..core.logging_config import logger
from ..security.path_validator import validate_path
from ..security.sanitizers import sanitize_path
from ..utils.helpers import check_file_operation_safety
from .system import _get_user_confirmation, _create_result


# ============================================================================
# File Operations
# ============================================================================

def read_file(file_path: str) -> Dict[str, Any]:
    """Reads the contents of a file with path validation."""
    logger.info(f"Reading file: {file_path}")
    print(f"\n[Tool Call] Read file: {file_path}")

    # Path validation
    is_safe, message = validate_path(file_path)
    if not is_safe:
        logger.warning(f"Path validation failed: {file_path} - {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    try:
        path = sanitize_path(file_path)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"File read: {len(content)} characters")
        return _create_result(success=True, content=content)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return _create_result(success=False, error=f"File not found: {file_path}")
    except PermissionError:
        logger.error(f"No permission: {file_path}")
        return _create_result(success=False, error=f"No permission to read: {file_path}")
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return _create_result(success=False, error=str(e))


def write_file(
    file_path: str,
    content: str,
    auto_confirm: bool = False
) -> Dict[str, Any]:
    """Writes content to a file with path validation."""
    logger.info(f"Writing file: {file_path}")

    print(f"\n[Tool Call] Write file: {file_path}")
    preview = content[:100] + "..." if len(content) > 100 else content
    print(f"  Content: {preview}")

    # Path validation
    is_safe, message = validate_path(file_path)
    if not is_safe:
        logger.warning(f"Path validation failed: {file_path} - {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    if not auto_confirm and not _get_user_confirmation("Write?"):
        logger.info("User declined write operation")
        return _create_result(success=False, error="User declined write operation")

    try:
        path = sanitize_path(file_path)
        # Create directory if necessary
        parent_dir = os.path.dirname(path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"File written: {len(content)} characters")
        return _create_result(success=True, message="File written successfully")
    except PermissionError:
        logger.error(f"No write permission: {file_path}")
        return _create_result(success=False, error=f"No write permission: {file_path}")
    except Exception as e:
        logger.error(f"Error writing file: {e}")
        return _create_result(success=False, error=str(e))


def rename_file(
    old_path: str,
    new_path: str,
    auto_confirm: bool = False
) -> Dict[str, Any]:
    """Renames a file with path validation."""
    logger.info(f"Renaming: {old_path} -> {new_path}")

    print(f"\n[Tool Call] Rename file:")
    print(f"  From: {old_path}")
    print(f"  To: {new_path}")

    # Path validations
    for path, label in [(old_path, "Source path"), (new_path, "Destination path")]:
        is_safe, message = validate_path(path)
        if not is_safe:
            logger.warning(f"{label} validation failed: {path} - {message}")
            print(f"  ⚠️  {label}: {message}")
            return _create_result(success=False, error=f"{label} unsafe: {message}")

    if not auto_confirm and not _get_user_confirmation("Rename?"):
        logger.info("User declined rename operation")
        return _create_result(success=False, error="User declined rename operation")

    try:
        old = sanitize_path(old_path)
        new = sanitize_path(new_path)
        os.rename(old, new)
        logger.info("Rename successful")
        return _create_result(success=True, message=f"Successfully renamed from {old} to {new}")
    except FileNotFoundError:
        logger.error(f"File not found: {old_path}")
        return _create_result(success=False, error=f"File not found: {old_path}")
    except PermissionError:
        logger.error(f"No permission: {old_path}")
        return _create_result(success=False, error=f"No permission to rename")
    except Exception as e:
        logger.error(f"Rename failed: {e}")
        return _create_result(success=False, error=str(e))


def copy_file(
    source: str,
    destination: str,
    auto_confirm: bool = False
) -> Dict[str, Any]:
    """Copies a file or folder with security checks."""
    logger.info(f"Copying: {source} -> {destination}")

    print(f"\n[Tool Call] Copy file/folder:")
    print(f"  From: {source}")
    print(f"  To: {destination}")

    # Security check for file operations
    is_safe, message = check_file_operation_safety("copy", source, destination)
    if not is_safe:
        logger.warning(f"Security check failed: {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    if not auto_confirm and not _get_user_confirmation("Copy?"):
        logger.info("User declined copy operation")
        return _create_result(success=False, error="User declined copy operation")

    try:
        src = sanitize_path(source)
        dst = sanitize_path(destination)

        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            # Create destination directory if necessary
            parent_dir = os.path.dirname(dst)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            shutil.copy2(src, dst)

        logger.info("Copy successful")
        return _create_result(success=True, message=f"Successfully copied from {src} to {dst}")
    except FileNotFoundError:
        logger.error(f"File not found: {source}")
        return _create_result(success=False, error=f"File not found: {source}")
    except PermissionError:
        logger.error(f"No permission to copy")
        return _create_result(success=False, error="No permission to copy")
    except Exception as e:
        logger.error(f"Copy failed: {e}")
        return _create_result(success=False, error=str(e))


def move_file(
    source: str,
    destination: str,
    auto_confirm: bool = False
) -> Dict[str, Any]:
    """Moves a file or folder with security checks."""
    logger.info(f"Moving: {source} -> {destination}")

    print(f"\n[Tool Call] Move file/folder:")
    print(f"  From: {source}")
    print(f"  To: {destination}")

    # Security check for file operations
    is_safe, message = check_file_operation_safety("move", source, destination)
    if not is_safe:
        logger.warning(f"Security check failed: {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    if not auto_confirm and not _get_user_confirmation("Move?"):
        logger.info("User declined move operation")
        return _create_result(success=False, error="User declined move operation")

    try:
        src = sanitize_path(source)
        dst = sanitize_path(destination)
        # Create destination directory if necessary
        parent_dir = os.path.dirname(dst)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        shutil.move(src, dst)
        logger.info("Move successful")
        return _create_result(success=True, message=f"Successfully moved from {src} to {dst}")
    except FileNotFoundError:
        logger.error(f"File not found: {source}")
        return _create_result(success=False, error=f"File not found: {source}")
    except PermissionError:
        logger.error(f"No permission to move")
        return _create_result(success=False, error="No permission to move")
    except Exception as e:
        logger.error(f"Move failed: {e}")
        return _create_result(success=False, error=str(e))
