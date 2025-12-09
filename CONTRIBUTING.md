# Contributing to Mistral CLI

Vielen Dank für Ihr Interesse, zu Mistral CLI beizutragen!

## Wie kann ich beitragen?

### Bug Reports
- Verwenden Sie die [GitHub Issues](https://github.com/IHR-USERNAME/mistral-cli/issues)
- Beschreiben Sie das Problem detailliert
- Fügen Sie Schritte zur Reproduktion hinzu
- Geben Sie Ihre System- und Python-Version an

### Feature Requests
- Öffnen Sie ein Issue mit dem Label "enhancement"
- Beschreiben Sie den Use Case
- Erklären Sie, warum das Feature nützlich wäre

### Pull Requests

#### Vor dem Coden
1. Öffnen Sie ein Issue, um das Feature/den Bugfix zu diskutieren
2. Forken Sie das Repository
3. Erstellen Sie einen Feature-Branch von `main`

#### Coding Guidelines
- Folgen Sie PEP 8 für Python Code
- Schreiben Sie aussagekräftige Commit-Messages
- Kommentieren Sie komplexen Code
- Testen Sie Ihre Änderungen gründlich

#### Pull Request Prozess
1. Aktualisieren Sie die README.md falls nötig
2. Aktualisieren Sie die requirements.txt falls neue Dependencies hinzukommen
3. Testen Sie alle Befehle (chat, complete, exec, models)
4. Erstellen Sie den Pull Request mit einer klaren Beschreibung

### Development Setup

```bash
# Repository forken und klonen
git clone https://github.com/IHR-USERNAME/mistral-cli.git
cd mistral-cli

# Virtuelle Umgebung erstellen
python3 -m venv mistral_env
source mistral_env/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# API-Key setzen
export MISTRAL_API_KEY='your-key'

# Testen
./mistral chat
```

### Code Review Prozess
- Mindestens ein Maintainer muss den PR reviewen
- Alle Diskussionspunkte müssen gelöst sein
- CI-Tests müssen bestehen (falls vorhanden)

### Verhaltenskodex
- Seien Sie respektvoll und inklusiv
- Konstruktive Kritik ist willkommen
- Fokus auf technische Argumente

## Fragen?
Öffnen Sie ein Issue oder starten Sie eine Diskussion!

Vielen Dank! 🎉
