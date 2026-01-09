#!/usr/bin/env python3
"""
Mistral CLI - Utilities Module
Zentrale Funktionen für Client-Initialisierung, Logging, Konfiguration und Sicherheit

Version: 1.3.0
"""

import os
import sys
import re
import shlex
import logging
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path
from enum import Enum
from urllib.parse import urlparse
import ipaddress

# Versuche python-dotenv zu laden (optional)
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# Versuche keyring zu laden (optional, für sichere Key-Speicherung)
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

# Versuche cryptography zu laden (optional, für AES-Fallback)
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

import getpass
import hashlib
import secrets

# Mistral Client Import
from mistralai import Mistral


# ============================================================================
# Konstanten
# ============================================================================

DEFAULT_MODEL = "mistral-small-latest"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TIMEOUT = 30

# Log-Datei im Home-Verzeichnis
LOG_FILE = Path.home() / ".mistral-cli.log"

# Sichere Speicherung Konstanten
KEYRING_SERVICE = "mistral-cli"
KEYRING_USERNAME = "api_key"
ENCRYPTED_KEY_FILE = Path.home() / ".mistral-cli-key.enc"
SALT_FILE = Path.home() / ".mistral-cli-salt"


# ============================================================================
# Sicherheits-Konstanten
# ============================================================================

class RiskLevel(Enum):
    """Risikostufen für Befehle und Aktionen."""
    CRITICAL = "CRITICAL"  # Sofort blockieren
    HIGH = "HIGH"          # Blockieren mit Warnung
    MEDIUM = "MEDIUM"      # Warnung, Bestätigung erforderlich
    LOW = "LOW"            # Hinweis
    SAFE = "SAFE"          # Sicher


# ============================================================================
# Erweiterte Sicherheits-Patterns (v1.2.0)
# ============================================================================

# Kategorien von gefährlichen Befehlen
DANGEROUS_COMMANDS = {
    # Destruktive Befehle
    'rm', 'rmdir', 'unlink', 'shred',
    # Formatierung / Disk
    'mkfs', 'fdisk', 'parted', 'format',
    # Permissions (kritisch bei System-Pfaden)
    'chmod', 'chown', 'chattr',
    # Netzwerk (Exfiltration-Risiko)
    'nc', 'netcat', 'ncat',
    # Shell-Ausführung (indirekte Ausführung)
    'eval', 'exec', 'source',
    # System-kritisch
    'shutdown', 'reboot', 'init', 'systemctl', 'halt', 'poweroff',
    'kill', 'killall', 'pkill',
    # User/Privilege Escalation
    'sudo', 'su', 'passwd', 'useradd', 'userdel', 'usermod',
    'visudo', 'chpasswd',
    # Disk-Operationen
    'dd', 'wipefs', 'sgdisk', 'gdisk',
}

# Befehle die nur mit bestimmten Argumenten gefährlich sind
CONDITIONAL_DANGEROUS = {
    'rm': ['-r', '-f', '-rf', '-fr', '--recursive', '--force', '-R'],
    'chmod': ['777', '000', '666', '-R', '--recursive'],
    'chown': ['-R', '--recursive'],
    'curl': ['|', '-o', '--output'],  # Download + Execute oder Überschreiben
    'wget': ['|', '-O', '--output-document'],
    'mv': ['/etc', '/usr', '/var', '/boot', '/bin', '/sbin', '/lib'],
    'cp': ['--no-preserve', '/etc', '/usr', '/var', '/boot'],
}

# Gefährliche Muster (Regex) - ERWEITERT v1.2.0
DANGEROUS_PATTERNS = [
    # Command Chaining mit destruktiven Befehlen
    r';\s*rm\b',                        # ; rm
    r'&&\s*rm\b',                       # && rm
    r'\|\|\s*rm\b',                     # || rm
    r'\|\s*rm\b',                       # | rm
    
    # Subshell mit gefährlichen Befehlen
    r'\$\([^)]*\brm\b[^)]*\)',          # $(rm ...)
    r'`[^`]*\brm\b[^`]*`',              # `rm ...`
    
    # Eval und indirekte Ausführung
    r'\beval\b',                        # eval anything
    r'\bexec\b',                        # exec anything
    
    # Device-Schreiboperationen
    r'>\s*/dev/sd[a-z]',                # Write to SATA/SAS disk
    r'>\s*/dev/nvme',                   # Write to NVMe
    r'>\s*/dev/hd[a-z]',                # Write to IDE disk
    r'>\s*/dev/vd[a-z]',                # Write to virtio disk
    
    # Encoded Execution
    r'\bbase64\b.*\|\s*bash',           # base64 decode to bash
    r'\bbase64\b.*\|\s*sh',             # base64 decode to sh
    r'\bbase64\b.*\|\s*zsh',            # base64 decode to zsh
    r'\bxxd\b.*\|\s*bash',              # hex decode to bash
    
    # Fork Bomb Varianten
    r':\(\)\s*{\s*:\|:&\s*}\s*;:',      # Classic fork bomb
    r':\(\)\s*{\s*:\|:&\s*};\s*:',      # Fork bomb variant
    
    # DD gefährliche Operationen
    r'\bdd\b.*\bof=/dev/',              # dd to device
    r'\bdd\b.*\bif=/dev/(zero|random|urandom).*\bof=',  # dd wipe
    
    # Direkte Löschung kritischer Pfade
    r'\brm\s+(-[rfRF]+\s+)?/',          # rm starting with /
    r'\brm\s+(-[rfRF]+\s+)?~',          # rm in home
    r'\brm\s+(-[rfRF]+\s+)?\.',         # rm dotfiles
    
    # System-Konfiguration überschreiben
    r'>\s*/etc/',                       # Overwrite /etc
    r'>>\s*/etc/',                      # Append to /etc
    r'>\s*~/\.',                        # Overwrite dotfiles
    
    # History-Manipulation (Spurenverwischung)
    r'\bhistory\s+-c',                  # Clear history
    r'>\s*~/\.bash_history',            # Overwrite bash history
    r'>\s*~/\.zsh_history',             # Overwrite zsh history
    
    # Crontab-Manipulation
    r'\bcrontab\s+-r',                  # Remove crontab
    
    # Netzwerk-Backdoors
    r'\bnc\b.*-[elp]',                  # netcat listener
    r'\bncat\b.*-[elp]',                # ncat listener
    
    # Remote Code Execution
    r'(curl|wget)\s+.*\|\s*(bash|sh|zsh|python|perl|ruby)',
    r'(curl|wget)\s+-[^\s]*o[^\s]*\s+.*&&\s*(bash|sh|chmod)',
]

