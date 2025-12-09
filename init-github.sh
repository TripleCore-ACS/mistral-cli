#!/bin/bash
# GitHub Initialisierungs-Script für Mistral CLI

echo "=========================================="
echo "  Mistral CLI - GitHub Setup"
echo "=========================================="
echo ""

# Prüfe ob Git installiert ist
if ! command -v git &> /dev/null; then
    echo "❌ Git ist nicht installiert. Bitte installieren Sie Git zuerst:"
    echo "   sudo apt-get install git"
    exit 1
fi

echo "✓ Git gefunden"
echo ""

# Git konfigurieren (falls noch nicht geschehen)
if [ -z "$(git config --global user.name)" ]; then
    read -p "Git Benutzername: " git_name
    git config --global user.name "$git_name"
fi

if [ -z "$(git config --global user.email)" ]; then
    read -p "Git E-Mail: " git_email
    git config --global user.email "$git_email"
fi

echo "✓ Git konfiguriert"
echo ""

# Git Repository initialisieren (falls noch nicht geschehen)
if [ ! -d ".git" ]; then
    echo "Initialisiere Git Repository..."
    git init
    echo "✓ Repository initialisiert"
else
    echo "✓ Git Repository bereits vorhanden"
fi

echo ""

# Dateien hinzufügen
echo "Füge Dateien zu Git hinzu..."
git add README.md
git add LICENSE
git add requirements.txt
git add setup.py
git add mistral
git add mistral-cli.py
git add .gitignore
git add CONTRIBUTING.md
git add EXAMPLES.md
git add .github/

echo "✓ Dateien hinzugefügt"
echo ""

# Ersten Commit erstellen
echo "Erstelle ersten Commit..."
git commit -m "Initial commit: Mistral CLI v1.0.0

Features:
- Interaktiver Chat mit Function Calling
- 13 integrierte Tools
- Web-Recherche und Downloads
- Dateioperationen und Datenverarbeitung
- FTP-Upload
- JSON/CSV-Parsing
- Bildanalyse

🤖 Generated with Claude Code
"

echo "✓ Commit erstellt"
echo ""

# Anleitung für GitHub
echo "=========================================="
echo "  Nächste Schritte:"
echo "=========================================="
echo ""
echo "1. Erstellen Sie ein neues Repository auf GitHub:"
echo "   https://github.com/new"
echo ""
echo "2. Führen Sie folgende Befehle aus (ersetzen Sie USERNAME und REPO):"
echo ""
echo "   git remote add origin https://github.com/USERNAME/REPO.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Optional: Branches erstellen"
echo "   git checkout -b develop"
echo "   git push -u origin develop"
echo ""
echo "=========================================="
echo "  Fertig! Ihr Projekt ist bereit für GitHub"
echo "=========================================="
