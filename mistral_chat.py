#!/usr/bin/env python3
"""
Mistral CLI - Chat Mode
Interactive chat with tool support and token management
"""

import sys
import json
import argparse
import atexit
from pathlib import Path
from typing import List, Dict, Any, Optional

# ============================================================================
# Readline Setup für Pfeiltasten und History
# ============================================================================

READLINE_AVAILABLE = False
READLINE_TYPE = "none"

# History-Datei für persistente Command-History
HISTORY_FILE = Path.home() / ".mistral-cli_history"
HISTORY_LENGTH = 1000

def _detect_readline_type() -> str:
    """Erkennt welche readline-Bibliothek verwendet wird."""
    try:
        import readline
        doc = getattr(readline, '__doc__', '') or ''
        if 'libedit' in doc.lower():
            return 'libedit'
        elif 'gnu' in doc.lower():
            return 'gnu'
        else:
            # Prüfe auf GNU readline Funktionen
            if hasattr(readline, 'append_history_file'):
                return 'gnu'
            return 'unknown'
    except ImportError:
        return 'none'


def _setup_readline_gnu() -> bool:
    """Konfiguriert GNU readline."""
    try:
        import readline
        
        # History laden
        if HISTORY_FILE.exists():
            try:
                readline.read_history_file(HISTORY_FILE)
            except (IOError, OSError):
                pass
        
        # History-Länge setzen
        readline.set_history_length(HISTORY_LENGTH)
        
        # History beim Beenden speichern
        atexit.register(readline.write_history_file, HISTORY_FILE)
        
        # Standard Emacs-Bindings (funktionieren normalerweise)
        readline.parse_and_bind('tab: self-insert')
        readline.parse_and_bind('"\\e[A": previous-history')  # Up
        readline.parse_and_bind('"\\e[B": next-history')      # Down
        readline.parse_and_bind('"\\e[C": forward-char')      # Right
        readline.parse_and_bind('"\\e[D": backward-char')     # Left
        
        return True
    except Exception:
        return False


def _setup_readline_libedit() -> bool:
    """Konfiguriert libedit (macOS Standard)."""
    try:
        import readline
        
        # History laden
        if HISTORY_FILE.exists():
            try:
                readline.read_history_file(HISTORY_FILE)
            except (IOError, OSError):
                pass
        
        # History-Länge setzen
        readline.set_history_length(HISTORY_LENGTH)
        
        # History beim Beenden speichern
        atexit.register(readline.write_history_file, HISTORY_FILE)
        
        # libedit-spezifische Bindings (unterschiedliche Syntax!)
        readline.parse_and_bind('bind ^I rl_complete')  # Tab
        readline.parse_and_bind('bind -e')  # Emacs-Modus aktivieren
        
        # Pfeiltasten sollten in libedit standardmäßig funktionieren
        # wenn Emacs-Modus aktiv ist
        
        return True
    except Exception:
        return False


def _setup_readline_windows() -> bool:
    """Konfiguriert pyreadline3 für Windows."""
    try:
        import pyreadline3 as readline
        
        # History laden
        if HISTORY_FILE.exists():
            try:
                readline.read_history_file(str(HISTORY_FILE))
            except (IOError, OSError):
                pass
        
        # History-Länge setzen
        readline.set_history_length(HISTORY_LENGTH)
        
        # History beim Beenden speichern
        atexit.register(readline.write_history_file, str(HISTORY_FILE))
        
        return True
    except ImportError:
        return False
    except Exception:
        return False


def setup_readline() -> tuple:
    """
    Konfiguriert readline für Pfeiltasten und History.
    Erkennt automatisch die richtige Bibliothek (GNU, libedit, pyreadline3).
    
    Returns:
        Tuple (erfolg: bool, typ: str)
    """
    global READLINE_AVAILABLE, READLINE_TYPE
    
    # Erst prüfen welcher Typ
    READLINE_TYPE = _detect_readline_type()
    
    if READLINE_TYPE == 'gnu':
        READLINE_AVAILABLE = _setup_readline_gnu()
    elif READLINE_TYPE == 'libedit':
        READLINE_AVAILABLE = _setup_readline_libedit()
    elif READLINE_TYPE == 'none':
        # Versuche Windows-Fallback
        READLINE_AVAILABLE = _setup_readline_windows()
        if READLINE_AVAILABLE:
            READLINE_TYPE = 'pyreadline3'
    else:
        # Unknown - versuche GNU-Setup
        READLINE_AVAILABLE = _setup_readline_gnu()
    
    return (READLINE_AVAILABLE, READLINE_TYPE)


