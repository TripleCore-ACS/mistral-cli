#!/usr/bin/env python3
"""
Mistral CLI - Chat Mode
Interactive chat with tool support
"""

import os
import sys
import json
from mistralai import Mistral
from mistral_tools import TOOLS, execute_tool


def get_client():
    """Initialisiert und gibt einen Mistral Client zurück."""
    api_key = os.environ.get('MISTRAL_API_KEY')
    if not api_key:
        print("Fehler: MISTRAL_API_KEY Umgebungsvariable ist nicht gesetzt.", file=sys.stderr)
        print("\nBitte setzen Sie den API-Key:", file=sys.stderr)
        print("  export MISTRAL_API_KEY='ihr-api-key'", file=sys.stderr)
        print("\nOder speichern Sie ihn dauerhaft in ~/.bashrc oder ~/.zshrc", file=sys.stderr)
        sys.exit(1)
    return Mistral(api_key=api_key)


def cmd_chat(args):
    """Interaktiver Chat-Modus mit Tool-Unterstützung."""
    client = get_client()

    # ASCII Logo
    logo = r"""
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

    print(logo)
    print("Bienvenue! 🇫🇷\n")
    print("Mistral AI Chat with Tool Support")
    print("(Enter 'exit' or 'quit' to exit)")
    print(f"Model: {args.model}")
    print("Available Tools:")
    print("  - Bash commands, Files (read/write/rename/copy/move)")
    print("  - Web (search, URL fetch, downloads, FTP upload)")
    print("  - Data processing (JSON/CSV parsing)")
    print("  - Image analysis (format, size, dimensions)\n")

    messages = []
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Au revoir!")
                break

            if not user_input:
                continue

            messages.append({"role": "user", "content": user_input})

            # API-Anfrage mit Tools senden
            response = client.chat.complete(
                model=args.model,
                messages=messages,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                tools=TOOLS,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message

            # Prüfe ob Tool Calls vorhanden sind
            if assistant_message.tool_calls:
                # Füge Assistant-Nachricht zu Messages hinzu
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": assistant_message.tool_calls
                })

                # Führe alle Tool Calls aus
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Tool ausführen
                    tool_result = execute_tool(tool_name, tool_args, auto_confirm=getattr(args, 'yes', False))

                    # Tool-Ergebnis zu Messages hinzufügen
                    messages.append({
                        "role": "tool",
                        "name": tool_name,
                        "content": json.dumps(tool_result),
                        "tool_call_id": tool_call.id
                    })

                # Zweite API-Anfrage mit Tool-Ergebnissen
                response = client.chat.complete(
                    model=args.model,
                    messages=messages,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                    tools=TOOLS,
                    tool_choice="auto"
                )

                assistant_message = response.choices[0].message

            # Zeige die finale Antwort
            if assistant_message.content:
                messages.append({"role": "assistant", "content": assistant_message.content})
                print(f"\nMistral: {assistant_message.content}\n")
            else:
                print()

        except KeyboardInterrupt:
            print("\n\nAu revoir!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n", file=sys.stderr)
