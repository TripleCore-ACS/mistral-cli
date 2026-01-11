#!/usr/bin/env python3
"""
Mistral CLI - Configuration Module
Central configuration, constants and environment variables

Version: 1.5.2
"""

import os
import sys
from typing import Optional
from pathlib import Path
from enum import Enum

# Try to load python-dotenv (optional)
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# Try to load keyring (optional, for secure key storage)
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

# Try to load cryptography (optional, for AES fallback)
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


# ============================================================================
# General Constants
# ============================================================================

DEFAULT_MODEL = "mistral-small-latest"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TIMEOUT = 30

# Log file in home directory
LOG_FILE = Path.home() / ".mistral-cli.log"

# Secure storage constants
KEYRING_SERVICE = "mistral-cli"
KEYRING_USERNAME = "api_key"
ENCRYPTED_KEY_FILE = Path.home() / ".mistral-cli-key.enc"
SALT_FILE = Path.home() / ".mistral-cli-salt"


# ============================================================================
# Security Constants
# ============================================================================

class RiskLevel(Enum):
    """Risk levels for commands and actions."""
    CRITICAL = "CRITICAL"  # Block immediately
    HIGH = "HIGH"          # Block with warning
    MEDIUM = "MEDIUM"      # Warning, confirmation required
    LOW = "LOW"            # Notice
    SAFE = "SAFE"          # Safe


# ============================================================================
# Extended Security Patterns (v1.2.0)
# ============================================================================

# Categories of dangerous commands
DANGEROUS_COMMANDS = {
    # Destructive commands
    'rm', 'rmdir', 'unlink', 'shred',
    # Formatting / Disk
    'mkfs', 'fdisk', 'parted', 'format',
    # Permissions (critical on system paths)
    'chmod', 'chown', 'chattr',
    # Network (exfiltration risk)
    'nc', 'netcat', 'ncat',
    # Shell execution (indirect execution)
    'eval', 'exec', 'source',
    # System-critical
    'shutdown', 'reboot', 'init', 'systemctl', 'halt', 'poweroff',
    'kill', 'killall', 'pkill',
    # User/Privilege Escalation
    'sudo', 'su', 'passwd', 'useradd', 'userdel', 'usermod',
    'visudo', 'chpasswd',
    # Disk operations
    'dd', 'wipefs', 'sgdisk', 'gdisk',
}

# Commands that are only dangerous with certain arguments
CONDITIONAL_DANGEROUS = {
    'rm': ['-r', '-f', '-rf', '-fr', '--recursive', '--force', '-R'],
    'chmod': ['777', '000', '666', '-R', '--recursive'],
    'chown': ['-R', '--recursive'],
    'curl': ['|', '-o', '--output'],  # Download + Execute or overwrite
    'wget': ['|', '-O', '--output-document'],
    'mv': ['/etc', '/usr', '/var', '/boot', '/bin', '/sbin', '/lib'],
    'cp': ['--no-preserve', '/etc', '/usr', '/var', '/boot'],
}

