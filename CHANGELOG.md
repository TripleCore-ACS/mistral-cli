# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

---

## [1.3.0] - 2025-01-08

### 🔐 Hinzugefügt - Sichere API-Key-Verwaltung

- **Neuer Befehl: `mistral auth`**
  - `mistral auth setup` - Interaktive API-Key-Einrichtung
  - `mistral auth status` - Zeigt Speicher-Status an
  - `mistral auth delete` - Löscht gespeicherten API-Key

- **System-Keyring-Integration**
  - macOS Keychain
  - GNOME Keyring (Linux)
  - Windows Credential Manager
  - Kein Klartext in Shell-Config-Dateien mehr nötig!

- **AES-256 Verschlüsselung als Fallback**
  - PBKDF2 mit 480.000 Iterationen (OWASP-Empfehlung)
  - Master-Passwort-basierte Schlüsselableitung
  - Verschlüsselte Datei: `~/.mistral-cli-key.enc`

### 🔐 Hinzugefügt - SFTP Support (Sichere Dateiübertragung)

- **Neues Tool: `upload_sftp`**
  - Sichere Dateiübertragung via SSH File Transfer Protocol
  - Vollständig verschlüsselte Übertragung (im Gegensatz zu FTP)
  - Empfohlene Alternative für sensible Daten

- **Authentifizierungs-Optionen**
  - Passwort-Authentifizierung (SFTP_PASS Umgebungsvariable)
  - SSH-Key-Authentifizierung (SFTP_KEY_PATH Umgebungsvariable)
  - Unterstützte Key-Typen: RSA, Ed25519, ECDSA

- **Umgebungsvariablen**
  - `SFTP_USER` - SFTP Benutzername
  - `SFTP_PASS` - SFTP Passwort
  - `SFTP_KEY_PATH` - Pfad zum SSH Private Key

- **Sicherheitsfeatures**
  - Pfad-Validierung für lokale Dateien
  - Keine Credentials im Log (wie bei FTP)
  - Automatische Host-Key-Verifikation
  - Timeout-Handling

### Geändert

- **Tool-Anzahl**
  - Von 13 auf 14 Tools erhöht
  - FTP-Upload jetzt explizit als "unverschlüsselt" markiert

- **`mistral_tools.py`**
  - Neue Funktion `_upload_sftp()` mit umfassender Fehlerbehandlung
  - Tool-Dispatcher um SFTP erweitert

- **`requirements.txt`**
  - `paramiko>=3.4.0` als optionale Dependency hinzugefügt

### Dokumentation

- Tool-Beschreibungen aktualisiert
- FTP vs SFTP Unterscheidung klargestellt

---

## [1.2.0] - 2025-01-08

### 🔒 Sicherheit - Erweiterte Bash Command Validation

- **Umfassende Command Injection Detection**
  - Command Chaining erkennung (`;`, `&&`, `||`, `|`, `\n`)
  - Subshell-Ausführung blockiert (`$()`, Backticks, Process Substitution)
  - Encoded Execution verhindert (`base64 | bash`, `xxd | sh`)
  - Variable Expansion erkannt (`$cmd`, `eval $DANGER`)
  - Interpreter-Ausführung blockiert (`python -c`, `perl -e`, `ruby -e`, `node -e`, `bash -c`)

- **Neue Sicherheitsfunktionen in `mistral_utils.py`**
  - `is_dangerous_command(command) -> Tuple[bool, str]` - Erweiterte Prüfung mit Begründung
  - `_check_single_command(command)` - Einzelbefehl-Analyse mit shlex
  - `request_confirmation(command, reason)` - Benutzer-Bestätigung für gefährliche Befehle
  - `is_safe_path(path, base_dir)` - Path Traversal Protection
  - `sanitize_for_log(text)` - Redaktiert API-Keys, Tokens, Passwords in Logs

- **Erweiterte Pattern-Erkennung**
  - 20+ Regex-Patterns für verschiedene Angriffsvektoren
  - Fork Bomb Varianten (`:(){:|:&};:`)
  - Device-Schreiboperationen (`> /dev/sda`, `dd of=/dev/`)
  - History-Manipulation (`history -c`, `> ~/.bash_history`)
  - Netzwerk-Backdoors (`nc -l -e`)
  - Remote Code Execution (`curl | bash`, `wget -O - | sh`)