# ============================================================================
# Lokale Imports
# ============================================================================

from mistral_utils import (
    get_client,
    logger,
    trim_messages,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
)
from mistral_tools import TOOLS, execute_tool


# ============================================================================
# ASCII Logo
# ============================================================================

LOGO = r"""
┌─────────────────────────────────────────────────────┐
│ ███╗   ███╗██╗███████╗████████╗██████╗  █████╗ ██╗  │
│ ████╗ ████║██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║  │
│ ██╔████╔██║██║███████╗   ██║   ██████╔╝███████║██║  │
│ ██║╚██╔╝██║██║╚════██║   ██║   ██╔══██╗██╔══██║██║  │
│ ██║ ╚═╝ ██║██║███████║   ██║   ██║  ██║██║  ██║███╗ │
│ ╚═╝     ╚═╝╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══╝ │
│        CLI TOOL - ⚠️ UNOFFICIAL VERSION ⚠️            │
└─────────────────────────────────────────────────────┘
"""


# ============================================================================
# Hilfsfunktionen
# ============================================================================

def print_welcome(model: str, readline_info: tuple) -> None:
    """
    Zeigt die Willkommensnachricht an.
    
    Args:
        model: Das verwendete Modell
        readline_info: Tuple (verfügbar, typ)
    """
    available, rl_type = readline_info
    
    print(LOGO)
    print("Bienvenue! 🇫🇷\n")
    print("Mistral AI Chat with Tool Support")
    print("(Enter 'exit', 'quit' or 'q' to exit)")
    print("(Enter 'clear' to clear conversation history)")
    
    if available:
        print(f"(Use ↑↓ arrow keys for command history) [{rl_type}]")
    else:
        print("(⚠️  Arrow keys not available - install 'gnureadline' for macOS)")
    
    print(f"Model: {model}")
    print("\nAvailable Tools:")
    print("  - Bash commands, Files (read/write/rename/copy/move)")
    print("  - Web (search, URL fetch, downloads, FTP upload)")
    print("  - Data processing (JSON/CSV parsing)")
    print("  - Image analysis (format, size, dimensions)\n")


def process_tool_calls(
    client: Any,
    assistant_message: Any,
    messages: List[Dict[str, Any]],
    auto_confirm: bool,
    model: str,
    temperature: float,
    max_tokens: int
) -> Optional[Any]:
    """
    Verarbeitet Tool-Calls und gibt die finale Antwort zurück.
    
    Args:
        client: Mistral Client
        assistant_message: Die Assistant-Nachricht mit Tool-Calls
        messages: Die Nachrichtenliste (wird modifiziert)
        auto_confirm: Ob Tools automatisch bestätigt werden
        model: Das verwendete Modell
        temperature: Temperatur für die Generierung
        max_tokens: Maximale Token-Anzahl
    
    Returns:
        Die finale Assistant-Nachricht nach Tool-Ausführung
    """
    # Füge Assistant-Nachricht zu Messages hinzu
    messages.append({
        "role": "assistant",
        "content": assistant_message.content or "",
        "tool_calls": assistant_message.tool_calls
    })

    # Führe alle Tool Calls aus
    for tool_call in assistant_message.tool_calls:
        tool_name = tool_call.function.name
        
        try:
            tool_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            logger.error(f"JSON-Parsing-Fehler für Tool {tool_name}: {e}")
            tool_result = {"success": False, "error": f"Ungültige Tool-Argumente: {e}"}
            messages.append({
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(tool_result),
                "tool_call_id": tool_call.id
            })
            continue

        logger.info(f"Tool-Call: {tool_name} mit Args: {tool_args}")

        # Tool ausführen
        tool_result = execute_tool(tool_name, tool_args, auto_confirm=auto_confirm)
        
        logger.debug(f"Tool-Ergebnis: {tool_result}")

        # Tool-Ergebnis zu Messages hinzufügen
        messages.append({
            "role": "tool",
            "name": tool_name,
            "content": json.dumps(tool_result),
            "tool_call_id": tool_call.id
        })

    # Zweite API-Anfrage mit Tool-Ergebnissen
    try:
        response = client.chat.complete(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=TOOLS,
            tool_choice="auto"
        )
        return response.choices[0].message
    except Exception as e:
        logger.error(f"Fehler bei zweiter API-Anfrage: {e}")
        return None


