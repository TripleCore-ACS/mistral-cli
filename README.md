# Mistral CLI

Eine leistungsstarke Kommandozeilenanwendung für Mistral AI mit erweiterten Tool-Funktionen.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Mistral AI](https://img.shields.io/badge/Mistral-AI-orange.svg)](https://mistral.ai)

## Features

### 🚀 Hauptfunktionen
- **Interaktiver Chat** mit Function Calling
- **Bash-Befehlsgenerierung und -ausführung**
- **Textvervollständigung**
- **Modellübersicht**
- **TUI-Modus** (Text User Interface)

### 🛠️ 14 Integrierte Tools

#### Dateisystem
- Dateien lesen, schreiben, umbenennen
- Dateien/Ordner kopieren und verschieben
- Bash-Befehle ausführen

#### Web & Netzwerk
- Web-Suche (DuckDuckGo)
- URL-Inhalte abrufen
- Dateien herunterladen
- FTP-Upload (unverschlüsselt)
- **SFTP-Upload (verschlüsselt)** 🆕

#### Datenverarbeitung
- JSON parsen und durchsuchen
- CSV-Dateien lesen und analysieren
- Bildanalyse (Format, Größe, Dimensionen)

### Neu in v1.5.2 🆕

- **🏗️ Modulare Architektur** - Professionelle Python-Paketstruktur
  - Von 2 monolithischen Dateien → 25 fokussierte Module
  - Klare Trennung: `core/`, `security/`, `auth/`, `utils/`, `tools/`
  - Bessere Wartbarkeit, Testbarkeit und Erweiterbarkeit
  - 100% Rückwärtskompatibel

- **🧪 Umfassende Test-Suite** - 424 Unit-Tests mit pytest
  - ✅ 100% Erfolgsquote (424/424 Tests bestehen)
  - 📈 40% Code Coverage (Security-Module: 90%+)
  - Automatisierte Security-Tests (236 Tests)
  - Performance-Benchmarks (< 50µs)
  - `./run_tests.sh` - Komfortabler Test-Runner

- **🔐 Sichere API-Key-Verwaltung** - Kein Klartext mehr in Shell-Configs!
  - System-Keyring (macOS Keychain, GNOME Keyring, Windows Credential Manager)
  - AES-256 Verschlüsselung als Fallback
  - Interaktive Einrichtung: `./mistral auth setup`

- **🔒 SFTP-Support** - Sichere Dateiübertragung via SSH
  - Passwort-Authentifizierung
  - SSH-Key-Support (RSA, Ed25519, ECDSA)
  - Verschlüsselte Alternative zu FTP

- **🛠️ 14 Tools** - Neues Tool `upload_sftp`

### Neu in v1.2.0

- **Erweiterte Sicherheitsprüfungen** - Command Injection Detection
- **Log Sanitization** - Keine Credentials in Logs
- **URL-Validierung** - SSRF-Schutz
- **Download-Limits** - Max. 100MB

### Neu in v1.1.0

- **Bugfix: Pfeiltasten im Chat-Modus**
- **Neue Chat-Befehle** - `history` - Zeigt die letzten 10 Eingaben an
- **Verbesserte Eingabebehandlung** - EOFError (Ctrl+D) wird sauber abgefangen
  
### v1.1.0

- **Zentrales Logging** - Alle Aktionen werden in `~/.mistral-cli.log` protokolliert
- **`.env` Support** - API-Keys und Konfiguration via `.env`-Dateien
- **Token-Management** - Automatisches Kürzen langer Konversationen
- **Sicherheitsprüfungen** - Blockierung gefährlicher Bash-Befehle
- **Debug-Modus** - Detaillierte Ausgaben mit `--debug`
- **Type Hints** - Vollständige Typ-Annotationen

## Installation

### Voraussetzungen
- Python 3.8 oder höher
- Mistral AI API-Key ([hier erhalten](https://console.mistral.ai))

### Schritt 1: Repository klonen
```bash
git clone https://github.com/TripleCore-ACS/mistral-cli.git
cd mistral-cli
```

### Schritt 2: Virtuelle Umgebung erstellen
```bash
python3 -m venv mistral_env
source mistral_env/bin/activate  # Auf Windows: mistral_env\Scripts\activate
```

### Schritt 3: Dependencies installieren
```bash
pip install -r requirements.txt
```

### Schritt 4: API-Key konfigurieren

**Option A: Sichere Einrichtung (empfohlen)** 🆕
```bash
./mistral auth setup
```
Der API-Key wird sicher im System-Keyring (macOS Keychain, GNOME Keyring, Windows Credential Manager) oder AES-256 verschlüsselt gespeichert.

**Option B: Umgebungsvariable (temporär)**
```bash
export MISTRAL_API_KEY='ihr-api-key-hier'
```

**Option C: .env-Datei (für Entwicklung)**
```bash
echo "MISTRAL_API_KEY=ihr-api-key-hier" > ~/.mistral-cli.env
```
Die Anwendung lädt automatisch `.env` aus dem aktuellen Verzeichnis oder `~/.mistral-cli.env`.

> ⚠️ **Sicherheitshinweis:** Vermeide das Speichern von API-Keys in `.bashrc`/`.zshrc` - diese Dateien werden oft versehentlich in Repositories committed.

### Schritt 5: Anwendung ausführbar machen
```bash
chmod +x mistral
```

### Optional: Global verfügbar machen
```bash
sudo ln -s $(pwd)/mistral /usr/local/bin/mistral
```

## Verwendung

### Chat-Modus (mit Tools)
```bash
./mistral chat
```

Beispiele im Chat:
```
You: Erstelle einen Ordner ~/projects/test
You: Suche nach "Python best practices" und zeige die ersten 3 Ergebnisse
You: Lade https://example.com/data.json herunter und parse die JSON-Daten
You: Analysiere das Bild ~/photo.jpg
You: Lade report.pdf via SFTP auf server.example.com hoch
You: clear                          # Konversation löschen
You: exit                           # Chat beenden
```

**Mit automatischer Bestätigung:**
```bash
./mistral chat -y
```

**Mit bestimmtem Modell:**
```bash
./mistral chat -m mistral-large-latest
```

**Mit Debug-Ausgaben:** 🆕
```bash
./mistral --debug chat
```

### Textvervollständigung
```bash
./mistral complete "Erkläre Quantencomputing in einfachen Worten"
```

### Bash-Befehle generieren
```bash
./mistral exec "Erstelle eine Python-Projektstruktur mit src, tests und docs"
```

**Ohne Bestätigung ausführen:**
```bash
./mistral exec -y "Zeige Systemauslastung"
```

### Verfügbare Modelle anzeigen
```bash
./mistral models
```

### TUI-Modus (Text User Interface)
```bash
./mistral tui
```

### API-Key-Verwaltung 🆕
```bash
# API-Key sicher einrichten (interaktiv)
./mistral auth setup

# Status der API-Key-Speicherung anzeigen
./mistral auth status

# Gespeicherten API-Key löschen
./mistral auth delete
```

## Konfiguration

### CLI-Optionen
```bash
./mistral --help
./mistral --version
./mistral --debug chat    # Debug-Modus
```

### Chat-Optionen
| Option | Beschreibung | Default |
|--------|--------------|---------|
| `-m, --model` | Modell auswählen | `mistral-small-latest` |
| `-t, --temperature` | Temperatur (0.0 - 1.0) | `0.7` |
| `--max-tokens` | Max. Tokens | `1024` |
| `-y, --yes` | Tools automatisch bestätigen | `False` |

### Exec-Optionen
| Option | Beschreibung | Default |
|--------|--------------|---------|
| `-m, --model` | Modell auswählen | `mistral-small-latest` |
| `-y, --yes` | Ohne Bestätigung ausführen | `False` |
| `-f, --force` | Bei Fehlern fortfahren | `False` |

### Umgebungsvariablen

| Variable | Beschreibung |
|----------|--------------|
| `MISTRAL_API_KEY` | Mistral AI API-Key (erforderlich) |
| `FTP_USER` | FTP-Benutzername (optional) |
| `FTP_PASS` | FTP-Passwort (optional) |
| `SFTP_USER` | SFTP-Benutzername (optional) 🆕 |
| `SFTP_PASS` | SFTP-Passwort (optional) 🆕 |
| `SFTP_KEY_PATH` | Pfad zum SSH Private Key (optional) 🆕 |

## Tool-Übersicht

| Tool | Beschreibung |
|------|--------------|
| `execute_bash_command` | Führt Bash-Befehle aus (mit Sicherheitsprüfung) |
| `read_file` | Liest Dateiinhalte |
| `write_file` | Schreibt/erstellt Dateien |
| `rename_file` | Benennt Dateien/Ordner um |
| `copy_file` | Kopiert Dateien/Ordner |
| `move_file` | Verschiebt Dateien/Ordner |
| `fetch_url` | Ruft URL-Inhalte ab |
| `download_file` | Lädt Dateien herunter |
| `search_web` | Sucht im Internet (DuckDuckGo) |
| `upload_ftp` | Lädt Dateien via FTP hoch (unverschlüsselt) |
| `upload_sftp` | Lädt Dateien via SFTP hoch (verschlüsselt) 🆕 |
| `parse_json` | Parst JSON-Daten |
| `parse_csv` | Liest CSV-Dateien |
| `get_image_info` | Analysiert Bilder |

## Projektstruktur

```
mistral-cli/
├── mistral                     # Einstiegspunkt (Shell-Script)
├── mistral-cli.py              # Hauptanwendung mit Subcommands
├── mistral_chat.py             # Chat-Modus mit Tool-Support
├── mistral_tui.py              # Text User Interface
│
├── mistralcli/                 # 🆕 Modulares Python-Package (25 Module)
│   ├── core/                   # Kern-Funktionalität
│   │   ├── config.py           # Konstanten, Enums, Patterns
│   │   ├── logging_config.py   # Logger Setup
│   │   └── client.py           # Mistral Client Management
│   ├── security/               # Sicherheits-Validierung
│   │   ├── command_validator.py # Bash Command Security
│   │   ├── path_validator.py   # Path Traversal Schutz
│   │   ├── url_validator.py    # SSRF Protection
│   │   └── sanitizers.py       # Sanitization
│   ├── auth/                   # Authentifizierung
│   │   └── api_key_manager.py  # Keyring & AES-256
│   ├── utils/                  # Utilities
│   │   ├── token_manager.py    # Token Handling
│   │   ├── formatting.py       # Output Formatting
│   │   └── helpers.py          # Misc Helpers
│   └── tools/                  # 14 Tools
│       ├── definitions.py      # Tool Schemas
│       ├── executor.py         # Tool Dispatcher
│       ├── system.py           # Bash Commands
│       ├── filesystem.py       # File Operations
│       ├── network.py          # Web & Downloads
│       ├── transfer.py         # FTP/SFTP
│       ├── data.py             # JSON/CSV
│       └── image.py            # Image Analysis
│
├── tests/                      # 🧪 Test-Suite (424 Tests)
│   ├── conftest.py             # Pytest Fixtures
│   ├── security/               # Security-Tests (236 Tests)
│   └── tools/                  # Tools-Tests
│
├── requirements.txt            # Python-Abhängigkeiten
├── requirements-test.txt       # Test-Dependencies
├── setup.py                    # Package-Installation
├── pytest.ini                  # Pytest-Konfiguration
├── run_tests.sh                # Test-Runner
│
├── README.md                   # Hauptdokumentation
├── TESTING.md                  # Test-Dokumentation
├── QUICKSTART.md               # Schnellstart-Anleitung
├── EXAMPLES.md                 # Ausführliche Beispiele
├── MIGRATION_COMPLETE.md       # Migration v1.5.2
├── CHANGELOG.md                # Versionshistorie
├── CONTRIBUTING.md             # Beitragsrichtlinien
└── LICENSE                     # MIT-Lizenz
```

## Logging 🆕

Alle Aktionen werden automatisch protokolliert:

```bash
# Log-Datei anzeigen
cat ~/.mistral-cli.log

# Live-Log verfolgen
tail -f ~/.mistral-cli.log
```

Log-Einträge enthalten:
- Zeitstempel
- Log-Level (DEBUG, INFO, WARNING, ERROR)
- Modul und Funktion
- Nachricht

## Pfeiltasten & Command History

Die CLI unterstützt Pfeiltasten (↑↓) für die Befehlshistorie und (←→) für Cursor-Navigation.

| Plattform | Status | Aktion |
|-----------|--------|--------|
| **Linux** | ✅ Funktioniert | Keine Aktion nötig |
| **macOS** | ⚠️ libedit | `pip install gnureadline` für volle Unterstützung |
| **Windows** | ⚠️ Optional | `pip install pyreadline3` |

### macOS Fix
```bash
pip install gnureadline
```

Nach der Installation zeigt der Chat:
```
(Use ↑↓ arrow keys for command history) [gnu]
```

### Nützliche Chat-Befehle
| Befehl | Beschreibung |
|--------|--------------|
| `↑` / `↓` | Vorherige/Nächste Eingabe |
| `history` | Zeigt letzte 10 Eingaben |
| `clear` | Löscht Konversation |
| `exit` | Beendet Chat |

## Sicherheit

- **Sichere API-Key-Speicherung**: System-Keyring oder AES-256 Verschlüsselung 🆕
- **Bestätigungspflicht**: Alle destruktiven Operationen erfordern Bestätigung (außer mit `-y` Flag)
- **Gefährliche Befehle**: Automatische Blockierung von `rm -rf /`, Fork-Bombs, etc.
- **SFTP statt FTP**: Verschlüsselte Dateiübertragung für sensible Daten
- **Timeouts**: Web-Requests haben automatische Timeouts (30 Sekunden)
- **Error-Handling**: Robuste Fehlerbehandlung für alle Operationen
- **Logging**: Alle Aktionen werden protokolliert (ohne sensible Daten)

### Blockierte Befehle 🆕

Folgende Befehlsmuster werden automatisch blockiert:
- `rm -rf /` und Varianten
- Fork-Bombs (`:(){:|:&};:`)
- Remote Code Execution (`curl | bash`)
- Destruktive `dd`-Befehle
- Pipe-zu-Shell von externen Quellen (`curl | sh`)

## Fehlerbehebung

### Problem: "MISTRAL_API_KEY nicht gesetzt"
**Lösung**: API-Key konfigurieren (siehe Installation Schritt 4)

### Problem: "ModuleNotFoundError"
**Lösung**: Virtuelle Umgebung aktivieren und Dependencies installieren
```bash
source mistral_env/bin/activate
pip install -r requirements.txt
```

### Problem: Bildanalyse zeigt nur Dateigröße
**Lösung**: Pillow installieren für vollständige Bildanalyse
```bash
pip install Pillow
```

### Problem: Debug-Informationen benötigt
**Lösung**: Debug-Modus aktivieren und Log prüfen
```bash
./mistral --debug chat
cat ~/.mistral-cli.log
```

## Optionale Abhängigkeiten

```bash
# Sichere API-Key-Speicherung (empfohlen) 🆕
pip install keyring
```
```bash
# AES-Verschlüsselung für API-Key (Fallback)
pip install cryptography
```
```bash
# SFTP-Support (verschlüsselte Dateiübertragung)
pip install paramiko
```
```bash
# Erweiterte Bildverarbeitung
pip install Pillow
```
```bash
# Pfeiltasten-Support macOS
pip install gnureadline
```
```bash
# Pfeiltasten-Support Windows
pip install pyreadline3
```
```bash
# Entwicklung & Testing 🆕
pip install -r requirements-test.txt
```

## Development & Testing 🧪

### Test-Suite ausführen

Das Projekt verfügt über eine umfassende Test-Suite mit **424 Tests** und **100% Erfolgsquote**:

```bash
# Alle Tests ausführen
./run_tests.sh

# Nur Security-Tests (236 Tests)
./run_tests.sh security
pytest -m security

# Nur Unit-Tests (424 Tests)
./run_tests.sh unit
pytest -m unit

# Mit Coverage-Report
./run_tests.sh coverage

# Schnelle Tests ohne Coverage
./run_tests.sh quick
```

### Test-Ergebnisse

```
✅ 424/424 Tests bestehen (100%)
📈 40% Code Coverage
🔒 Security-Module: 90%+ Coverage
⏱️  ~3 Sekunden Laufzeit
```

### Coverage-Report ansehen

```bash
# HTML-Report öffnen
firefox htmlcov/index.html

# Terminal-Report
pytest --cov=mistralcli --cov-report=term
```

### Weitere Informationen

- **Test-Dokumentation**: `TESTING.md`
- **Test-Structure**: `tests/README.md`
- **Migration-Details**: `MIGRATION_COMPLETE.md`

## Beitragen

Contributions sind willkommen! Bitte:

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/amazing-feature`)
3. Committe deine Änderungen (`git commit -m 'Add amazing feature'`)
4. Push zum Branch (`git push origin feature/amazing-feature`)
5. Öffne einen Pull Request

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Details.

## Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei für Details.

## Links

- **Repository**: [github.com/TripleCore-ACS/mistral-cli](https://github.com/TripleCore-ACS/mistral-cli)
- **Issues**: [GitHub Issues](https://github.com/TripleCore-ACS/mistral-cli/issues)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Mistral AI**: [docs.mistral.ai](https://docs.mistral.ai)

---

Made with ❤️ in Hamburg using [Mistral AI](https://mistral.ai)