# Dangerous patterns (Regex) - EXTENDED v1.2.0
DANGEROUS_PATTERNS = [
    # Command chaining with destructive commands
    r';\s*rm\b',                        # ; rm
    r'&&\s*rm\b',                       # && rm
    r'\|\|\s*rm\b',                     # || rm
    r'\|\s*rm\b',                       # | rm

    # Subshell with dangerous commands
    r'\$\([^)]*\brm\b[^)]*\)',          # $(rm ...)
    r'`[^`]*\brm\b[^`]*`',              # `rm ...`

    # Eval and indirect execution
    r'\beval\b',                        # eval anything
    r'\bexec\b',                        # exec anything

    # Device write operations
    r'>\s*/dev/sd[a-z]',                # Write to SATA/SAS disk
    r'>\s*/dev/nvme',                   # Write to NVMe
    r'>\s*/dev/hd[a-z]',                # Write to IDE disk
    r'>\s*/dev/vd[a-z]',                # Write to virtio disk

    # Encoded execution
    r'\bbase64\b.*\|\s*bash',           # base64 decode to bash
    r'\bbase64\b.*\|\s*sh',             # base64 decode to sh
    r'\bbase64\b.*\|\s*zsh',            # base64 decode to zsh
    r'\bxxd\b.*\|\s*bash',              # hex decode to bash

    # Fork bomb variants
    r':\(\)\s*{\s*:\|:&\s*}\s*;:',      # Classic fork bomb
    r':\(\)\s*{\s*:\|:&\s*};\s*:',      # Fork bomb variant

    # DD dangerous operations
    r'\bdd\b.*\bof=/dev/',              # dd to device
    r'\bdd\b.*\bif=/dev/(zero|random|urandom).*\bof=',  # dd wipe

    # Direct deletion of critical paths
    r'\brm\s+(-[rfRF]+\s+)?/',          # rm starting with /
    r'\brm\s+(-[rfRF]+\s+)?~',          # rm in home
    r'\brm\s+(-[rfRF]+\s+)?\.',         # rm dotfiles

    # Overwrite system configuration
    r'>\s*/etc/',                       # Overwrite /etc
    r'>>\s*/etc/',                      # Append to /etc
    r'>\s*~/\.',                        # Overwrite dotfiles

    # History manipulation (covering tracks)
    r'\bhistory\s+-c',                  # Clear history
    r'>\s*~/\.bash_history',            # Overwrite bash history
    r'>\s*~/\.zsh_history',             # Overwrite zsh history

    # Crontab manipulation
    r'\bcrontab\s+-r',                  # Remove crontab

    # Network backdoors
    r'\bnc\b.*-[elp]',                  # netcat listener
    r'\bncat\b.*-[elp]',                # ncat listener

    # Remote code execution
    r'(curl|wget)\s+.*\|\s*(bash|sh|zsh|python|perl|ruby)',
    r'(curl|wget)\s+-[^\s]*o[^\s]*\s+.*&&\s*(bash|sh|chmod)',
]

# Dangerous target directories/files
DANGEROUS_TARGETS = [
    # System-critical directories
    '/', '/etc', '/usr', '/var', '/boot', '/root', '/home',
    '/bin', '/sbin', '/lib', '/lib64', '/opt',
    '/dev', '/proc', '/sys', '/run',

    # Home directory variants
    '~', '$HOME',

    # Sensitive files
    '.ssh', '.gnupg', '.gpg',
    '.bashrc', '.zshrc', '.profile', '.bash_profile', '.bash_logout',
    '.env', '.git', '.gitconfig',
    '.config', '.local',
    '.aws', '.azure', '.kube',

    # Credentials
    'id_rsa', 'id_ed25519', 'id_ecdsa',
    '.netrc', '.npmrc', '.pypirc',
]

# Commands that can act as interpreters
INTERPRETER_COMMANDS = {
    'python', 'python3', 'python2',
    'perl', 'ruby', 'node', 'nodejs',
    'php', 'lua', 'tclsh', 'wish',
    'awk', 'gawk', 'nawk',
}

# Shell commands
SHELL_COMMANDS = {
    'bash', 'sh', 'zsh', 'fish', 'csh', 'tcsh', 'dash', 'ksh',
}

# Allowed hosts for URL fetches (whitelist)
ALLOWED_URL_SCHEMES = ["http", "https", "ftp", "ftps"]

# Private/local IP ranges that should be blocked
PRIVATE_IP_RANGES = [
    "127.0.0.0/8",      # Localhost
    "10.0.0.0/8",       # Private A
    "172.16.0.0/12",    # Private B
    "192.168.0.0/16",   # Private C
    "169.254.0.0/16",   # Link-local
    "::1/128",          # IPv6 Localhost
    "fc00::/7",         # IPv6 Private
    "fe80::/10",        # IPv6 Link-local
]


# ============================================================================
# Environment Variables & Configuration
# ============================================================================

def load_environment() -> None:
    """
    Loads environment variables from .env file (if present).
    Searches in the following order:
    1. Current directory (.env)
    2. Home directory (~/.mistral-cli.env)
    """
    if not DOTENV_AVAILABLE:
        # No logging here, as logger is not yet initialized
        return

    # Possible .env paths
    env_paths = [
        Path.cwd() / ".env",
        Path.home() / ".mistral-cli.env",
        Path.home() / ".env"
    ]

    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            # Logging occurs in logging_config after logger initialization
            return


# Load environment variables on import
load_environment()
