# Mistral CLI - Text User Interface (TUI) Dokumentation

## Übersicht

Die TUI-Version von Mistral CLI bietet eine moderne, interaktive Benutzeroberfläche mit ASCII-Logo beim Start und Tab-basierter Navigation.

## Features

### 🎨 Visuelles Design
- **ASCII-Logo** beim Start mit Hinweis auf inoffizielle Version
- **Tab-basierte Navigation** zwischen verschiedenen Modi
- **Farbige Ausgaben** mit Syntax-Highlighting
- **Scrollbare Bereiche** für Chat und Logs
- **Responsive Layout** das sich an Terminal-Größe anpasst

### 📑 Verfügbare Tabs

#### 1. 💬 Chat
- Interaktiver Chat mit Mistral AI
- Tool-Unterstützung (alle 13 Tools verfügbar)
- Separater Tool-Log Bereich
- Chat-Historie mit Scroll-Funktion
- Enter-Taste zum Senden

**Tastenkombinationen:**
- `Enter` - Nachricht senden
- `Ctrl+C` - Chat-Historie löschen

#### 2. ⚡ Exec
- Bash-Befehlsgenerierung aus natürlicher Sprache
- Vorschau generierter Befehle
- Manuelle Bestätigung vor Ausführung
- Ausführungs-Log mit Exit-Codes

**Workflow:**
1. Aufgabe beschreiben
2. "Befehle generieren" klicken
3. Generierte Befehle prüfen
4. "Ausführen" oder "Abbrechen"

#### 3. 🔧 Models
- Liste aller verfügbaren Mistral-Modelle
- Modell-IDs und Beschreibungen
- Tabellarische Darstellung
- "Modelle laden" Button zum Aktualisieren

#### 4. 📝 Complete
- Einmalige Textvervollständigung
- Direktes Ergebnis ohne Chat-Context
- Ideal für schnelle Anfragen

#### 5. ⚙️ Settings
- **Modell auswählen** (z.B. mistral-small-latest, mistral-large-latest)
- **Temperatur einstellen** (0.0 - 1.0)
- **Max Tokens anpassen** (Antwortlänge)
- Einstellungen werden für aktuelle Sitzung gespeichert

## Installation

### Voraussetzungen
```bash
# Python 3.8+ und venv erforderlich
sudo apt install python3.12-venv  # Ubuntu/Debian
```

### Setup
```bash
# Repository klonen
git clone https://github.com/TripleCore-ACS/mistral-cli.git
cd mistral-cli

# Virtual Environment erstellen
python3 -m venv mistral_env
source mistral_env/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# API-Key setzen
export MISTRAL_API_KEY='ihr-mistral-api-key'
```

## Verwendung

### TUI starten
```bash
# Mit Virtual Environment
source mistral_env/bin/activate
./mistral tui

# Oder direkt mit Python
python3 mistral-cli.py tui
```

### Alternative: Klassische CLI
Die ursprünglichen CLI-Befehle sind weiterhin verfügbar:
```bash
./mistral chat      # Klassischer Chat-Modus
./mistral exec      # Bash-Befehle generieren
./mistral models    # Modelle auflisten
./mistral complete  # Textvervollständigung
```

## Tastenkombinationen

| Kombination | Aktion |
|-------------|--------|
| `Ctrl+Q` | TUI beenden |
| `Ctrl+C` | Chat-Historie löschen |
| `Tab` | Zwischen Tabs wechseln |
| `Enter` | Eingabe bestätigen |
| `Esc` | Aus Eingabefeld springen |

## Tool-Funktionen in der TUI

Alle 13 Tools sind in der TUI verfügbar und werden **automatisch bestätigt**:

### Dateisystem (6 Tools)
- `execute_bash_command` - Bash-Befehle ausführen
- `read_file` - Dateien lesen
- `write_file` - Dateien schreiben
- `rename_file` - Dateien umbenennen
- `copy_file` - Dateien kopieren
- `move_file` - Dateien verschieben

### Web & Netzwerk (4 Tools)
- `fetch_url` - URLs abrufen
- `download_file` - Dateien herunterladen
- `search_web` - Internet-Suche (DuckDuckGo)
- `upload_ftp` - FTP-Upload

### Datenverarbeitung (3 Tools)
- `parse_json` - JSON parsen
- `parse_csv` - CSV-Dateien lesen
- `get_image_info` - Bildanalyse

**Hinweis:** Im TUI-Modus werden Tool-Aufrufe automatisch ausgeführt (ohne manuelle Bestätigung), um den Workflow zu beschleunigen.

## Beispiele

### Chat mit Tool-Nutzung
```
Sie: Erstelle eine Datei "test.txt" mit dem Inhalt "Hallo Welt"

🔧 Tools werden ausgeführt:
▶️ write_file: {'file_path': 'test.txt', 'content': 'Hallo Welt'}
✅ Ergebnis: {"success": true, "message": "Datei erfolgreich geschrieben"}

🤖 Mistral: Ich habe die Datei test.txt mit dem Inhalt "Hallo Welt" erstellt.
```

