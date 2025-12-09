# Mistral CLI - Schnellstart

Schneller Einstieg in 5 Minuten!

## 1. Installation (2 Minuten)

```bash
# Repository klonen
git clone https://github.com/triplecore-acs/mistral-cli.git
cd mistral-cli

# Virtuelle Umgebung erstellen
python3 -m venv mistral_env
source mistral_env/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Ausführbar machen
chmod +x mistral
```

## 2. API-Key konfigurieren (1 Minute)

1. Holen Sie sich einen API-Key: https://console.mistral.ai
2. Setzen Sie die Umgebungsvariable:

```bash
export MISTRAL_API_KEY='ihr-api-key-hier'
```

**Dauerhaft speichern:**
```bash
echo 'export MISTRAL_API_KEY="ihr-api-key"' >> ~/.bashrc
source ~/.bashrc
```

## 3. Erste Befehle (2 Minuten)

### Test: Modelle anzeigen
```bash
./mistral models
```

### Einfacher Chat
```bash
./mistral chat
```

Probieren Sie:
```
Sie: Was ist Mistral AI?
Sie: Erstelle einen Ordner ~/test-mistral
Sie: Suche nach "Python tutorials"
Sie: exit
```

### Schnelle Completion
```bash
./mistral complete "Erkläre Machine Learning in einem Satz"
```

### Befehle generieren
```bash
./mistral exec "Zeige alle Python-Dateien im aktuellen Verzeichnis"
```

## Nächste Schritte

- 📖 Vollständige Dokumentation: [README.md](README.md)
- 💡 Praktische Beispiele: [EXAMPLES.md](EXAMPLES.md)
- 🤝 Beitragen: [CONTRIBUTING.md](CONTRIBUTING.md)

## Häufige Probleme

**"MISTRAL_API_KEY nicht gesetzt"**
```bash
export MISTRAL_API_KEY='ihr-key'
```

**"ModuleNotFoundError"**
```bash
source mistral_env/bin/activate
pip install -r requirements.txt
```

**"Permission denied"**
```bash
chmod +x mistral
```

## Erweiterte Features aktivieren

**Bildverarbeitung:**
```bash
pip install Pillow
```

Dann im Chat:
```
Sie: Analysiere das Bild ~/photo.jpg
```

---

Viel Spaß mit Mistral CLI! 🚀
