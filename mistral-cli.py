#!/usr/bin/env python3
"""
Mistral CLI - Kommandozeilenanwendung für Mistral AI mit Subcommands

Eine umfassende CLI-Anwendung für die Mistral AI API mit 13 integrierten Tools,
mehreren Interaktionsmodi und deutscher Dokumentation.

Repository: https://github.com/TripleCore-ACS/mistral-cli
Lizenz: MIT
"""

import sys
import argparse
import subprocess
import re
from typing import List, Optional

# Lokale Imports
from mistral_utils import (
    get_client,
    logger,
    is_dangerous_command,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
)
from mistral_tools import TOOLS, execute_tool
from mistral_chat import cmd_chat


def cmd_complete(args: argparse.Namespace) -> None:
    """
    Einzelne Textvervollständigung.
    
    Args:
        args: Kommandozeilen-Argumente
    """
    if not args.prompt:
        logger.error("Kein Prompt angegeben")
        print("Fehler: Bitte geben Sie einen Prompt an", file=sys.stderr)
        sys.exit(1)

    client = get_client()
    prompt = ' '.join(args.prompt)
    
    logger.info(f"Complete-Anfrage: {prompt[:50]}...")

    try:
        response = client.chat.complete(
            model=args.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )

        result = response.choices[0].message.content
        print(result)
        logger.info(f"Complete erfolgreich, {len(result)} Zeichen generiert")

    except Exception as e:
        logger.error(f"Complete fehlgeschlagen: {e}")
        print(f"Fehler: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_exec(args: argparse.Namespace) -> None:
    """
    Generiert und führt Bash-Befehle aus.
    
    Args:
        args: Kommandozeilen-Argumente
    """
    if not args.task:
        logger.error("Keine Aufgabe angegeben")
        print("Fehler: Bitte geben Sie eine Aufgabe an", file=sys.stderr)
        sys.exit(1)

    client = get_client()
    task = ' '.join(args.task)
    
    logger.info(f"Exec-Anfrage: {task}")

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
        commands: List[str] = [
            cmd.strip() 
            for cmd in commands_text.split('\n') 
            if cmd.strip() and not cmd.strip().startswith('#')
        ]

        if not commands:
            logger.warning("Keine Befehle generiert")
            print("Fehler: Keine Befehle generiert", file=sys.stderr)
            sys.exit(1)

        # Sicherheitsprüfung
        dangerous_found = False
        for cmd in commands:
            if is_dangerous_command(cmd):
                print(f"⚠️  WARNUNG: Potenziell gefährlicher Befehl erkannt: {cmd}", file=sys.stderr)
                dangerous_found = True

        if dangerous_found and not args.force:
            print("\n❌ Ausführung abgebrochen wegen gefährlicher Befehle.", file=sys.stderr)
            print("   Verwende --force um die Ausführung zu erzwingen (nicht empfohlen).", file=sys.stderr)
            logger.warning("Ausführung wegen gefährlicher Befehle abgebrochen")
            return

        # Zeige generierte Befehle
        print("Generierte Befehle:")
        print("-" * 50)
        for i, cmd in enumerate(commands, 1):
            print(f"{i}. {cmd}")
        print("-" * 50)

        # Bestätigung einholen
        if not args.yes:
            response_input = input("\nBefehle ausführen? (y/n): ").strip().lower()
            if response_input not in ['y', 'yes', 'j', 'ja']:
                print("Abgebrochen.")
                logger.info("Benutzer hat Ausführung abgebrochen")
                return

        # Befehle ausführen
        print("\nFühre Befehle aus...\n")
        logger.info(f"Führe {len(commands)} Befehle aus")
        
        import os
        for i, cmd in enumerate(commands, 1):
            print(f"[{i}/{len(commands)}] Ausführen: {cmd}")
            logger.debug(f"Befehl {i}: {cmd}")
            
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    timeout=30
                )

                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)

                if result.returncode != 0:
                    logger.warning(f"Befehl fehlgeschlagen mit Exit-Code {result.returncode}: {cmd}")
                    print(f"Warnung: Befehl schlug fehl mit Exit-Code {result.returncode}", file=sys.stderr)
                    if not args.force:
                        cont = input("Fortfahren? (y/n): ").strip().lower()
                        if cont not in ['y', 'yes', 'j', 'ja']:
                            print("Abgebrochen.")
                            return

            except subprocess.TimeoutExpired:
                logger.error(f"Timeout bei Befehl: {cmd}")
                print(f"Fehler: Timeout bei '{cmd}'", file=sys.stderr)
                if not args.force:
                    return
            except Exception as e:
                logger.error(f"Fehler bei Befehl {cmd}: {e}")
                print(f"Fehler beim Ausführen von '{cmd}': {str(e)}", file=sys.stderr)
                if not args.force:
                    return

        print("\n✅ Alle Befehle ausgeführt.")
        logger.info("Alle Befehle erfolgreich ausgeführt")

    except Exception as e:
        logger.error(f"Exec fehlgeschlagen: {e}")
        print(f"Fehler: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_models(args: argparse.Namespace) -> None:
    """
    Zeigt verfügbare Modelle an.
    
    Args:
        args: Kommandozeilen-Argumente
    """
    client = get_client()
    logger.info("Rufe Modellliste ab")

    try:
        models = client.models.list()
        print("Verfügbare Mistral Modelle:\n")

        for model in models.data:
            print(f"  - {model.id}")
            if hasattr(model, 'description') and model.description:
                print(f"    {model.description}")
            print()
        
        logger.info(f"{len(models.data)} Modelle gefunden")

    except Exception as e:
        logger.error(f"Modellabruf fehlgeschlagen: {e}")
        print(f"Fehler: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_tui(args: argparse.Namespace) -> None:
    """
    Startet die TUI (Text User Interface).
    
    Args:
        args: Kommandozeilen-Argumente
    """
    logger.info("Starte TUI")
    try:
        from mistral_tui import run_tui
        run_tui()
    except ImportError as e:
        logger.error(f"TUI-Import fehlgeschlagen: {e}")
        print("Fehler: TUI-Module nicht verfügbar.", file=sys.stderr)
        print(f"Details: {str(e)}", file=sys.stderr)
        print("Bitte installieren Sie die Abhängigkeiten:", file=sys.stderr)
        print("  pip install textual", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"TUI-Start fehlgeschlagen: {e}")
        print(f"Fehler beim Start der TUI: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """
    Erstellt und konfiguriert den Argument-Parser.
    
    Returns:
        Konfigurierter ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description='Mistral AI CLI - Interagiere mit Mistral AI Modellen',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  mistral chat                      Starte interaktiven Chat
  mistral complete "Erkläre Python" Einmalige Vervollständigung
  mistral exec "Erstelle Ordner"    Generiere und führe Bash aus
  mistral models                    Liste verfügbare Modelle

Mehr Informationen: https://github.com/TripleCore-ACS/mistral-cli
"""
    )

    # Globale Optionen
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Aktiviere Debug-Ausgaben'
    )

    subparsers = parser.add_subparsers(
        title='Befehle',
        description='Verfügbare Befehle',
        dest='command',
        help='Verwenden Sie "mistral <befehl> --help" für weitere Informationen'
    )

    # =========================================================================
    # Chat Command
    # =========================================================================
    parser_chat = subparsers.add_parser(
        'chat',
        help='Starte interaktiven Chat-Modus mit Tool-Unterstützung',
        description='Interaktiver Chat-Modus mit 13 integrierten Tools für Dateioperationen, Web-Suche, und mehr.'
    )
    parser_chat.add_argument(
        '-m', '--model',
        default=DEFAULT_MODEL,
        help=f'Das zu verwendende Mistral-Modell (default: {DEFAULT_MODEL})'
    )
    parser_chat.add_argument(
        '-t', '--temperature',
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f'Temperatur für die Generierung (0.0 - 1.0, default: {DEFAULT_TEMPERATURE})'
    )
    parser_chat.add_argument(
        '--max-tokens',
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f'Maximale Anzahl der zu generierenden Tokens (default: {DEFAULT_MAX_TOKENS})'
    )
    parser_chat.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Tool-Ausführungen automatisch bestätigen (ohne Nachfrage)'
    )
    parser_chat.set_defaults(func=cmd_chat)

    # =========================================================================
    # Complete Command
    # =========================================================================
    parser_complete = subparsers.add_parser(
        'complete',
        help='Einmalige Textvervollständigung',
        description='Sendet einen einzelnen Prompt an Mistral und gibt die Antwort aus.'
    )
    parser_complete.add_argument(
        'prompt',
        nargs='+',
        help='Der Prompt für die Vervollständigung'
    )
    parser_complete.add_argument(
        '-m', '--model',
        default=DEFAULT_MODEL,
        help=f'Das zu verwendende Mistral-Modell (default: {DEFAULT_MODEL})'
    )
    parser_complete.add_argument(
        '-t', '--temperature',
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f'Temperatur für die Generierung (0.0 - 1.0, default: {DEFAULT_TEMPERATURE})'
    )
    parser_complete.add_argument(
        '--max-tokens',
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f'Maximale Anzahl der zu generierenden Tokens (default: {DEFAULT_MAX_TOKENS})'
    )
    parser_complete.set_defaults(func=cmd_complete)

    # =========================================================================
    # Exec Command
    # =========================================================================
    parser_exec = subparsers.add_parser(
        'exec',
        help='Generiere und führe Bash-Befehle aus',
        description='Generiert Bash-Befehle basierend auf einer Beschreibung und führt diese optional aus.'
    )
    parser_exec.add_argument(
        'task',
        nargs='+',
        help='Die Aufgabe, die ausgeführt werden soll'
    )
    parser_exec.add_argument(
        '-m', '--model',
        default=DEFAULT_MODEL,
        help=f'Das zu verwendende Mistral-Modell (default: {DEFAULT_MODEL})'
    )
    parser_exec.add_argument(
        '--max-tokens',
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f'Maximale Anzahl der zu generierenden Tokens (default: {DEFAULT_MAX_TOKENS})'
    )
    parser_exec.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Befehle ohne Bestätigung ausführen'
    )
    parser_exec.add_argument(
        '-f', '--force',
        action='store_true',
        help='Bei Fehlern fortfahren und Sicherheitsprüfungen ignorieren'
    )
    parser_exec.set_defaults(func=cmd_exec)

    # =========================================================================
    # Models Command
    # =========================================================================
    parser_models = subparsers.add_parser(
        'models',
        help='Liste verfügbare Modelle auf',
        description='Zeigt alle verfügbaren Mistral AI Modelle an.'
    )
    parser_models.set_defaults(func=cmd_models)

    # =========================================================================
    # TUI Command
    # =========================================================================
    parser_tui = subparsers.add_parser(
        'tui',
        help='Starte die interaktive Text User Interface (TUI)',
        description='Startet eine grafische Text-Benutzeroberfläche im Terminal.'
    )
    parser_tui.set_defaults(func=cmd_tui)

    return parser


def main() -> None:
    """Haupteinstiegspunkt der CLI-Anwendung."""
    parser = create_parser()
    args = parser.parse_args()

    # Debug-Modus aktivieren
    if getattr(args, 'debug', False):
        import logging
        logger.setLevel(logging.DEBUG)
        # Füge Console-Handler für Debug hinzu
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.debug("Debug-Modus aktiviert")

    # Wenn kein Befehl angegeben wurde, zeige Hilfe
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    logger.info(f"Befehl gestartet: {args.command}")
    
    # Führe den entsprechenden Befehl aus
    args.func(args)


if __name__ == '__main__':
    main()
