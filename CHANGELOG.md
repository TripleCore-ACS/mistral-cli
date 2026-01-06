# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

---

## [1.1.0] - 2025-01-07

### 🆕 Hinzugefügt

- **Neues Modul `mistral_utils.py`** - Zentrales Utilities-Modul mit:
  - `get_client()` - Singleton-Pattern für Mistral Client (keine Duplikation mehr)
  - `setup_logging()` - Konfigurierbares Logging-System
  - `trim_messages()` - Automatisches Token-Management für lange Konversationen
  - `is_dangerous_command()` - Sicherheitsprüfung für Bash-Befehle
  - `sanitize_path()` - Pfad-Bereinigung und Expansion
  - Hilfsfunktionen für formatierte Ausgaben (`print_error`, `print_warning`, etc.)

- **Logging-System**
  - Automatisches Logging nach `~/.mistral-cli.log`
  - Konfigurierbare Log-Level (DEBUG, INFO, WARNING, ERROR)
  - Optionale Konsolen-Ausgabe im Debug-Modus

- **`.env` Datei-Support**
  - Automatisches Laden von Umgebungsvariablen aus `.env` oder `~/.mistral-cli.env`
  - Neue Abhängigkeit: `python-dotenv`

- **Token-Management**
  - `trim_messages()` kürzt automatisch alte Nachrichten bei langen Konversationen
  - Verhindert Token-Limit-Überschreitungen
  - System-Nachrichten werden optional beibehalten

- **Sicherheitsverbesserungen**
  - Blockierung gefährlicher Bash-Befehle (z.B. `rm -rf /`, Fork-Bombs)
  - Warnung bei potenziell unsicheren Befehlen im `exec`-Modus
  - FTP-Credentials können über Umgebungsvariablen (`FTP_USER`, `FTP_PASS`) gesetzt werden

- **Neue Chat-Befehle**
  - `clear` - Löscht die Konversationshistorie

- **Neue CLI-Optionen**
  - `--debug` - Aktiviert Debug-Ausgaben auf der Konsole
  - `--version` - Zeigt Versionsnummer

- **Type Hints**
  - Vollständige Type Annotations in allen Modulen
  - Verbesserte IDE-Unterstützung und Autovervollständigung

### ♻️ Geändert

- **`mistral_cli.py`**
  - Nutzt jetzt `mistral_utils` statt eigener `get_client()` Funktion
  - Verbesserte `argparse` Hilfetexte mit Beispielen
  - Sicherheitsprüfung vor Bash-Ausführung im `exec`-Modus
  - Refaktorierter Code mit Type Hints

- **`mistral_chat.py`**
  - Automatisches Token-Trimming bei langen Konversationen
  - Neuer `clear`-Befehl zum Löschen der Historie
  - Ausgelagerte `process_tool_calls()` Funktion
  - Verbesserte Fehlerbehandlung bei Tool-Calls

- **`mistral_tools.py`**
  - Alle Tool-Funktionen als private Funktionen refaktoriert (`_execute_bash_command`, etc.)
  - Zentraler `execute_tool()` Dispatcher mit Dictionary-Mapping
  - Durchgängiges Logging für alle Tool-Operationen
  - Standardisierte Ergebnis-Struktur mit `_create_result()`
  - Automatische Verzeichniserstellung bei Dateioperationen

- **`requirements.txt`**
  - `python-dotenv>=1.0.0` hinzugefügt
  - Bessere Dokumentation und Kategorisierung
  - Entwicklungs-Abhängigkeiten dokumentiert (pytest, black, etc.)

### 🔧 Behoben

- Duplizierter Code für `get_client()` in mehreren Dateien
- Fehlende Fehlerbehandlung bei ungültigen Tool-Argumenten (JSON-Parsing)
- Potenzielle Token-Limit-Überschreitungen bei langen Chats

### 📚 Dokumentation

- README.md aktualisiert mit neuen Features
- Neue Abschnitte: Logging, .env Konfiguration, Debug-Modus
- Aktualisierte Sicherheitshinweise

---

## [1.0.5] - 2025-01-06

### 🆕 Hinzugefügt

- Initial Public Release
- Interaktiver Chat-Modus mit Function Calling
- 13 integrierte Tools:
  - Dateisystem: read, write, rename, copy, move, bash
  - Web: search, fetch, download, ftp_upload
  - Daten: parse_json, parse_csv, get_image_info
- Textvervollständigung (`complete`)
- Bash-Befehlsgenerierung (`exec`)
- Modellübersicht (`models`)
- TUI-Modus (Text User Interface)
- Deutsche Dokumentation
- MIT Lizenz

---

## Versionsschema

- **MAJOR.MINOR.PATCH**
  - MAJOR: Inkompatible API-Änderungen
  - MINOR: Neue Features (abwärtskompatibel)
  - PATCH: Bugfixes (abwärtskompatibel)

---

[1.1.0]: https://github.com/TripleCore-ACS/mistral-cli/compare/v1.0.5...v1.1.0
[1.0.5]: https://github.com/TripleCore-ACS/mistral-cli/releases/tag/v1.0.5
