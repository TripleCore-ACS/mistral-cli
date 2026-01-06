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

### 🛠️ 13 Integrierte Tools

#### Dateisystem
- Dateien lesen, schreiben, umbenennen
- Dateien/Ordner kopieren und verschieben
- Bash-Befehle ausführen

#### Web & Netzwerk
- Web-Suche (DuckDuckGo)
- URL-Inhalte abrufen
- Dateien herunterladen
- FTP-Upload

#### Datenverarbeitung
- JSON parsen und durchsuchen
- CSV-Dateien lesen und analysieren
- Bildanalyse (Format, Größe, Dimensionen)

### 🆕 Neu in v1.1.0

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

**Option A: Umgebungsvariable (temporär)**
```bash
export MISTRAL_API_KEY='ihr-api-key-hier'
```

**Option B: Shell-Konfiguration (dauerhaft)**
```bash
echo 'export MISTRAL_API_KEY="ihr-api-key-hier"' >> ~/.bashrc
source ~/.bashrc
```

**Option C: .env-Datei (empfohlen für Entwicklung)** 🆕
```bash
echo "MISTRAL_API_KEY=ihr-api-key-hier" > ~/.mistral-cli.env
```
Die Anwendung lädt automatisch `.env` aus dem aktuellen Verzeichnis oder `~/.mistral-cli.env`.

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
| `upload_ftp` | Lädt Dateien via FTP hoch |
| `parse_json` | Parst JSON-Daten |
| `parse_csv` | Liest CSV-Dateien |
| `get_image_info` | Analysiert Bilder |

## Projektstruktur

```
mistral-cli/
├── mistral                 # Einstiegspunkt (Shell-Script)
├── mistral-cli.py          # Hauptanwendung mit Subcommands
├── mistral_chat.py         # Chat-Modus mit Tool-Support
├── mistral_tools.py        # 13 Tool-Definitionen und Ausführung
├── mistral_utils.py        # 🆕 Zentrale Utilities (Client, Logging, etc.)
├── mistral_tui.py          # Text User Interface
├── requirements.txt        # Python-Abhängigkeiten
├── setup.py                # Package-Installation
├── CHANGELOG.md            # 🆕 Versionshistorie
├── README.md               # Diese Datei
├── QUICKSTART.md           # Schnellstart-Anleitung
├── EXAMPLES.md             # Ausführliche Beispiele
├── CONTRIBUTING.md         # Beitragsrichtlinien
└── LICENSE                 # MIT-Lizenz
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

## Sicherheit

- **Bestätigungspflicht**: Alle destruktiven Operationen erfordern Bestätigung (außer mit `-y` Flag)
- **Gefährliche Befehle**: Automatische Blockierung von `rm -rf /`, Fork-Bombs, etc. 🆕
- **Timeouts**: Web-Requests haben automatische Timeouts (30 Sekunden)
- **Error-Handling**: Robuste Fehlerbehandlung für alle Operationen
- **API-Key**: Wird nur aus Umgebungsvariablen oder `.env` gelesen
- **Logging**: Alle Aktionen werden protokolliert (ohne sensible Daten)

### Blockierte Befehle 🆕

Folgende Befehlsmuster werden automatisch blockiert:
- `rm -rf /` und Varianten
- Fork-Bombs (`:(){:|:&};:`)
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
# Erweiterte Bildverarbeitung
pip install Pillow

# Entwicklung
pip install pytest black flake8 mypy
```

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