### Exec-Modus
```
Aufgabe: Erstelle einen Ordner "projekt" und darin die Dateien main.py und README.md

✅ Generierte Befehle:
1. mkdir projekt
2. touch projekt/main.py
3. touch projekt/README.md

⚡ Führe Befehle aus...
[1/3] mkdir projekt
  ✅
[2/3] touch projekt/main.py
  ✅
[3/3] touch projekt/README.md
  ✅
```

## Fehlerbehandlung

### MISTRAL_API_KEY nicht gesetzt
```
FEHLER: MISTRAL_API_KEY nicht gesetzt!
Bitte setzen Sie: export MISTRAL_API_KEY='ihr-api-key'
```

**Lösung:**
```bash
export MISTRAL_API_KEY='your-key-here'
# Oder permanent in ~/.bashrc oder ~/.zshrc speichern
```

### Textual nicht installiert
```
Fehler: TUI-Module nicht verfügbar.
Bitte installieren Sie die Abhängigkeiten:
  pip install textual
```

**Lösung:**
```bash
pip install -r requirements.txt
```

## Technische Details

### Architektur
- **Framework:** Textual (Python TUI Framework)
- **App-Struktur:** Tab-basierte Navigation
- **Async-Support:** Asynchrone Event-Handler
- **CSS-Styling:** Textual CSS für Layout

### Code-Struktur
```
mistral-cli/
├── mistral-cli.py          # Hauptanwendung (CLI + TUI Entry)
├── mistral_tui.py          # TUI-Implementierung
├── requirements.txt        # Dependencies (inkl. textual)
└── TUI_README.md          # Diese Dokumentation
```

### Anpassung

#### CSS-Styling ändern
Die TUI verwendet Textual CSS. Zum Anpassen das `CSS`-Attribut in `mistral_tui.py` bearbeiten:

```python
CSS = """
Screen {
    background: $surface;
}
#logo {
    color: cyan;  # Ändern Sie die Logo-Farbe
}
"""
```

#### Logo anpassen
Das ASCII-Logo ist in `mistral_tui.py` als `LOGO`-Variable definiert:

```python
LOGO = r"""
Ihr eigenes Logo hier...
"""
```

## Vergleich: TUI vs CLI

| Feature | CLI | TUI |
|---------|-----|-----|
| Interface | Zeilen-basiert | Tab-basiert |
| Navigation | Befehle | Tabs + Buttons |
| Tool-Bestätigung | Manuell (y/n) | Automatisch |
| Chat-Historie | Keine Scroll | Scrollbar |
| Visuelles Feedback | Minimal | Farben + Emojis |
| Multitasking | Ein Modus | Alle Modi parallel |
| API-Key Check | Bei jedem Start | Einmalig |

## Bekannte Einschränkungen

1. **Terminal-Größe:** Mindestens 80x24 empfohlen
2. **API-Key:** Muss bei jedem Start neu gesetzt werden (nicht persistent)
3. **Tool-Logs:** Werden auf 200 Zeichen gekürzt
4. **Timeout:** Bash-Befehle haben 30s Timeout

## Troubleshooting

### Problem: TUI startet nicht
**Symptom:** ImportError oder ModuleNotFoundError

**Lösung:**
```bash
# Dependencies neu installieren
pip install --upgrade textual mistralai
```

### Problem: Logo wird nicht korrekt angezeigt
**Symptom:** Kaputte Zeichen oder Box-Drawing

**Lösung:**
- UTF-8 Terminal verwenden
- Schriftart mit Unicode-Unterstützung (z.B. Nerd Fonts)

### Problem: Farben fehlen
**Symptom:** Nur schwarz-weiß

**Lösung:**
```bash
# Terminal mit 256 Farben verwenden
export TERM=xterm-256color
```

## Weiterentwicklung

### Geplante Features
- [ ] Persistente Konfiguration (Config-Datei)
- [ ] Chat-Exporte (Markdown/JSON)
- [ ] Mehrere Chat-Sessions parallel
- [ ] Custom Themes
- [ ] Keyboard-Shortcuts konfigurierbar

### Beitragen
Pull Requests sind willkommen! Siehe [CONTRIBUTING.md](CONTRIBUTING.md)

## Lizenz

MIT License - Siehe [LICENSE](LICENSE)

## Autor

**Daniel Thun** (TripleCore-ACS)
- GitHub: [@TripleCore-ACS](https://github.com/TripleCore-ACS)
- Email: second.try.dt@mailbox.org

---

**⚠️ HINWEIS:** Dies ist eine inoffizielle Implementierung und steht in keiner Verbindung zu Mistral AI.
