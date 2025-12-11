#!/usr/bin/env python3
"""
Mistral CLI - Kommandozeilenanwendung für Mistral AI mit Subcommands
"""

import os
import sys
import argparse
import subprocess
import re
from mistralai import Mistral
from mistral_tools import TOOLS, execute_tool
from mistral_chat import cmd_chat


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


def cmd_complete(args):
    """Einzelne Textvervollständigung."""
    if not args.prompt:
        print("Fehler: Bitte geben Sie einen Prompt an", file=sys.stderr)
        sys.exit(1)

    client = get_client()
    prompt = ' '.join(args.prompt)

    try:
        response = client.chat.complete(
            model=args.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )

        print(response.choices[0].message.content)

    except Exception as e:
        print(f"Fehler: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_exec(args):
    """Generiert und führt Bash-Befehle aus."""
    if not args.task:
        print("Fehler: Bitte geben Sie eine Aufgabe an", file=sys.stderr)
        sys.exit(1)

    client = get_client()
    task = ' '.join(args.task)

    # System-Prompt für Befehlsgenerierung
    system_prompt = """Du bist ein Bash-Experte. Generiere ausführbare Bash-Befehle für die gegebene Aufgabe.

WICHTIG:
- Gib NUR die Bash-Befehle aus, keine Erklärungen
- Jeder Befehl in einer eigenen Zeile
- Verwende keine Markdown-Code-Blöcke
- Beginne direkt mit den Befehlen
- Verwende sichere Befehle
- Vermeide gefährliche Operationen wie rm -rf / oder ähnliches

Beispiel für korrekte Ausgabe:
mkdir test_folder
cd test_folder
echo "Hello World" > hello.txt"""

    try:
        print(f"Generiere Befehle für: {task}\n")

        response = client.chat.complete(
            model=args.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task}
            ],
            temperature=0.3,
            max_tokens=args.max_tokens
        )

        commands_text = response.choices[0].message.content.strip()

        # Entferne mögliche Markdown-Code-Blöcke
        commands_text = re.sub(r'^```(?:bash)?\n?', '', commands_text)
        commands_text = re.sub(r'\n?```$', '', commands_text)

        # Extrahiere Befehle (eine Zeile pro Befehl)
        commands = [cmd.strip() for cmd in commands_text.split('\n') if cmd.strip() and not cmd.strip().startswith('#')]

        if not commands:
            print("Fehler: Keine Befehle generiert", file=sys.stderr)
            sys.exit(1)

        # Zeige generierte Befehle
        print("Generierte Befehle:")
        print("-" * 50)
        for i, cmd in enumerate(commands, 1):
            print(f"{i}. {cmd}")
        print("-" * 50)

        # Bestätigung einholen
        if not args.yes:
            response = input("\nBefehle ausführen? (y/n): ").strip().lower()
            if response not in ['y', 'yes', 'j', 'ja']:
                print("Abgebrochen.")
                return

        # Befehle ausführen
        print("\nFühre Befehle aus...\n")
        for i, cmd in enumerate(commands, 1):
            print(f"[{i}/{len(commands)}] Ausführen: {cmd}")
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )

                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)

                if result.returncode != 0:
                    print(f"Warnung: Befehl schlug fehl mit Exit-Code {result.returncode}", file=sys.stderr)
                    if not args.force:
                        cont = input("Fortfahren? (y/n): ").strip().lower()
                        if cont not in ['y', 'yes', 'j', 'ja']:
                            print("Abgebrochen.")
                            return

            except Exception as e:
                print(f"Fehler beim Ausführen von '{cmd}': {str(e)}", file=sys.stderr)
                if not args.force:
                    return

        print("\nAlle Befehle ausgeführt.")

    except Exception as e:
        print(f"Fehler: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_models(args):
    """Zeigt verfügbare Modelle an."""
    client = get_client()

    try:
        models = client.models.list()
        print("Verfügbare Mistral Modelle:\n")

        for model in models.data:
            print(f"  - {model.id}")
            if hasattr(model, 'description') and model.description:
                print(f"    {model.description}")
            print()

    except Exception as e:
        print(f"Fehler: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_tui(args):
    """Startet die TUI (Text User Interface)."""
    try:
        from mistral_tui import run_tui
        run_tui()
    except ImportError as e:
        print("Fehler: TUI-Module nicht verfügbar.", file=sys.stderr)
        print(f"Details: {str(e)}", file=sys.stderr)
        print("Bitte installieren Sie die Abhängigkeiten:", file=sys.stderr)
        print("  pip install textual", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"Fehler beim Start der TUI: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Mistral AI CLI - Interagiere mit Mistral AI Modellen',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(
        title='Befehle',
        description='Verfügbare Befehle',
        dest='command',
        help='Verwenden Sie "mistral <befehl> --help" für weitere Informationen'
    )

    # Chat Command
    parser_chat = subparsers.add_parser(
        'chat',
        help='Starte interaktiven Chat-Modus'
    )
    parser_chat.add_argument(
        '-m', '--model',
        default='mistral-small-latest',
        help='Das zu verwendende Mistral-Modell (default: mistral-small-latest)'
    )
    parser_chat.add_argument(
        '-t', '--temperature',
        type=float,
        default=0.7,
        help='Temperatur für die Generierung (0.0 - 1.0, default: 0.7)'
    )
    parser_chat.add_argument(
        '--max-tokens',
        type=int,
        default=1024,
        help='Maximale Anzahl der zu generierenden Tokens (default: 1024)'
    )
    parser_chat.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Tool-Ausführungen automatisch bestätigen (ohne Nachfrage)'
    )
    parser_chat.set_defaults(func=cmd_chat)

    # Complete Command
    parser_complete = subparsers.add_parser(
        'complete',
        help='Einmalige Textvervollständigung'
    )
    parser_complete.add_argument(
        'prompt',
        nargs='+',
        help='Der Prompt für die Vervollständigung'
    )
    parser_complete.add_argument(
        '-m', '--model',
        default='mistral-small-latest',
        help='Das zu verwendende Mistral-Modell (default: mistral-small-latest)'
    )
    parser_complete.add_argument(
        '-t', '--temperature',
        type=float,
        default=0.7,
        help='Temperatur für die Generierung (0.0 - 1.0, default: 0.7)'
    )
    parser_complete.add_argument(
        '--max-tokens',
        type=int,
        default=1024,
        help='Maximale Anzahl der zu generierenden Tokens (default: 1024)'
    )
    parser_complete.set_defaults(func=cmd_complete)

    # Exec Command
    parser_exec = subparsers.add_parser(
        'exec',
        help='Generiere und führe Bash-Befehle aus'
    )
    parser_exec.add_argument(
        'task',
        nargs='+',
        help='Die Aufgabe, die ausgeführt werden soll'
    )
    parser_exec.add_argument(
        '-m', '--model',
        default='mistral-small-latest',
        help='Das zu verwendende Mistral-Modell (default: mistral-small-latest)'
    )
    parser_exec.add_argument(
        '--max-tokens',
        type=int,
        default=1024,
        help='Maximale Anzahl der zu generierenden Tokens (default: 1024)'
    )
    parser_exec.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Befehle ohne Bestätigung ausführen'
    )
    parser_exec.add_argument(
        '-f', '--force',
        action='store_true',
        help='Bei Fehlern fortfahren'
    )
    parser_exec.set_defaults(func=cmd_exec)

    # Models Command
    parser_models = subparsers.add_parser(
        'models',
        help='Liste verfügbare Modelle auf'
    )
    parser_models.set_defaults(func=cmd_models)

    # TUI Command
    parser_tui = subparsers.add_parser(
        'tui',
        help='Starte die interaktive Text User Interface (TUI)'
    )
    parser_tui.set_defaults(func=cmd_tui)

    # Parse arguments
    args = parser.parse_args()

    # Wenn kein Befehl angegeben wurde, zeige Hilfe
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    # Führe den entsprechenden Befehl aus
    args.func(args)


if __name__ == '__main__':
    main()
