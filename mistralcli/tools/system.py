#!/usr/bin/env python3
"""
Mistral CLI - System Tools
Bash command execution with security checks

Version: 1.5.2
"""

import os
import subprocess
from typing import Dict, Any

from ..core.config import DEFAULT_TIMEOUT
from ..core.logging_config import logger
from ..security.command_validator import get_command_risk_info
from ..utils.formatting import format_risk_warning


# ============================================================================
# Helper Functions
# ============================================================================

def _get_user_confirmation(prompt: str) -> bool:
    """
    Asks the user for confirmation.

    Args:
        prompt: The question to ask the user

    Returns:
        True if confirmed, False otherwise
    """
    response = input(f"  {prompt} (y/n): ").strip().lower()
    return response in ['y', 'yes', 'j', 'ja']


def _create_result(
    success: bool,
    message: str = None,
    error: str = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Creates a standardized result dictionary.

    Args:
        success: Whether the operation was successful
        message: Success message
        error: Error message
        **kwargs: Additional fields

    Returns:
        Result dictionary
    """
    result: Dict[str, Any] = {"success": success}
    if message:
        result["message"] = message
    if error:
        result["error"] = error
    result.update(kwargs)
    return result


# ============================================================================
# Bash Command Execution
# ============================================================================

def execute_bash_command(
    command: str,
    explanation: str,
    auto_confirm: bool = False
) -> Dict[str, Any]:
    """Executes a Bash command with extended security checks."""
    logger.info(f"Bash command: {command}")
    logger.debug(f"Explanation: {explanation}")

    print(f"\n[Tool Call] Execute Bash command:")
    print(f"  Command: {command}")
    print(f"  Explanation: {explanation}")

    # Extended security check
    risk_info = get_command_risk_info(command)

    if risk_info["is_blocked"]:
        logger.warning(f"Dangerous command blocked: {command}")
        print(format_risk_warning(risk_info))
        return _create_result(
            success=False,
            error=f"Command blocked: {risk_info['description']}",
            risk_level=risk_info["risk_level"],
            category=risk_info["category"]
        )

    if risk_info["needs_confirmation"]:
        print(format_risk_warning(risk_info))
        if not _get_user_confirmation("Execute anyway?"):
            logger.info("User declined execution of medium-risk command")
            return _create_result(success=False, message="User declined execution")

    if not auto_confirm and risk_info["risk_level"] == "SAFE":
        if not _get_user_confirmation("Execute?"):
            logger.info("User declined execution")
            return _create_result(success=False, message="User declined execution")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=DEFAULT_TIMEOUT
        )

        output = result.stdout if result.stdout else result.stderr
        logger.info(f"Command executed, exit code: {result.returncode}")

        return _create_result(
            success=result.returncode == 0,
            output=output,
            exit_code=result.returncode
        )
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout for command: {command}")
        return _create_result(success=False, message=f"Command exceeded timeout ({DEFAULT_TIMEOUT}s)")
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return _create_result(success=False, error=str(e))
