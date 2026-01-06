#!/usr/bin/env python3
"""
Mistral CLI - Utilities Module
Zentrale Funktionen für Client-Initialisierung, Logging und Konfiguration
"""

import os
import sys
import logging
from typing import Optional
from pathlib import Path

# Versuche python-dotenv zu laden (optional)
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

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

# Gefährliche Bash-Befehle (für spätere Sicherheits-Implementierung)
DANGEROUS_COMMANDS = [
    "rm -rf /",
    "rm -rf /*",
    "dd if=/dev/zero",
    "mkfs.",
    ":(){:|:&};:",  # Fork bomb
    "chmod -R 777 /",
    "chown -R",
    "> /dev/sda",
    "mv /* /dev/null",
    "wget | sh",
    "curl | sh",
    "wget | bash",
    "curl | bash",
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
# Client-Initialisierung
# ============================================================================

_client_instance: Optional[Mistral] = None


def get_client(api_key: Optional[str] = None) -> Mistral:
    """
    Initialisiert und gibt einen Mistral Client zurück.
    Verwendet Singleton-Pattern für Wiederverwendung.
    
    Args:
        api_key: Optionaler API-Key (überschreibt Umgebungsvariable)
    
    Returns:
        Mistral Client Instanz
    
    Raises:
        SystemExit: Wenn kein API-Key verfügbar ist
    """
    global _client_instance
    
    # Wenn bereits initialisiert und kein neuer Key, verwende bestehende Instanz
    if _client_instance is not None and api_key is None:
        return _client_instance
    
    # API-Key ermitteln
    key = api_key or os.environ.get("MISTRAL_API_KEY")
    
    if not key:
        error_msg = """
╔══════════════════════════════════════════════════════════════════╗
║  FEHLER: MISTRAL_API_KEY nicht gefunden                          ║
╠══════════════════════════════════════════════════════════════════╣
║  Bitte setzen Sie den API-Key auf eine der folgenden Weisen:     ║
║                                                                  ║
║  Option 1: Umgebungsvariable (temporär)                          ║
║    export MISTRAL_API_KEY='ihr-api-key'                          ║
║                                                                  ║
║  Option 2: Shell-Konfiguration (dauerhaft)                       ║
║    echo "export MISTRAL_API_KEY='ihr-api-key'" >> ~/.bashrc      ║
║    source ~/.bashrc                                              ║
║                                                                  ║
║  Option 3: .env-Datei (empfohlen für Entwicklung)                ║
║    echo "MISTRAL_API_KEY=ihr-api-key" > ~/.mistral-cli.env       ║
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
# Sicherheitsfunktionen
# ============================================================================

def is_dangerous_command(command: str) -> bool:
    """
    Prüft, ob ein Bash-Befehl potenziell gefährlich ist.
    
    Args:
        command: Der zu prüfende Befehl
    
    Returns:
        True wenn gefährlich, False sonst
    """
    command_lower = command.lower().strip()
    
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous.lower() in command_lower:
            logger.warning(f"Gefährlicher Befehl erkannt: {command}")
            return True
    
    # Zusätzliche Prüfungen
    # Prüfe auf Pipes zu Shell
    if "|" in command and any(sh in command for sh in ["sh", "bash", "zsh"]):
        if any(dl in command for dl in ["wget", "curl"]):
            logger.warning(f"Potenziell gefährlicher Download+Execute erkannt: {command}")
            return True
    
    return False


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
# Token-Management (Vorbereitung)
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
