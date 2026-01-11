#!/usr/bin/env python3
"""
Mistral CLI - Command Validator
Functions for validating and analyzing shell commands

Version: 1.5.2
"""

import re
import shlex
from typing import Tuple, Dict, Any

from ..core.config import (
    RiskLevel,
    DANGEROUS_COMMANDS,
    CONDITIONAL_DANGEROUS,
    DANGEROUS_PATTERNS,
    DANGEROUS_TARGETS,
    INTERPRETER_COMMANDS,
    SHELL_COMMANDS
)
from ..core.logging_config import logger


# ============================================================================
# Command Security (v1.2.0)
# ============================================================================

def is_dangerous_command(command: str) -> Tuple[bool, str]:
    """
    Checks if a command is potentially dangerous.

    This function analyzes shell commands for various attack vectors:
    - Directly destructive commands (rm, mkfs, dd, etc.)
    - Command chaining (;, &&, ||, |)
    - Subshell execution ($(), ``)
    - Encoded execution (base64, xxd)
    - Interpreter execution (python -c, bash -c, etc.)
    - Dangerous target directories

    Args:
        command: The shell command to check

    Returns:
        Tuple[bool, str]: (is_dangerous, reason)

    Examples:
        >>> is_dangerous_command("ls -la")
        (False, "")
        >>> is_dangerous_command("rm -rf /")
        (True, "Dangerous pattern detected: rm with critical path")
        >>> is_dangerous_command("echo hi && rm -rf ~")
        (True, "Dangerous command in chain: rm with dangerous arguments")
    """
    if not command or not command.strip():
        return False, ""

    command = command.strip()

    # 1. Pattern-based detection (fastest check first)
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, f"Dangerous pattern detected: {pattern[:30]}..."

    # 2. Detect command chaining and check each part
    chain_separators = [';', '&&', '||', '\n']
    has_chaining = any(sep in command for sep in chain_separators)

    # Handle pipe separately (not always dangerous)
    has_pipe = '|' in command and 'base64' not in command.lower()

    if has_chaining:
        # Split by separators
        parts = re.split(r'[;&\n]+|&&|\|\|', command)
        for part in parts:
            part = part.strip()
            if part:
                is_dangerous, reason = _check_single_command(part)
                if is_dangerous:
                    return True, f"Dangerous command in chain: {reason}"

    # 3. Subshell detection (recursive)
    subshell_patterns = [
        (r'\$\(([^)]+)\)', 'Command Substitution $()'),
        (r'`([^`]+)`', 'Backtick Substitution'),
    ]
    for pattern, subshell_type in subshell_patterns:
        matches = re.findall(pattern, command)
        for match in matches:
            is_dangerous, reason = is_dangerous_command(match)
            if is_dangerous:
                return True, f"Dangerous command in {subshell_type}: {reason}"

    # 4. Analyze pipe chains
    if has_pipe:
        pipe_parts = command.split('|')
        for part in pipe_parts:
            part = part.strip()
            if part:
                is_dangerous, reason = _check_single_command(part)
                if is_dangerous:
                    return True, f"Dangerous command in pipe: {reason}"

    # 5. Check single command (if no chaining)
    if not has_chaining and not has_pipe:
        return _check_single_command(command)

    return False, ""


