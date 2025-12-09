# Mistral CLI - Projektstruktur

## Übersicht

```
mistral-cli/
├── .github/
│   └── workflows/
│       └── test.yml              # GitHub Actions CI
├── mistral-cli.py                # Hauptanwendung
├── mistral                       # Ausführbares Wrapper-Script
├── setup.py                      # Installation Script
├── requirements.txt              # Python Dependencies
├── .gitignore                    # Git Ignore Regeln
├── LICENSE                       # MIT Lizenz
├── README.md                     # Hauptdokumentation
├── QUICKSTART.md                 # Schnellstart-Anleitung
├── EXAMPLES.md                   # Praktische Beispiele
├── CONTRIBUTING.md               # Beitragsrichtlinien
├── PROJECT_STRUCTURE.md          # Diese Datei
├── init-github.sh                # GitHub Setup Script
└── mistral_env/                  # Virtuelle Umgebung (nicht im Git)
```

## Dateibeschreibungen

### Kerndateien

**mistral-cli.py**
- Hauptanwendung mit allen Features
- 13 Tools für verschiedene Aufgaben
- Function Calling Integration
- ~700+ Zeilen Python Code

**mistral**
- Bash Wrapper-Script
- Aktiviert automatisch die virtuelle Umgebung
- Startet die Python-Anwendung

### Konfiguration

**requirements.txt**
- Python Dependencies
- Mindestanforderungen für Betrieb
- Optionale Pakete auskommentiert

**setup.py**
- Installationsscript für pip
- Metadata für PyPI
- Entry Points Definition

**.gitignore**
- Ignoriert virtuelle Umgebungen
- Schützt API-Keys
- Standard Python Ignores

### Dokumentation

**README.md**
- Vollständige Projektdokumentation
- Installation und Verwendung
- Tool-Übersicht
- Fehlerbehebung

**QUICKSTART.md**
- 5-Minuten Schnellstart
- Minimale Schritte zum Loslegen
- Häufige Probleme

**EXAMPLES.md**
- Praktische Anwendungsbeispiele
- Workflows und Patterns
- Tipps und Tricks

**CONTRIBUTING.md**
- Richtlinien für Beiträge
- Development Setup
- Code Guidelines

**PROJECT_STRUCTURE.md**
- Projektstruktur (diese Datei)
- Dateibeschreibungen
- Entwicklungshinweise

### Automatisierung

**init-github.sh**
- Automatisches GitHub Setup
- Git-Konfiguration
- Erster Commit

**.github/workflows/test.yml**
- CI/CD für GitHub Actions
- Syntax-Tests
- Multi-Version Testing

### Lizenz

**LICENSE**
- MIT License
- Copyright 2024 Daniel Thun

## Entwicklung

### Neue Tools hinzufügen

1. Tool-Definition in `TOOLS` Array (mistral-cli.py)
2. Handler-Funktion in `execute_tool()`
3. Tests erstellen
4. Dokumentation aktualisieren

### Neue Befehle hinzufügen

1. Funktion erstellen (z.B. `cmd_newfeature()`)
2. Subparser in `main()` registrieren
3. Help-Text hinzufügen
4. README aktualisieren

## Deployment

### Lokale Installation
```bash
pip install -e .
```

### PyPI Veröffentlichung
```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

### GitHub Release
1. Tag erstellen: `git tag v1.0.0`
2. Push: `git push origin v1.0.0`
3. GitHub Release erstellen

## Größe und Komplexität

- **Zeilen Code**: ~700+ (mistral-cli.py)
- **Tools**: 13
- **Befehle**: 4 (chat, complete, exec, models)
- **Dependencies**: 1 (mistralai)
- **Optionale Deps**: 1 (Pillow)

## Wartung

### Regelmäßige Updates
- Mistral AI SDK aktualisieren
- Sicherheitsupdates
- Bug-Fixes

### Testing
```bash
python -m py_compile mistral-cli.py
./mistral --help
./mistral models
```

---

Letzte Aktualisierung: Dezember 2024
