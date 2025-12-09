# Mistral CLI

Eine leistungsstarke Kommandozeilenanwendung für Mistral AI mit erweiterten Tool-Funktionen.

## Features

### 🚀 Hauptfunktionen
- **Interaktiver Chat** mit Function Calling
- **Bash-Befehlsgenerierung und -ausführung**
- **Textvervollständigung**
- **Modellübersicht**

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

## Installation

### Voraussetzungen
- Python 3.8 oder höher
- Mistral AI API-Key ([hier erhalten](https://console.mistral.ai))

### Schritt 1: Repository klonen
```bash
git clone https://github.com/IHR-USERNAME/mistral-cli.git
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
```bash
export MISTRAL_API_KEY='ihr-api-key-hier'
```

Für dauerhafte Konfiguration in `~/.bashrc` oder `~/.zshrc`:
```bash
echo 'export MISTRAL_API_KEY="ihr-api-key-hier"' >> ~/.bashrc
source ~/.bashrc
```

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

Beispiele:
```
Sie: Erstelle einen Ordner ~/projects/test
Sie: Suche nach "Python best practices" und zeige die ersten 3 Ergebnisse
Sie: Lade https://example.com/data.json herunter und parse die JSON-Daten
Sie: Analysiere das Bild ~/photo.jpg
```

**Mit automatischer Bestätigung:**
```bash
./mistral chat -y
```

**Mit bestimmtem Modell:**
```bash
./mistral chat -m mistral-large-latest
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

## Erweiterte Konfiguration

### Chat-Optionen
```bash
./mistral chat --help
```

Optionen:
- `-m, --model` - Modell auswählen (default: mistral-small-latest)
- `-t, --temperature` - Temperatur (0.0 - 1.0, default: 0.7)
- `--max-tokens` - Max. Tokens (default: 1024)
- `-y, --yes` - Tools automatisch bestätigen

### Exec-Optionen
```bash
./mistral exec --help
```

Optionen:
- `-m, --model` - Modell auswählen
- `-y, --yes` - Befehle ohne Bestätigung ausführen
- `-f, --force` - Bei Fehlern fortfahren

## Tool-Übersicht

| Tool | Beschreibung |
|------|--------------|
| `execute_bash_command` | Führt Bash-Befehle aus |
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

## Beispiel-Workflows

### Web-Recherche mit Dateierstellung
```bash
./mistral chat

Sie: Suche nach "Mistral AI API documentation", öffne die erste Seite,
     fasse den Inhalt zusammen und speichere die Zusammenfassung als ~/mistral-docs.md
```

### Datenverarbeitung
```bash
Sie: Lade die JSON-Daten von https://api.example.com/data herunter,
     parse sie und erstelle eine CSV-Datei mit den wichtigsten Informationen
```

### Projektautomatisierung
```bash
Sie: Erstelle eine neue Python-Projektstruktur, initialisiere ein Git-Repository
     und erstelle eine .gitignore Datei für Python
```

## Optionale Abhängigkeiten

Für erweiterte Bildverarbeitung:
```bash
pip install Pillow
```

## Sicherheit

- **Bestätigungspflicht**: Alle destruktiven Operationen erfordern Bestätigung (außer mit `-y` Flag)
- **Timeouts**: Web-Requests haben automatische Timeouts
- **Error-Handling**: Robuste Fehlerbehandlung für alle Operationen
- **API-Key**: Wird nur aus Umgebungsvariablen gelesen

## Fehlerbehebung

### Problem: "MISTRAL_API_KEY nicht gesetzt"
**Lösung**: API-Key in Umgebungsvariable exportieren
```bash
export MISTRAL_API_KEY='ihr-key'
```

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

## Beitragen

Contributions sind willkommen! Bitte:
1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/amazing-feature`)
3. Committe deine Änderungen (`git commit -m 'Add amazing feature'`)
4. Push zum Branch (`git push origin feature/amazing-feature`)
5. Öffne einen Pull Request

## Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei für Details

## Support

- **Issues**: [GitHub Issues](https://github.com/IHR-USERNAME/mistral-cli/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/IHR-USERNAME/mistral-cli/discussions)
- **Mistral AI**: [Offizielle Dokumentation](https://docs.mistral.ai)

## Changelog

### v1.0.0 (2024)
- Initial Release
- Interaktiver Chat mit Function Calling
- 13 integrierte Tools
- Web-Recherche und Downloads
- Dateioperationen und Datenverarbeitung
- Bildanalyse

---

Made with ❤️ using [Mistral AI](https://mistral.ai)