- **Gefährliche Ziele**
  - System-kritische Verzeichnisse (`/`, `/etc`, `/usr`, `/var`, `/boot`, `/root`)
  - Home-Verzeichnis Varianten (`~`, `$HOME`)
  - Sensitive Dateien (`.ssh`, `.env`, `.bashrc`, `.gitconfig`, `.aws`)
  - Credentials (`id_rsa`, `.netrc`, `.npmrc`)

- **Log Sanitization**
  - API-Keys werden automatisch aus Logs entfernt
  - Tokens, Passwords, Secrets maskiert
  - FTP-Credentials in URLs redaktiert
  - Bearer Tokens geschützt

### Hinzugefügt

- **Benutzer-Bestätigungssystem**
  - Formatierte Warnung mit Befehl und Begründung
  - 3 Versuche für gültige Eingabe (j/n)
  - Alle Entscheidungen werden geloggt
  - Graceful Handling von Ctrl+C und EOF

- **Interpreter Detection**
  - Python, Perl, Ruby, Node.js, PHP, Lua, AWK
  - Code-Execution Flags erkannt (`-c`, `-e`, `--eval`)
  - Shell-Befehle mit `-c` Flag blockiert

- **Conditional Dangerous Commands**
  - `rm` nur mit `-rf`, `-fr`, `--recursive --force` gefährlich
  - `chmod` nur mit `777`, `000`, `-R` auf System-Pfaden
  - `curl`/`wget` nur mit Pipe oder `-o` zu gefährlichen Zielen

- **Test Suite**
  - 79 Security Tests (standalone, keine Dependencies)
  - Command Injection Tests
  - Path Validation Tests
  - Log Sanitization Tests

### Geändert

- **`mistral_utils.py`**
  - `is_dangerous_command()` gibt jetzt `Tuple[bool, str]` zurück
  - Neue Konstanten: `DANGEROUS_COMMANDS`, `CONDITIONAL_DANGEROUS`, `INTERPRETER_COMMANDS`, `SHELL_COMMANDS`
  - `get_version()` gibt "1.2.0" zurück

- **`mistral_tools.py`**
  - `execute_bash_command()` nutzt erweiterte Sicherheitsprüfung
  - Bessere Fehlerbehandlung mit spezifischen Meldungen

### Dokumentation

- CHANGELOG.md mit detaillierter Sicherheitsdokumentation
- Inline-Dokumentation für alle neuen Funktionen
- Beispiele in Docstrings

### Breaking Changes

- Keine API-Breaking Changes
- **Behavioral Change:** Manche Befehle die vorher durchgingen, triggern jetzt Confirmation Prompts

---

## [1.1.1] - 2025-01-07

### Behoben

- **Pfeiltasten im Chat-Modus** ⌨️
  - Verbesserte readline-Erkennung für macOS (libedit vs GNU readline)
  - Automatische Erkennung der readline-Variante (gnu, libedit, pyreadline3)
  - Separate Konfiguration für jede Variante
  - Zeigt readline-Typ in der Willkommensnachricht an
  - Bessere Fehlermeldung wenn readline nicht verfügbar

- **Neue Chat-Befehle**
  - `history` - Zeigt die letzten 10 Eingaben an

- **Verbesserte Eingabebehandlung**
  - EOFError (Ctrl+D) wird sauber abgefangen
  - Explizite Pfeiltasten-Bindings für GNU readline

### Dokumentation

- requirements.txt: Anleitung für `gnureadline` (macOS) und `pyreadline3` (Windows)

---

## [1.1.0] - 2025-01-07

### Hinzugefügt

- **Neues Modul `mistral_utils.py`** - Zentrales Utilities-Modul mit:
  - `get_client()` - Singleton-Pattern für Mistral Client (keine Duplikation mehr)
  - `setup_logging()` - Konfigurierbares Logging-System
  - `trim_messages()` - Automatisches Token-Management für lange Konversationen
  - Hilfsfunktionen für formatierte Ausgaben (`print_error`, `print_warning`, etc.)