# Gefährliche Zielverzeichnisse/-dateien
DANGEROUS_TARGETS = [
    # System-kritische Verzeichnisse
    '/', '/etc', '/usr', '/var', '/boot', '/root', '/home',
    '/bin', '/sbin', '/lib', '/lib64', '/opt',
    '/dev', '/proc', '/sys', '/run',
    
    # Home-Verzeichnis Varianten
    '~', '$HOME',
    
    # Sensitive Dateien
    '.ssh', '.gnupg', '.gpg',
    '.bashrc', '.zshrc', '.profile', '.bash_profile', '.bash_logout',
    '.env', '.git', '.gitconfig',
    '.config', '.local',
    '.aws', '.azure', '.kube',
    
    # Credentials
    'id_rsa', 'id_ed25519', 'id_ecdsa',
    '.netrc', '.npmrc', '.pypirc',
]

# Befehle die als Interpreter fungieren können
INTERPRETER_COMMANDS = {
    'python', 'python3', 'python2',
    'perl', 'ruby', 'node', 'nodejs',
    'php', 'lua', 'tclsh', 'wish',
    'awk', 'gawk', 'nawk',
}

# Shell-Befehle
SHELL_COMMANDS = {
    'bash', 'sh', 'zsh', 'fish', 'csh', 'tcsh', 'dash', 'ksh',
}

# Erlaubte Hosts für URL-Abrufe (Whitelist)
ALLOWED_URL_SCHEMES = ["http", "https", "ftp"]

# Private/Lokale IP-Bereiche die blockiert werden sollten
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
# Logging-Konfiguration
# ============================================================================

def setup_logging(
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = False
) -> logging.Logger:
    """
    Konfiguriert und gibt einen Logger für die Mistral CLI zurück.
    
    Args:
        level: Log-Level (default: INFO)
        log_to_file: Ob in Datei geloggt werden soll (default: True)
        log_to_console: Ob auf Konsole geloggt werden soll (default: False)
    
    Returns:
        Konfigurierter Logger
    """
    logger = logging.getLogger("mistral-cli")
    
    # Verhindere doppelte Handler
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Format für Log-Einträge
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File Handler
    if log_to_file:
        try:
            file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warnung: Konnte Log-Datei nicht erstellen: {e}", file=sys.stderr)
    
    # Console Handler (optional)
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


# Globaler Logger
logger = setup_logging()


# ============================================================================
# Umgebungsvariablen & Konfiguration
# ============================================================================

