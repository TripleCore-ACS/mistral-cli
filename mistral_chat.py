#!/usr/bin/env python3
"""
Mistral CLI - Chat Mode
Interactive chat with tool support and token management
"""

import sys
import json
import argparse
from typing import List, Dict, Any, Optional

# Lokale Imports
from mistral_utils import (
    get_client,
    logger,
    trim_messages,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
)
from mistral_tools import TOOLS, execute_tool


# ASCII Logo
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


def print_welcome(model: str) -> None:
    """
    Zeigt die Willkommensnachricht an.
    
    Args:
        model: Das verwendete Modell
    """
    print(LOGO)
    print("Bienvenue! 🇫🇷\n")
    print("Mistral AI Chat with Tool Support")
    print("(Enter 'exit', 'quit' or 'q' to exit)")
    print("(Enter 'clear' to clear conversation history)")
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


def cmd_chat(args: argparse.Namespace) -> None:
    """
    Interaktiver Chat-Modus mit Tool-Unterstützung.
    
    Args:
        args: Kommandozeilen-Argumente mit model, temperature, max_tokens, yes
    """
    client = get_client()
    
    # Parameter extrahieren
    model: str = getattr(args, 'model', DEFAULT_MODEL)
    temperature: float = getattr(args, 'temperature', DEFAULT_TEMPERATURE)
    max_tokens: int = getattr(args, 'max_tokens', DEFAULT_MAX_TOKENS)
    auto_confirm: bool = getattr(args, 'yes', False)
    
    logger.info(f"Chat gestartet mit Modell: {model}, Temp: {temperature}, MaxTokens: {max_tokens}")

    print_welcome(model)

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
        except Exception as e:
            logger.error(f"Fehler im Chat: {e}")
            print(f"\n❌ Fehler: {str(e)}\n", file=sys.stderr)


# Für direkten Aufruf (z.B. zum Testen)
if __name__ == '__main__':
    # Einfache Test-Args erstellen
    class TestArgs:
        model = DEFAULT_MODEL
        temperature = DEFAULT_TEMPERATURE
        max_tokens = DEFAULT_MAX_TOKENS
        yes = False
    
    cmd_chat(TestArgs())
