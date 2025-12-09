# Mistral CLI - Praktische Beispiele

## Grundlegende Verwendung

### 1. Einfacher Chat
```bash
./mistral chat

Sie: Was ist Quantencomputing?
Mistral: [Erklärt Quantencomputing...]
```

### 2. Schnelle Textvervollständigung
```bash
./mistral complete "Schreibe einen Python-Oneliner der eine Liste von 1-100 generiert"
```

## Dateisystem-Operationen

### Projektstruktur erstellen
```bash
./mistral chat

Sie: Erstelle eine Python-Projektstruktur mit:
     - src/ Ordner für Quellcode
     - tests/ Ordner für Tests
     - docs/ Ordner für Dokumentation
     - README.md Datei
     - requirements.txt Datei
     - .gitignore für Python
```

### Dateien umbenennen und organisieren
```bash
Sie: Benenne alle .txt Dateien im aktuellen Ordner um zu .md Dateien
```

### Backup erstellen
```bash
Sie: Kopiere den Ordner ~/projects/wichtig nach ~/backups/wichtig-backup-$(date +%Y%m%d)
```

## Web-Recherche

### Aktuelle Informationen suchen
```bash
./mistral chat

Sie: Suche nach "Python 3.12 neue Features" und fasse die Top 3 Ergebnisse zusammen
```

### Website analysieren
```bash
Sie: Rufe https://python.org ab und liste mir alle Hauptnavigationspunkte auf
```

### Download und Analyse
```bash
Sie: Lade https://example.com/data.json herunter, parse die JSON-Daten
     und erstelle eine Zusammenfassung als data-summary.txt
```

## Datenverarbeitung

### CSV-Analyse
```bash
Sie: Lies die CSV-Datei sales.csv, berechne den Gesamtumsatz und
     erstelle eine Zusammenfassung
```

### JSON transformieren
```bash
Sie: Lade die API-Daten von https://api.example.com/users,
     extrahiere alle E-Mail-Adressen und speichere sie als emails.txt
```

### Daten kombinieren
```bash
Sie: Lies data1.csv und data2.csv, kombiniere sie basierend auf der ID-Spalte
     und speichere das Ergebnis als combined.csv
```

## Automatisierung

### Tägliches Backup-Script erstellen
```bash
./mistral exec "Erstelle ein Bash-Script backup.sh das:
- Alle Dateien aus ~/documents sichert
- Ein Archiv mit Datum erstellt
- Das Archiv nach ~/backups verschiebt"
```

### Git-Workflow automatisieren
```bash
Sie: Erstelle ein Script das:
     1. Alle Änderungen zu Git hinzufügt
     2. Mit aussagekräftiger Message committed
     3. Zum main-Branch pushed
```

### System-Monitoring
```bash
./mistral chat -y

Sie: Erstelle einen Report über:
     - Festplattenspeicher
     - RAM-Auslastung
     - CPU-Load
     - Laufende Prozesse
     Speichere den Report als system-status.txt
```

## Entwickler-Workflows

### Dokumentation erstellen
```bash
Sie: Lies alle Python-Dateien im src/ Ordner, analysiere die Funktionen
     und erstelle eine API-Dokumentation als docs/api.md
```

### Code-Analyse
```bash
Sie: Analysiere die Datei app.py und erstelle eine Liste aller:
     - Importierten Module
     - Definierten Funktionen
     - Verwendeten Klassen
```

### Requirements generieren
```bash
Sie: Scanne alle Python-Dateien im Projekt und erstelle eine
     requirements.txt mit allen verwendeten Packages
```

## Content-Erstellung

### Blog-Post-Recherche
```bash
Sie: Recherchiere zum Thema "Machine Learning Best Practices 2024",
     fasse die wichtigsten Punkte zusammen und erstelle einen
     Entwurf für einen Blog-Post als blog-draft.md
```

### README generieren
```bash
Sie: Analysiere die Python-Dateien in diesem Projekt und erstelle
     eine umfassende README.md mit Installation, Features und Beispielen
```

## Erweiterte Beispiele

### Multi-Step Workflow
```bash
./mistral chat

Sie: Führe folgende Schritte aus:
     1. Suche nach "Python asyncio tutorial"
     2. Öffne die Top 3 Webseiten
     3. Extrahiere Code-Beispiele
     4. Erstelle ein kombiniertes Tutorial als asyncio-guide.md
     5. Erstelle ein funktionierendes Beispiel-Script
```

### Daten-Pipeline
```bash
Sie:
1. Lade Daten von https://api.example.com/data
2. Parse das JSON
3. Filtere nach Einträgen mit status="active"
4. Konvertiere zu CSV
5. Erstelle Visualisierungen in einem Markdown-Report
6. Sende den Report per FTP auf den Server
```

### Projekt-Setup komplett
```bash
Sie: Erstelle ein komplettes Python-Projekt "myapp" mit:
     - Ordnerstruktur (src, tests, docs)
     - Virtual Environment
     - requirements.txt
     - setup.py
     - README.md
     - .gitignore
     - Git-Repository initialisiert
     - Erste Commit gemacht
```

## Tipps & Tricks

### Automatic Mode für Scripts
Für automatisierte Workflows ohne Bestätigung:
```bash
./mistral chat -y < commands.txt
```

### Bestimmtes Modell verwenden
```bash
./mistral chat -m mistral-large-latest
```

### Höhere Kreativität
```bash
./mistral chat -t 0.9 --max-tokens 2048
```

### Batch-Processing
```bash
for file in *.txt; do
    ./mistral complete "Fasse diese Datei zusammen: $(cat $file)" > "${file%.txt}_summary.txt"
done
```

## Fehlersuche

### Debug-Modus
```bash
export MISTRAL_DEBUG=1
./mistral chat
```

### Verbose Output
```bash
./mistral exec -f "komplexer Befehl"  # Force weiterlaufen bei Fehlern
```

---

Haben Sie weitere coole Beispiele? Teilen Sie sie via Pull Request!