def _check_single_command(command: str) -> Tuple[bool, str]:
    """
    Checks a single command (without chaining).

    Args:
        command: Single shell command

    Returns:
        Tuple[bool, str]: (is_dangerous, reason)
    """
    command = command.strip()

    if not command:
        return False, ""

    try:
        # Safe parsing with shlex
        tokens = shlex.split(command)
    except ValueError as e:
        # Invalid quoting could indicate manipulation
        logger.warning(f"Invalid shell quoting in command: {command} ({e})")
        return True, f"Invalid shell quoting: {e}"

    if not tokens:
        return False, ""

    # Extract base command (without path like /usr/bin/)
    base_cmd = tokens[0].split('/')[-1].lower()
    args = tokens[1:] if len(tokens) > 1 else []

    # Special case: mkfs.* variants (mkfs.ext4, mkfs.xfs, etc.)
    if base_cmd.startswith('mkfs'):
        return True, f"Filesystem formatting: {base_cmd}"

    # 1. Interpreter with code execution
    if base_cmd in INTERPRETER_COMMANDS:
        code_exec_flags = ['-c', '-e', '--eval', '-exec']
        if any(flag in args for flag in code_exec_flags):
            return True, f"Code execution via {base_cmd}"

    # 2. Shell with -c flag
    if base_cmd in SHELL_COMMANDS:
        if '-c' in args:
            return True, f"Shell execution via {base_cmd} -c"

    # 3. Directly dangerous commands
    if base_cmd in DANGEROUS_COMMANDS:
        # Some commands are only dangerous with certain args
        if base_cmd in CONDITIONAL_DANGEROUS:
            dangerous_args = CONDITIONAL_DANGEROUS[base_cmd]
            args_str = ' '.join(args).lower()

            for dangerous_arg in dangerous_args:
                if dangerous_arg in args or dangerous_arg in args_str:
                    return True, f"{base_cmd} with dangerous arguments: {dangerous_arg}"

            # Without dangerous args, the command is allowed
            # (e.g., "rm file.txt" without -rf)

            # But still check for dangerous targets
            for arg in args:
                for target in DANGEROUS_TARGETS:
                    if arg == target or arg.startswith(target + '/') or arg.startswith(target):
                        return True, f"{base_cmd} on dangerous target: {arg}"

            return False, ""
        else:
            # Always dangerous (e.g., mkfs, shutdown)
            return True, f"Dangerous command: {base_cmd}"

    # 4. Conditionally dangerous commands
    if base_cmd in CONDITIONAL_DANGEROUS:
        dangerous_args = CONDITIONAL_DANGEROUS[base_cmd]
        for arg in args:
            if arg in dangerous_args:
                return True, f"{base_cmd} with dangerous arguments: {arg}"
            # Also check combinations like -rf
            if arg.startswith('-') and any(da.lstrip('-') in arg for da in dangerous_args if da.startswith('-')):
                return True, f"{base_cmd} with dangerous arguments: {arg}"

    # 5. Check dangerous targets (for modifying commands)
    modifying_commands = {'mv', 'cp', 'ln', 'touch', 'mkdir', 'tee'}
    if base_cmd in modifying_commands:
        for arg in args:
            if arg.startswith('-'):
                continue  # Skip flags
            for target in DANGEROUS_TARGETS:
                if arg == target or arg.startswith(target + '/'):
                    return True, f"{base_cmd} on dangerous target: {arg}"

    # 6. Redirect to dangerous targets (already in patterns, but for safety)
    if '>' in command:
        redirect_match = re.search(r'>+\s*(\S+)', command)
        if redirect_match:
            redirect_target = redirect_match.group(1)
            for target in DANGEROUS_TARGETS:
                if redirect_target.startswith(target):
                    return True, f"Redirect to dangerous target: {redirect_target}"

    return False, ""


def request_confirmation(command: str, reason: str) -> bool:
    """
    Asks the user for confirmation for a command detected as dangerous.

    Args:
        command: The dangerous command
        reason: Reason why the command was detected as dangerous

    Returns:
        bool: True if the user confirms, False otherwise
    """
    print()
    print("=" * 60)
    print("⚠️  WARNING: Potentially dangerous command detected!")
    print("=" * 60)
    print(f"  Command: {command}")
    print(f"  Reason:  {reason}")
    print("=" * 60)
    print()

    logger.warning(f"Dangerous command detected: {command} - Reason: {reason}")

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = input("Do you want to execute this command anyway? [y/N]: ").strip().lower()

            if response in ['j', 'ja', 'y', 'yes']:
                logger.info(f"User confirmed dangerous command: {command}")
                return True

            if response in ['n', 'nein', 'no', '']:
                logger.info(f"User rejected dangerous command: {command}")
                return False

            print("Please answer with 'y' (yes) or 'n' (no)")

        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return False

    print("Too many invalid inputs. Command will not be executed.")
    return False


# ============================================================================
# Legacy Functions (Compatibility with existing code)
# ============================================================================

def analyze_command_risk(command: str) -> Tuple[RiskLevel, str, str]:
    """
    Analyzes a command and returns risk level, category and description.
    (Legacy function for compatibility)

    Args:
        command: The command to analyze

    Returns:
        Tuple of (RiskLevel, category, description)
    """
    is_dangerous, reason = is_dangerous_command(command)

    if is_dangerous:
        if any(keyword in reason.lower() for keyword in ['critical', 'fork', 'dd', 'mkfs']):
            return (RiskLevel.CRITICAL, "security", reason)
        elif any(keyword in reason.lower() for keyword in ['rm', 'chmod', 'chown']):
            return (RiskLevel.HIGH, "filesystem", reason)
        else:
            return (RiskLevel.MEDIUM, "general", reason)

    return (RiskLevel.SAFE, "none", "No danger detected")


def get_command_risk_info(command: str) -> Dict[str, Any]:
    """
    Returns detailed risk information for a command.

    Args:
        command: The command to check

    Returns:
        Dictionary with risk details
    """
    is_dangerous, reason = is_dangerous_command(command)
    risk_level, category, description = analyze_command_risk(command)

    return {
        "command": command,
        "risk_level": risk_level.value,
        "is_blocked": risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH],
        "needs_confirmation": risk_level == RiskLevel.MEDIUM,
        "category": category,
        "description": description,
        "reason": reason,
        "recommendation": _get_risk_recommendation(risk_level)
    }


def _get_risk_recommendation(risk_level: RiskLevel) -> str:
    """Returns a recommendation based on the risk level."""
    recommendations = {
        RiskLevel.CRITICAL: "This command is extremely dangerous and will be blocked.",
        RiskLevel.HIGH: "This command is dangerous and will be blocked. Use safer alternatives.",
        RiskLevel.MEDIUM: "This command requires special caution. Please confirm execution.",
        RiskLevel.LOW: "This command is potentially sensitive. Check the result.",
        RiskLevel.SAFE: "No special security concerns."
    }
    return recommendations.get(risk_level, "Unknown risk level.")