# ============================================================================
# Hauptfunktion
# ============================================================================

def cmd_chat(args: argparse.Namespace) -> None:
    """
    Interaktiver Chat-Modus mit Tool-Unterstützung.
    
    Args:
        args: Kommandozeilen-Argumente mit model, temperature, max_tokens, yes
    """
    # Readline für Pfeiltasten und History aktivieren
    readline_info = setup_readline()
    available, rl_type = readline_info
    
    if available:
        logger.debug(f"Readline aktiviert: {rl_type}")
    else:
        logger.warning("Readline nicht verfügbar - Pfeiltasten deaktiviert")
    
    client = get_client()
    
    # Parameter extrahieren
    model: str = getattr(args, 'model', DEFAULT_MODEL)
    temperature: float = getattr(args, 'temperature', DEFAULT_TEMPERATURE)
    max_tokens: int = getattr(args, 'max_tokens', DEFAULT_MAX_TOKENS)
    auto_confirm: bool = getattr(args, 'yes', False)
    
    logger.info(f"Chat gestartet mit Modell: {model}, Temp: {temperature}, MaxTokens: {max_tokens}")

    print_welcome(model, readline_info)

    messages: List[Dict[str, Any]] = []
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            # Exit-Befehle
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Au revoir! 👋")
                logger.info("Chat beendet durch Benutzer")
                break

            # Clear-Befehl
            if user_input.lower() == 'clear':
                messages = []
                print("🗑️  Konversation gelöscht.\n")
                logger.info("Konversation gelöscht")
                continue

            # History-Befehl (zeigt letzte Eingaben)
            if user_input.lower() == 'history':
                if READLINE_AVAILABLE:
                    import readline
                    history_len = readline.get_current_history_length()
                    print(f"\n📜 Letzte {min(10, history_len)} Eingaben:")
                    for i in range(max(1, history_len - 9), history_len + 1):
                        try:
                            item = readline.get_history_item(i)
                            if item:
                                print(f"  {i}: {item}")
                        except Exception:
                            pass
                    print()
                else:
                    print("⚠️  History nicht verfügbar (readline nicht installiert)\n")
                continue

            # Leere Eingabe ignorieren
            if not user_input:
                continue

            # Nachricht hinzufügen
            messages.append({"role": "user", "content": user_input})
            
            # Token-Management: Kürze Messages wenn nötig
            messages = trim_messages(messages, max_tokens=8000)

            logger.debug(f"Sende {len(messages)} Nachrichten an API")

            # API-Anfrage mit Tools senden
            response = client.chat.complete(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=TOOLS,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message

            # Prüfe ob Tool Calls vorhanden sind
            if assistant_message.tool_calls:
                logger.info(f"{len(assistant_message.tool_calls)} Tool-Calls erkannt")
                
                # Verarbeite Tool-Calls
                final_message = process_tool_calls(
                    client=client,
                    assistant_message=assistant_message,
                    messages=messages,
                    auto_confirm=auto_confirm,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                if final_message:
                    assistant_message = final_message

            # Zeige die finale Antwort
            if assistant_message and assistant_message.content:
                messages.append({"role": "assistant", "content": assistant_message.content})
                print(f"\nMistral: {assistant_message.content}\n")
                logger.debug(f"Antwort: {assistant_message.content[:100]}...")
            else:
                print()

        except KeyboardInterrupt:
            print("\n\nAu revoir! 👋")
            logger.info("Chat beendet durch Keyboard Interrupt")
            break
        except EOFError:
            # Ctrl+D
            print("\nAu revoir! 👋")
            logger.info("Chat beendet durch EOF")
            break
        except Exception as e:
            logger.error(f"Fehler im Chat: {e}")
            print(f"\n❌ Fehler: {str(e)}\n", file=sys.stderr)


# ============================================================================
# Direkter Aufruf
# ============================================================================

if __name__ == '__main__':
    # Einfache Test-Args erstellen
    class TestArgs:
        model = DEFAULT_MODEL
        temperature = DEFAULT_TEMPERATURE
        max_tokens = DEFAULT_MAX_TOKENS
        yes = False
    
    cmd_chat(TestArgs())