def load_environment() -> None:
    """
    Lädt Umgebungsvariablen aus .env-Datei (falls vorhanden).
    Sucht in folgender Reihenfolge:
    1. Aktuelles Verzeichnis (.env)
    2. Home-Verzeichnis (~/.mistral-cli.env)
    """
    if not DOTENV_AVAILABLE:
        logger.debug("python-dotenv nicht installiert, überspringe .env-Laden")
        return
    
    # Mögliche .env Pfade
    env_paths = [
        Path.cwd() / ".env",
        Path.home() / ".mistral-cli.env",
        Path.home() / ".env"
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Umgebungsvariablen geladen aus: {env_path}")
            return
    
    logger.debug("Keine .env-Datei gefunden")


# Lade Umgebungsvariablen beim Import
load_environment()


# ============================================================================
# Sichere API-Key-Verwaltung (v1.3.0)
# ============================================================================

def _derive_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Leitet einen AES-Schlüssel aus einem Passwort ab (PBKDF2).
    
    Args:
        password: Das Master-Passwort
        salt: Salt für die Ableitung
    
    Returns:
        32-Byte-Schlüssel für Fernet
    """
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("cryptography nicht installiert")
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # OWASP-Empfehlung für 2023+
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def _get_or_create_salt() -> bytes:
    """
    Liest oder erstellt einen Salt für die Schlüsselableitung.
    
    Returns:
        16-Byte-Salt
    """
    if SALT_FILE.exists():
        with open(SALT_FILE, 'rb') as f:
            return f.read()
    else:
        salt = secrets.token_bytes(16)
        with open(SALT_FILE, 'wb') as f:
            f.write(salt)
        # Dateirechte einschränken (nur Besitzer)
        os.chmod(SALT_FILE, 0o600)
        return salt


def store_api_key(api_key: str, master_password: Optional[str] = None) -> Tuple[bool, str]:
    """
    Speichert den API-Key sicher.
    
    Methode 1 (Keyring): Nutzt OS-nativen Credential Manager
    Methode 2 (AES): Verschlüsselt mit Master-Passwort
    
    Args:
        api_key: Der zu speichernde API-Key
        master_password: Optionales Master-Passwort für AES-Fallback
    
    Returns:
        Tuple aus (Erfolg, Methode/Fehlermeldung)
    """
    if not api_key or not api_key.strip():
        return (False, "API-Key darf nicht leer sein")
    
    api_key = api_key.strip()
    
    # Methode 1: Keyring (bevorzugt)
    if KEYRING_AVAILABLE:
        try:
            keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, api_key)
            logger.info("API-Key sicher im System-Keyring gespeichert")
            return (True, "keyring")
        except Exception as e:
            logger.warning(f"Keyring-Speicherung fehlgeschlagen: {e}")
            # Fallback zu AES
    
    # Methode 2: AES-Verschlüsselung mit Master-Passwort
    if CRYPTO_AVAILABLE:
        if not master_password:
            try:
                master_password = getpass.getpass("🔐 Master-Passwort für API-Key-Verschlüsselung: ")
                if not master_password:
                    return (False, "Master-Passwort erforderlich")
            except (EOFError, KeyboardInterrupt):
                return (False, "Abgebrochen")
        
        try:
            salt = _get_or_create_salt()
            key = _derive_key_from_password(master_password, salt)
            fernet = Fernet(key)
            encrypted = fernet.encrypt(api_key.encode())
            
            with open(ENCRYPTED_KEY_FILE, 'wb') as f:
                f.write(encrypted)
            
            # Dateirechte einschränken
            os.chmod(ENCRYPTED_KEY_FILE, 0o600)
            
            logger.info("API-Key mit AES-256 verschlüsselt gespeichert")
            return (True, "aes")
        except Exception as e:
            logger.error(f"AES-Verschlüsselung fehlgeschlagen: {e}")
            return (False, f"Verschlüsselung fehlgeschlagen: {e}")
    
    return (False, "Weder keyring noch cryptography verfügbar. Installiere: pip install keyring")


def get_stored_api_key(master_password: Optional[str] = None) -> Optional[str]:
    """
    Ruft den sicher gespeicherten API-Key ab.
    
    Args:
        master_password: Master-Passwort für AES-Entschlüsselung (falls verwendet)
    
    Returns:
        API-Key oder None wenn nicht gefunden/entschlüsselbar
    """
    # Methode 1: Keyring
    if KEYRING_AVAILABLE:
        try:
            api_key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
            if api_key:
                logger.debug("API-Key aus System-Keyring geladen")
                return api_key
        except Exception as e:
            logger.debug(f"Keyring-Abruf fehlgeschlagen: {e}")
    
    # Methode 2: AES-verschlüsselte Datei
    if CRYPTO_AVAILABLE and ENCRYPTED_KEY_FILE.exists():
        if not master_password:
            try:
                master_password = getpass.getpass("🔐 Master-Passwort: ")
            except (EOFError, KeyboardInterrupt):
                return None
        
        try:
            salt = _get_or_create_salt()
            key = _derive_key_from_password(master_password, salt)
            fernet = Fernet(key)
            
            with open(ENCRYPTED_KEY_FILE, 'rb') as f:
                encrypted = f.read()
            
            api_key = fernet.decrypt(encrypted).decode()
            logger.debug("API-Key aus verschlüsselter Datei geladen")
            return api_key
        except Exception as e:
            logger.warning(f"API-Key-Entschlüsselung fehlgeschlagen: {e}")
            return None
    
    return None


def delete_stored_api_key() -> Tuple[bool, str]:
    """
    Löscht den gespeicherten API-Key.
    
    Returns:
        Tuple aus (Erfolg, Meldung)
    """
    deleted = []
    
    # Keyring löschen
    if KEYRING_AVAILABLE:
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
            deleted.append("keyring")
        except Exception:
            pass  # Nicht vorhanden oder Fehler
    
    # Verschlüsselte Datei löschen
    if ENCRYPTED_KEY_FILE.exists():
        try:
            ENCRYPTED_KEY_FILE.unlink()
            deleted.append("encrypted file")
        except Exception as e:
            logger.error(f"Konnte verschlüsselte Datei nicht löschen: {e}")
    
    # Salt auch löschen
    if SALT_FILE.exists():
        try:
            SALT_FILE.unlink()
            deleted.append("salt")
        except Exception:
            pass
    
    if deleted:
        logger.info(f"API-Key gelöscht aus: {', '.join(deleted)}")
        return (True, f"Gelöscht aus: {', '.join(deleted)}")
    
    return (False, "Kein gespeicherter API-Key gefunden")


def setup_api_key_interactive() -> bool:
    """
    Interaktive Einrichtung des API-Keys.
    
    Returns:
        True wenn erfolgreich, False sonst
    """
    print()
    print("╔" + "═" * 62 + "╗")
    print("║  🔐 Mistral CLI - API-Key Einrichtung                          ║")
    print("╠" + "═" * 62 + "╣")
    
    # Zeige verfügbare Speichermethoden
    if KEYRING_AVAILABLE:
        print("║  ✅ System-Keyring verfügbar (empfohlen)                      ║")
    else:
        print("║  ❌ System-Keyring nicht verfügbar                           ║")
        print("║     → pip install keyring                                   ║")
    
    if CRYPTO_AVAILABLE:
        print("║  ✅ AES-Verschlüsselung verfügbar (Fallback)                  ║")
    else:
        print("║  ❌ AES-Verschlüsselung nicht verfügbar                      ║")
        print("║     → pip install cryptography                              ║")
    
    print("╠" + "═" * 62 + "╣")
    print("║  API-Key erhalten: https://console.mistral.ai/               ║")
    print("╚" + "═" * 62 + "╝")
    print()
    
    if not KEYRING_AVAILABLE and not CRYPTO_AVAILABLE:
        print("❌ Keine sichere Speichermethode verfügbar.")
        print("   Installiere: pip install keyring")
        return False
    
    try:
        api_key = getpass.getpass("🔑 Mistral API-Key eingeben: ")
        
        if not api_key or not api_key.strip():
            print("❌ API-Key darf nicht leer sein.")
            return False
        
        # Einfache Validierung
        if len(api_key) < 10:
            print("⚠️  Warnung: API-Key scheint zu kurz zu sein.")
        
        success, method = store_api_key(api_key)
        
        if success:
            print(f"\n✅ API-Key erfolgreich gespeichert! (Methode: {method})")
            return True
        else:
            print(f"\n❌ Speichern fehlgeschlagen: {method}")
            return False
            
    except (EOFError, KeyboardInterrupt):
        print("\nAbgebrochen.")
        return False


def get_api_key_status() -> Dict[str, Any]:
    """
    Gibt den Status der API-Key-Speicherung zurück.
    
    Returns:
        Dictionary mit Status-Informationen
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


# ============================================================================
# Client-Initialisierung
# ============================================================================

_client_instance: Optional[Mistral] = None


def get_client(api_key: Optional[str] = None) -> Mistral:
    """
    Initialisiert und gibt einen Mistral Client zurück.
    Verwendet Singleton-Pattern für Wiederverwendung.
    
    Sucht den API-Key in folgender Reihenfolge:
    1. Expliziter Parameter
    2. Umgebungsvariable MISTRAL_API_KEY
    3. Sicher gespeicherter Key (Keyring/AES)
    4. Interaktive Einrichtung (falls nicht gefunden)
    
    Args:
        api_key: Optionaler API-Key (überschreibt alles andere)
    
    Returns:
        Mistral Client Instanz
    
    Raises:
        SystemExit: Wenn kein API-Key verfügbar ist
    """
    global _client_instance
    
    # Wenn bereits initialisiert und kein neuer Key, verwende bestehende Instanz
    if _client_instance is not None and api_key is None:
        return _client_instance
    
    # API-Key ermitteln (Priorität: Parameter > Env > Gespeichert)
    key = api_key or os.environ.get("MISTRAL_API_KEY")
    
    # Fallback: Sicher gespeicherter Key
    if not key:
        key = get_stored_api_key()
    
    # Immer noch kein Key? Interaktive Einrichtung anbieten
    if not key:
        print()
        print("🔑 Kein API-Key gefunden.")
        print()
        
        try:
            response = input("Möchtest du jetzt einen API-Key einrichten? [J/n]: ").strip().lower()
            if response in ['', 'j', 'ja', 'y', 'yes']:
                if setup_api_key_interactive():
                    key = get_stored_api_key()
        except (EOFError, KeyboardInterrupt):
            print("\nAbgebrochen.")
    
    if not key:
        error_msg = """
╔══════════════════════════════════════════════════════════════════╗
║  FEHLER: MISTRAL_API_KEY nicht gefunden                          ║
╠══════════════════════════════════════════════════════════════════╣
║  Bitte richte den API-Key auf eine der folgenden Weisen ein:      ║
║                                                                  ║
║  Option 1: Interaktive Einrichtung (empfohlen, sicher)           ║
║    ./mistral auth setup                                          ║
║                                                                  ║
║  Option 2: Umgebungsvariable (temporär)                          ║
║    export MISTRAL_API_KEY='ihr-api-key'                          ║
║                                                                  ║
║  API-Key erhalten: https://console.mistral.ai/                   ║
╚══════════════════════════════════════════════════════════════════╝
"""
        print(error_msg, file=sys.stderr)
        logger.error("MISTRAL_API_KEY nicht gefunden")
        sys.exit(1)
    
    try:
        client = Mistral(api_key=key)
        logger.info("Mistral Client erfolgreich initialisiert")
        
        # Speichere Instanz nur wenn kein expliziter Key übergeben wurde
        if api_key is None:
            _client_instance = client
        
        return client
    
    except Exception as e:
        logger.error(f"Fehler bei Client-Initialisierung: {e}")
        print(f"Fehler bei der Initialisierung des Mistral Clients: {e}", file=sys.stderr)
        sys.exit(1)


def reset_client() -> None:
    """Setzt den Client zurück (für Tests oder Neukonfiguration)."""
    global _client_instance
    _client_instance = None
    logger.debug("Client-Instanz zurückgesetzt")


# ============================================================================
# Sicherheitsfunktionen - Bash Command Validation (v1.2.0 ERWEITERT)
# ============================================================================

def is_dangerous_command(command: str) -> Tuple[bool, str]:
    """
    Prüft ob ein Befehl potentiell gefährlich ist.
    
    Diese Funktion analysiert Shell-Befehle auf verschiedene Angriffsvektoren:
    - Direkt destruktive Befehle (rm, mkfs, dd, etc.)
    - Command Chaining (;, &&, ||, |)
    - Subshell-Ausführung ($(), ``)
    - Encoded Execution (base64, xxd)
    - Interpreter-Ausführung (python -c, bash -c, etc.)
    - Gefährliche Zielverzeichnisse
    
    Args:
        command: Der zu prüfende Shell-Befehl
        
    Returns:
        Tuple[bool, str]: (ist_gefährlich, Begründung)
        
    Examples:
        >>> is_dangerous_command("ls -la")
        (False, "")
        >>> is_dangerous_command("rm -rf /")
        (True, "Gefährliches Pattern erkannt: rm mit kritischem Pfad")
        >>> is_dangerous_command("echo hi && rm -rf ~")
        (True, "Gefährlicher Befehl in Kette: rm mit gefährlichen Argumenten")
    """
    if not command or not command.strip():
        return False, ""
    
    command = command.strip()
    
    # 1. Pattern-basierte Erkennung (schnellste Prüfung zuerst)
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, f"Gefährliches Pattern erkannt: {pattern[:30]}..."
    
    # 2. Command Chaining erkennen und jeden Teil prüfen
    chain_separators = [';', '&&', '||', '\n']
    has_chaining = any(sep in command for sep in chain_separators)
    
    # Pipe separat behandeln (nicht immer gefährlich)
    has_pipe = '|' in command and 'base64' not in command.lower()
    
    if has_chaining:
        # Aufteilen nach Trennzeichen
        parts = re.split(r'[;&\n]+|&&|\|\|', command)
        for part in parts:
            part = part.strip()
            if part:
                is_dangerous, reason = _check_single_command(part)
                if is_dangerous:
                    return True, f"Gefährlicher Befehl in Kette: {reason}"
    
    # 3. Subshell-Erkennung (rekursiv)
    subshell_patterns = [
        (r'\$\(([^)]+)\)', 'Command Substitution $()'),
        (r'`([^`]+)`', 'Backtick Substitution'),
    ]
    for pattern, subshell_type in subshell_patterns:
        matches = re.findall(pattern, command)
        for match in matches:
            is_dangerous, reason = is_dangerous_command(match)
            if is_dangerous:
                return True, f"Gefährlicher Befehl in {subshell_type}: {reason}"
    
    # 4. Pipe-Ketten analysieren
    if has_pipe:
        pipe_parts = command.split('|')
        for part in pipe_parts:
            part = part.strip()
            if part:
                is_dangerous, reason = _check_single_command(part)
                if is_dangerous:
                    return True, f"Gefährlicher Befehl in Pipe: {reason}"
    
    # 5. Einzelbefehl prüfen (wenn kein Chaining)
    if not has_chaining and not has_pipe:
        return _check_single_command(command)
    
    return False, ""


def _check_single_command(command: str) -> Tuple[bool, str]:
    """
    Prüft einen einzelnen Befehl (ohne Chaining).
    
    Args:
        command: Einzelner Shell-Befehl
        
    Returns:
        Tuple[bool, str]: (ist_gefährlich, Begründung)
    """
    command = command.strip()
    
    if not command:
        return False, ""
    
    try:
        # Sicheres Parsen mit shlex
        tokens = shlex.split(command)
    except ValueError as e:
        # Ungültiges Quoting könnte auf Manipulation hindeuten
        logger.warning(f"Ungültiges Shell-Quoting in Befehl: {command} ({e})")
        return True, f"Ungültiges Shell-Quoting: {e}"
    
    if not tokens:
        return False, ""
    
    # Basis-Befehl extrahieren (ohne Pfad wie /usr/bin/)
    base_cmd = tokens[0].split('/')[-1].lower()
    args = tokens[1:] if len(tokens) > 1 else []
    
    # Spezialfall: mkfs.* Varianten (mkfs.ext4, mkfs.xfs, etc.)
    if base_cmd.startswith('mkfs'):
        return True, f"Dateisystem-Formatierung: {base_cmd}"
    
    # 1. Interpreter mit Code-Ausführung
    if base_cmd in INTERPRETER_COMMANDS:
        code_exec_flags = ['-c', '-e', '--eval', '-exec']
        if any(flag in args for flag in code_exec_flags):
            return True, f"Code-Ausführung via {base_cmd}"
    
    # 2. Shell mit -c Flag
    if base_cmd in SHELL_COMMANDS:
        if '-c' in args:
            return True, f"Shell-Ausführung via {base_cmd} -c"
    
    # 3. Direkt gefährliche Befehle
    if base_cmd in DANGEROUS_COMMANDS:
        # Einige Befehle sind nur mit bestimmten Args gefährlich
        if base_cmd in CONDITIONAL_DANGEROUS:
            dangerous_args = CONDITIONAL_DANGEROUS[base_cmd]
            args_str = ' '.join(args).lower()
            
            for dangerous_arg in dangerous_args:
                if dangerous_arg in args or dangerous_arg in args_str:
                    return True, f"{base_cmd} mit gefährlichen Argumenten: {dangerous_arg}"
            
            # Ohne gefährliche Args ist der Befehl erlaubt
            # (z.B. "rm file.txt" ohne -rf)
            
            # Aber trotzdem auf gefährliche Ziele prüfen
            for arg in args:
                for target in DANGEROUS_TARGETS:
                    if arg == target or arg.startswith(target + '/') or arg.startswith(target):
                        return True, f"{base_cmd} auf gefährliches Ziel: {arg}"
            
            return False, ""
        else:
            # Immer gefährlich (z.B. mkfs, shutdown)
            return True, f"Gefährlicher Befehl: {base_cmd}"
    
    # 4. Bedingt gefährliche Befehle
    if base_cmd in CONDITIONAL_DANGEROUS:
        dangerous_args = CONDITIONAL_DANGEROUS[base_cmd]
        for arg in args:
            if arg in dangerous_args:
                return True, f"{base_cmd} mit gefährlichen Argumenten: {arg}"
            # Auch Kombinationen wie -rf prüfen
            if arg.startswith('-') and any(da.lstrip('-') in arg for da in dangerous_args if da.startswith('-')):
                return True, f"{base_cmd} mit gefährlichen Argumenten: {arg}"
    
    # 5. Gefährliche Ziele prüfen (für modifizierende Befehle)
    modifying_commands = {'mv', 'cp', 'ln', 'touch', 'mkdir', 'tee'}
    if base_cmd in modifying_commands:
        for arg in args:
            if arg.startswith('-'):
                continue  # Flags überspringen
            for target in DANGEROUS_TARGETS:
                if arg == target or arg.startswith(target + '/'):
                    return True, f"{base_cmd} auf gefährliches Ziel: {arg}"
    
    # 6. Redirect zu gefährlichen Zielen (bereits in Patterns, aber sicherheitshalber)
    if '>' in command:
        redirect_match = re.search(r'>+\s*(\S+)', command)
        if redirect_match:
            redirect_target = redirect_match.group(1)
            for target in DANGEROUS_TARGETS:
                if redirect_target.startswith(target):
                    return True, f"Redirect zu gefährlichem Ziel: {redirect_target}"
    
    return False, ""


def request_confirmation(command: str, reason: str) -> bool:
    """
    Fragt den Benutzer um Bestätigung für einen als gefährlich erkannten Befehl.
    
    Args:
        command: Der gefährliche Befehl
        reason: Begründung warum der Befehl als gefährlich erkannt wurde
        
    Returns:
        bool: True wenn der Benutzer bestätigt, False sonst
    """
    print()
    print("=" * 60)
    print("⚠️  WARNUNG: Potentiell gefährlicher Befehl erkannt!")
    print("=" * 60)
    print(f"  Befehl: {command}")
    print(f"  Grund:  {reason}")
    print("=" * 60)
    print()
    
    logger.warning(f"Gefährlicher Befehl erkannt: {command} - Grund: {reason}")
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = input("Möchtest du diesen Befehl trotzdem ausführen? [j/N]: ").strip().lower()
            
            if response in ['j', 'ja', 'y', 'yes']:
                logger.info(f"Benutzer hat gefährlichen Befehl bestätigt: {command}")
                return True
            
            if response in ['n', 'nein', 'no', '']:
                logger.info(f"Benutzer hat gefährlichen Befehl abgelehnt: {command}")
                return False
            
            print("Bitte antworte mit 'j' (ja) oder 'n' (nein)")
            
        except (EOFError, KeyboardInterrupt):
            print("\nAbgebrochen.")
            return False
    
    print("Zu viele ungültige Eingaben. Befehl wird nicht ausgeführt.")
    return False


# ============================================================================
# Legacy-Funktionen (Kompatibilität mit bestehenden Code)
# ============================================================================

def analyze_command_risk(command: str) -> Tuple[RiskLevel, str, str]:
    """
    Analysiert einen Befehl und gibt Risikostufe, Kategorie und Beschreibung zurück.
    (Legacy-Funktion für Kompatibilität)
    
    Args:
        command: Der zu analysierende Befehl
    
    Returns:
        Tuple aus (RiskLevel, Kategorie, Beschreibung)
    """
    is_dangerous, reason = is_dangerous_command(command)
    
    if is_dangerous:
        if any(keyword in reason.lower() for keyword in ['critical', 'fork', 'dd', 'mkfs']):
            return (RiskLevel.CRITICAL, "security", reason)
        elif any(keyword in reason.lower() for keyword in ['rm', 'chmod', 'chown']):
            return (RiskLevel.HIGH, "filesystem", reason)
        else:
            return (RiskLevel.MEDIUM, "general", reason)
    
    return (RiskLevel.SAFE, "none", "Keine Gefahr erkannt")


def get_command_risk_info(command: str) -> Dict[str, Any]:
    """
    Gibt detaillierte Risiko-Informationen für einen Befehl zurück.
    
    Args:
        command: Der zu prüfende Befehl
    
    Returns:
        Dictionary mit Risiko-Details
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
    """Gibt eine Empfehlung basierend auf der Risikostufe zurück."""
    recommendations = {
        RiskLevel.CRITICAL: "Dieser Befehl ist extrem gefährlich und wird blockiert.",
        RiskLevel.HIGH: "Dieser Befehl ist gefährlich und wird blockiert. Verwende sicherere Alternativen.",
        RiskLevel.MEDIUM: "Dieser Befehl erfordert besondere Vorsicht. Bitte bestätige die Ausführung.",
        RiskLevel.LOW: "Dieser Befehl ist potenziell sensibel. Prüfe das Ergebnis.",
        RiskLevel.SAFE: "Keine besonderen Sicherheitsbedenken."
    }
    return recommendations.get(risk_level, "Unbekannte Risikostufe.")


# ============================================================================
# Path Validation (v1.2.0)
# ============================================================================

def is_safe_path(path: str, base_dir: Optional[str] = None) -> Tuple[bool, str]:
    """
    Prüft ob ein Pfad sicher ist (keine Path Traversal Attacke).
    
    Args:
        path: Der zu prüfende Pfad
        base_dir: Optionales Basis-Verzeichnis für relative Pfade
        
    Returns:
        Tuple[bool, str]: (ist_sicher, Begründung oder normalisierter Pfad)
    """
    if not path:
        return False, "Leerer Pfad"
    
    # Path Traversal Patterns
    if '..' in path:
        return False, "Path Traversal erkannt (..)"
    
    # Absolute Pfade zu sensitiven Bereichen
    sensitive_prefixes = ['/etc', '/usr', '/var', '/boot', '/root', '/dev', '/proc', '/sys']
    
    try:
        # Pfad normalisieren
        normalized = os.path.normpath(path)
        
        if base_dir:
            base_normalized = os.path.normpath(base_dir)
            full_path = os.path.normpath(os.path.join(base_normalized, normalized))
            
            # Prüfen ob der Pfad innerhalb des Base-Verzeichnisses bleibt
            if not full_path.startswith(base_normalized):
                return False, "Pfad verlässt das erlaubte Verzeichnis"
            
            return True, full_path
        
        # Ohne Base-Dir: Sensitive Bereiche prüfen
        abs_path = os.path.abspath(os.path.expanduser(normalized))
        
        for prefix in sensitive_prefixes:
            if abs_path.startswith(prefix):
                return False, f"Zugriff auf sensitiven Bereich: {prefix}"
        
        return True, abs_path
        
    except Exception as e:
        return False, f"Pfad-Validierung fehlgeschlagen: {e}"


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validiert eine URL auf Sicherheit.
    
    Args:
        url: Die zu validierende URL
    
    Returns:
        Tuple aus (ist_sicher, Fehlermeldung)
    """
    try:
        parsed = urlparse(url)
        
        # Prüfe Schema
        if parsed.scheme.lower() not in ALLOWED_URL_SCHEMES:
            return (False, f"URL-Schema '{parsed.scheme}' nicht erlaubt. Erlaubt: {ALLOWED_URL_SCHEMES}")
        
        # Prüfe auf leeren Host
        if not parsed.netloc:
            return (False, "URL hat keinen gültigen Host")
        
        # Prüfe auf lokale/private IPs
        hostname = parsed.hostname
        if hostname:
            # Versuche als IP zu parsen
            try:
                ip = ipaddress.ip_address(hostname)
                for private_range in PRIVATE_IP_RANGES:
                    if ip in ipaddress.ip_network(private_range, strict=False):
                        logger.warning(f"URL zu privater/lokaler IP blockiert: {url}")
                        return (False, f"Zugriff auf private/lokale IP-Adresse nicht erlaubt: {hostname}")
            except ValueError:
                # Kein IP, sondern Hostname - das ist okay
                pass
            
            # Blockiere localhost-Varianten
            localhost_patterns = ["localhost", "127.0.0.1", "::1", "0.0.0.0"]
            if any(lh in hostname.lower() for lh in localhost_patterns):
                return (False, "Zugriff auf localhost nicht erlaubt")
        
        logger.debug(f"URL validiert: {url}")
        return (True, "URL ist sicher")
    
    except Exception as e:
        logger.error(f"URL-Validierung fehlgeschlagen: {e}")
        return (False, f"URL-Validierung fehlgeschlagen: {str(e)}")


def validate_path(path: str, allow_system_paths: bool = False) -> Tuple[bool, str]:
    """
    Validiert einen Dateipfad auf Sicherheit.
    (Alias für is_safe_path für Kompatibilität)
    
    Args:
        path: Der zu validierende Pfad
        allow_system_paths: Ob Systempfade erlaubt sind (default: False)
    
    Returns:
        Tuple aus (ist_sicher, Fehlermeldung)
    """
    return is_safe_path(path)


def sanitize_path(path: str) -> str:
    """
    Bereinigt einen Dateipfad und expandiert ~ zu Home-Verzeichnis.
    
    Args:
        path: Der zu bereinigende Pfad
    
    Returns:
        Bereinigter, absoluter Pfad
    """
    return os.path.abspath(os.path.expanduser(path))


# ============================================================================
# Log Sanitization (v1.2.0)
# ============================================================================

def sanitize_for_log(text: str, max_length: int = 500) -> str:
    """
    Bereinigt Text für sicheres Logging (entfernt sensitive Daten).
    
    Args:
        text: Der zu bereinigende Text
        max_length: Maximale Länge des Outputs
        
    Returns:
        Bereinigter Text
    """
    if not text:
        return ""
    
    # API-Keys und Tokens maskieren
    patterns = [
        (r'(MISTRAL_API_KEY[=:\s]+)[^\s]+', r'\1[REDACTED]'),
        (r'(api[_-]?key[=:\s]+)[^\s]+', r'\1[REDACTED]'),
        (r'(token[=:\s]+)[^\s]+', r'\1[REDACTED]'),
        (r'(password[=:\s]+)[^\s]+', r'\1[REDACTED]'),
        (r'(secret[=:\s]+)[^\s]+', r'\1[REDACTED]'),
        (r'(Bearer\s+)[^\s]+', r'\1[REDACTED]'),
        (r'(ftp://[^:]+:)[^@]+(@)', r'\1[REDACTED]\2'),
    ]
    
    sanitized = text
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    
    # Länge begrenzen
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "... [truncated]"
    
    return sanitized


# ============================================================================
# Token-Management
# ============================================================================

def estimate_tokens(text: str) -> int:
    """
    Schätzt die Anzahl der Tokens in einem Text.
    Grobe Schätzung: ~4 Zeichen pro Token für Deutsch/Englisch.
    
    Args:
        text: Der Text
    
    Returns:
        Geschätzte Token-Anzahl
    """
    return len(text) // 4


def trim_messages(
    messages: list,
    max_tokens: int = 8000,
    keep_system: bool = True
) -> list:
    """
    Kürzt die Nachrichtenliste, um das Token-Limit nicht zu überschreiten.
    Behält die neuesten Nachrichten und optional die System-Nachricht.
    
    Args:
        messages: Liste der Nachrichten
        max_tokens: Maximale Token-Anzahl
        keep_system: Ob System-Nachrichten behalten werden sollen
    
    Returns:
        Gekürzte Nachrichtenliste
    """
    if not messages:
        return messages
    
    # Separiere System-Nachrichten
    system_messages = []
    other_messages = []
    
    for msg in messages:
        if msg.get("role") == "system" and keep_system:
            system_messages.append(msg)
        else:
            other_messages.append(msg)
    
    # Schätze Tokens für System-Nachrichten
    system_tokens = sum(
        estimate_tokens(msg.get("content", "")) 
        for msg in system_messages
    )
    
    remaining_tokens = max_tokens - system_tokens
    
    # Füge Nachrichten von hinten hinzu (neueste zuerst)
    trimmed = []
    current_tokens = 0
    
    for msg in reversed(other_messages):
        msg_tokens = estimate_tokens(str(msg.get("content", "")))
        if current_tokens + msg_tokens <= remaining_tokens:
            trimmed.insert(0, msg)
            current_tokens += msg_tokens
        else:
            break
    
    # Kombiniere System-Nachrichten mit gekürzten Nachrichten
    result = system_messages + trimmed
    
    if len(result) < len(messages):
        logger.info(f"Nachrichten gekürzt: {len(messages)} -> {len(result)}")
    
    return result


# ============================================================================
# Hilfsfunktionen
# ============================================================================

def print_error(message: str) -> None:
    """Gibt eine formatierte Fehlermeldung aus."""
    print(f"❌ Fehler: {message}", file=sys.stderr)
    logger.error(message)


def print_warning(message: str) -> None:
    """Gibt eine formatierte Warnung aus."""
    print(f"⚠️  Warnung: {message}", file=sys.stderr)
    logger.warning(message)


def print_success(message: str) -> None:
    """Gibt eine formatierte Erfolgsmeldung aus."""
    print(f"✅ {message}")
    logger.info(message)


def print_info(message: str) -> None:
    """Gibt eine formatierte Info-Meldung aus."""
    print(f"ℹ️  {message}")
    logger.info(message)


def format_risk_warning(risk_info: Dict[str, Any]) -> str:
    """
    Formatiert eine Risiko-Warnung für die Konsolenausgabe.
    
    Args:
        risk_info: Dictionary mit Risiko-Details
    
    Returns:
        Formatierte Warnung
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
{icon} Sicherheitswarnung: {risk_level}
   Kategorie: {risk_info['category']}
   Beschreibung: {risk_info['description']}
   Empfehlung: {risk_info['recommendation']}
"""


def check_file_operation_safety(
    operation: str,
    source: str,
    destination: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Prüft, ob eine Dateioperationen sicher ist.
    
    Args:
        operation: Die Operation (read, write, copy, move, delete)
        source: Quellpfad
        destination: Zielpfad (optional)
    
    Returns:
        Tuple aus (ist_sicher, Fehlermeldung)
    """
    # Validiere Quellpfad
    is_safe, message = is_safe_path(source)
    if not is_safe:
        return (False, f"Quellpfad unsicher: {message}")
    
    # Validiere Zielpfad wenn vorhanden
    if destination:
        is_safe, message = is_safe_path(destination)
        if not is_safe:
            return (False, f"Zielpfad unsicher: {message}")
    
    # Spezielle Prüfungen je nach Operation
    if operation == "delete":
        source_path = sanitize_path(source)
        home = str(Path.home())
        
        # Verhindere Löschen wichtiger Verzeichnisse
        protected_dirs = [home, "/", "/home", "/etc", "/var", "/usr"]
        if source_path in protected_dirs:
            return (False, f"Löschen von {source_path} nicht erlaubt")
    
    return (True, "Operation ist sicher")


def get_version() -> str:
    """Returns the current version of mistral-cli."""
    return "1.3.0"