- **Erweitertes Sicherheitssystem** 🔒
  - `RiskLevel` Enum mit Stufen: CRITICAL, HIGH, MEDIUM, LOW, SAFE
  - `analyze_command_risk()` - Detaillierte Risikoanalyse für Befehle
  - `get_command_risk_info()` - Gibt Risiko-Details als Dictionary zurück
  - `is_dangerous_command()` - Prüft auf CRITICAL/HIGH Risiken
  - `format_risk_warning()` - Formatierte Konsolenausgabe für Warnungen
  - Kategorisierte gefährliche Muster:
    - `filesystem_destruction` - rm -rf, dd, mkfs, etc.
    - `privilege_escalation` - chmod 777, chown auf System
    - `fork_bombs` - :(){:|:&};: und Varianten
    - `remote_code_execution` - curl|bash, wget|sh, etc.
    - `data_exfiltration` - Senden sensibler Daten
    - `system_modification` - Änderungen an /etc
    - `network_dangerous` - iptables -F, ufw disable
    - `history_manipulation` - history -c
    - `credential_exposure` - echo password

- **URL-Validierung** 🌐
  - `validate_url()` - Prüft URLs auf Sicherheit
  - Blockiert lokale/private IP-Adressen (127.0.0.1, 192.168.x.x, etc.)
  - Blockiert localhost-Varianten
  - Erlaubt nur http, https, ftp Schemas

- **Pfad-Validierung** 📁
  - `validate_path()` - Prüft Dateipfade auf Sicherheit
  - Erkennt Path Traversal Angriffe (../)
  - Blockiert Zugriff auf sensible Pfade (/etc/passwd, ~/.ssh/, etc.)
  - `check_file_operation_safety()` - Prüft Dateioperationen

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

- **Neue Chat-Befehle**
  - `clear` - Löscht die Konversationshistorie

- **Neue CLI-Optionen**
  - `--debug` - Aktiviert Debug-Ausgaben auf der Konsole
  - `--version` - Zeigt Versionsnummer

- **Type Hints**
  - Vollständige Type Annotations in allen Modulen
  - Verbesserte IDE-Unterstützung und Autovervollständigung

- **Input-Validierungen**
  - Suchanfragen: min. 2, max. 500 Zeichen
  - JSON-Parsing: max. 1 MB
  - CSV-Parsing: max. 10 MB
  - Suchergebnisse: max. 10

### Geändert

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
  - Alle Tool-Funktionen nutzen jetzt Sicherheitsvalidierungen
  - URL-Validierung für `fetch_url` und `download_file`
  - Pfad-Validierung für alle Dateioperationen
  - Erweiterte Bash-Sicherheitsprüfung mit Risikostufen
  - Bessere Fehlermeldungen (PermissionError, FileNotFoundError)
  - Tool-Beschreibungen mit Sicherheitshinweisen aktualisiert

- **`requirements.txt`**
  - `python-dotenv>=1.0.0` hinzugefügt
  - Bessere Dokumentation und Kategorisierung
  - Entwicklungs-Abhängigkeiten dokumentiert (pytest, black, etc.)

### Behoben

- Duplizierter Code für `get_client()` in mehreren Dateien
- Fehlende Fehlerbehandlung bei ungültigen Tool-Argumenten (JSON-Parsing)
- Potenzielle Token-Limit-Überschreitungen bei langen Chats
- Fehlende Validierung von Benutzereingaben

### 🔒 Sicherheit

- **Gefährliche Befehle werden blockiert:**
  - `rm -rf /` und Varianten
  - Fork-Bombs (`:(){:|:&};:`)
  - Remote Code Execution (`curl | bash`)
  - Destruktive `dd`-Befehle
  - Privilege Escalation Versuche

- **URL-Sicherheit:**
  - Lokale IPs blockiert (127.0.0.1, localhost)
  - Private Netzwerke blockiert (10.x.x.x, 192.168.x.x, 172.16.x.x)
  - Nur sichere Schemas erlaubt (http, https, ftp)

- **Pfad-Sicherheit:**
  - Path Traversal verhindert
  - Systemverzeichnisse geschützt (/etc, /root, /proc, /sys)
  - SSH-Verzeichnis geschützt (~/.ssh)

### Dokumentation

- README.md aktualisiert mit neuen Features
- Neue Abschnitte: Logging, .env Konfiguration, Debug-Modus
- Aktualisierte Sicherheitshinweise
- CHANGELOG.md erstellt

---

## [1.0.5] - 2025-01-06

### Hinzugefügt

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

[1.2.0]: https://github.com/TripleCore-ACS/mistral-cli/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/TripleCore-ACS/mistral-cli/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/TripleCore-ACS/mistral-cli/compare/v1.0.5...v1.1.0
[1.0.5]: https://github.com/TripleCore-ACS/mistral-cli/releases/tag/v1.0.5
