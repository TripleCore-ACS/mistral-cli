# Mistral CLI Test Suite

Umfassende Unit-Test-Suite für das mistralcli Python-Package.

## 📦 Struktur

```
tests/
├── conftest.py                      # Gemeinsame Fixtures & Setup
├── pytest.ini                       # Pytest-Konfiguration (im Root)
│
├── core/                            # Core-Module Tests
│   ├── test_config.py
│   ├── test_logging_config.py
│   └── test_client.py
│
├── security/                        # Security-Module Tests
│   ├── test_command_validator.py   # ✅ Vollständig (80+ Tests)
│   ├── test_path_validator.py      # ✅ Vollständig
│   ├── test_url_validator.py       # ✅ Vollständig (SSRF-Protection)
│   └── test_sanitizers.py          # ✅ Vollständig
│
├── auth/                            # Auth-Module Tests
│   └── test_api_key_manager.py
│
├── utils/                           # Utils-Module Tests
│   ├── test_token_manager.py
│   ├── test_formatting.py
│   └── test_helpers.py
│
└── tools/                           # Tools-Module Tests
    ├── test_definitions.py          # ✅ Vollständig (Tool-Schemas)
    ├── test_executor.py
    ├── test_system.py
    ├── test_filesystem.py           # ✅ Vollständig (5 Tools)
    ├── test_network.py
    ├── test_transfer.py
    ├── test_data.py
    └── test_image.py
```

## 🚀 Installation

### 1. Test-Dependencies installieren

```bash
pip install -r requirements-test.txt
```

Oder einzeln:
```bash
pip install pytest pytest-cov pytest-mock pytest-benchmark
```

### 2. Projekt im Development-Modus installieren

```bash
pip install -e .
```

## 🧪 Tests ausführen

### Alle Tests ausführen

```bash
pytest
```

### Mit Coverage-Report

```bash
pytest --cov=mistralcli --cov-report=html
```

Öffne dann `htmlcov/index.html` im Browser für detaillierten Coverage-Report.

### Nur spezifische Module testen

```bash
# Nur Security-Tests
pytest tests/security/

# Nur einen spezifischen Test
pytest tests/security/test_command_validator.py

# Nur eine Test-Klasse
pytest tests/security/test_command_validator.py::TestDangerousCommands

# Nur eine spezifische Test-Funktion
pytest tests/security/test_command_validator.py::TestDangerousCommands::test_dangerous_rm_commands
```

### Mit Markern filtern

```bash
# Nur Unit-Tests (schnell)
pytest -m unit

# Nur Security-Tests
pytest -m security

# Nur langsame Tests
pytest -m slow

# Nur Tests die kein Netzwerk brauchen
pytest -m "not network"
```

### Verbose-Modus

```bash
pytest -v                    # Zeigt jeden Test
pytest -vv                   # Noch ausführlicher
pytest -s                    # Zeigt print-Ausgaben
```

### Test-Output anpassen

```bash
pytest --tb=short            # Kurze Tracebacks
pytest --tb=line             # Eine Zeile pro Fehler
pytest -x                    # Stop bei erstem Fehler
pytest --maxfail=3           # Stop nach 3 Fehlern
```

## 📊 Coverage-Ziele

| Modul | Ziel | Status |
|-------|------|--------|
| **security/** | 95%+ | ✅ Tests komplett |
| **tools/** | 90%+ | 🔄 In Arbeit |
| **core/** | 85%+ | ⏳ Ausstehend |
| **auth/** | 85%+ | ⏳ Ausstehend |
| **utils/** | 85%+ | ⏳ Ausstehend |
| **Gesamt** | 90%+ | 🎯 Ziel |

## 🏷️ Verfügbare Test-Marker

Tests können mit Markern kategorisiert werden:

- `@pytest.mark.unit` - Schnelle Unit-Tests (Standard)
- `@pytest.mark.integration` - Integration-Tests (langsamer)
- `@pytest.mark.security` - Security-fokussierte Tests
- `@pytest.mark.slow` - Langsam laufende Tests
- `@pytest.mark.network` - Tests die Netzwerk benötigen
- `@pytest.mark.requires_api_key` - Tests die Mistral API-Key benötigen

## 🛠️ Fixtures

Gemeinsame Fixtures in `conftest.py`:

### Verzeichnis-Fixtures
- `temp_dir` - Temporäres Verzeichnis
- `test_data_dir` - Test-Daten Verzeichnis

### Mock-Fixtures
- `mock_mistral_client` - Gemockter Mistral Client
- `mock_tool_call` - Gemockter Tool-Call
- `mock_requests_get` / `mock_requests_post` - Gemockte HTTP-Requests
- `mock_subprocess_run` - Gemockter subprocess
- `mock_keyring` - Gemocktes Keyring

### Datei-Fixtures
- `sample_text_file` - Beispiel-Textdatei
- `sample_json_file` - Beispiel-JSON-Datei
- `sample_csv_file` - Beispiel-CSV-Datei
- `sample_image_file` - Beispiel-Bilddatei (benötigt PIL)

### Environment-Fixtures
- `clean_env` - Saubere Umgebung ohne API-Keys
- `mock_api_key` - Gesetzter Mock API-Key

### Security-Fixtures
- `dangerous_commands` - Liste gefährlicher Befehle
- `safe_commands` - Liste sicherer Befehle

## 📝 Test schreiben

### Beispiel: Neuen Test hinzufügen

```python
#!/usr/bin/env python3
"""
Unit Tests for mistralcli.module.feature

Description of what this module tests.
Version: 1.5.2
"""

import pytest
from mistralcli.module import feature_function


class TestFeature:
    """Tests for feature_function."""

    @pytest.mark.unit
    def test_basic_functionality(self):
        """Test basic functionality."""
        result = feature_function("input")
        assert result == "expected_output"

    @pytest.mark.unit
    @pytest.mark.security
    def test_security_validation(self):
        """Test security validation."""
        result = feature_function("malicious_input")
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.unit
    def test_with_fixture(self, temp_dir):
        """Test using a fixture."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        result = feature_function(str(test_file))
        assert result["success"] is True
```

### Parametrized Tests

```python
@pytest.mark.unit
@pytest.mark.parametrize("input,expected", [
    ("test1", "output1"),
    ("test2", "output2"),
    ("test3", "output3"),
])
def test_multiple_inputs(input, expected):
    """Test with multiple inputs."""
    result = feature_function(input)
    assert result == expected
```

## 🐛 Debugging Tests

### Fehlgeschlagenen Test debuggen

```bash
# Zeige lokale Variablen bei Fehler
pytest -l

# Interaktiver Debugger bei Fehler
pytest --pdb

# Nur fehlgeschlagene Tests erneut ausführen
pytest --lf

# Nur letzte fehlgeschlagene + neue Tests
pytest --ff
```

### Performance-Profiling

```bash
# Zeige langsamste Tests
pytest --durations=10

# Mit Benchmark
pytest --benchmark-only
```

## 📈 CI/CD Integration

### GitHub Actions Beispiel

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements-test.txt
      - run: pytest --cov=mistralcli --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## 🔧 Konfiguration

### pytest.ini

Die Pytest-Konfiguration befindet sich in `pytest.ini` im Root-Verzeichnis.

Wichtige Einstellungen:
- Test Discovery: `test_*.py`, `Test*` Klassen
- Coverage: Automatisch aktiviert mit HTML/XML Reports
- Marker: Definiert für Kategorisierung
- Logging: Konfigurierbar via CLI

### Coverage-Konfiguration

Coverage-Einstellungen in `pytest.ini`:
- Source: `mistralcli`
- Omit: Tests selbst, `__pycache__`
- Reports: HTML, Terminal, XML

## 📚 Best Practices

1. **Ein Test pro Assertion-Gruppe** - Tests sollten fokussiert sein
2. **Beschreibende Namen** - `test_feature_does_something_when_condition`
3. **AAA-Pattern** - Arrange, Act, Assert
4. **Fixtures verwenden** - Statt Wiederholung von Setup-Code
5. **Mocking für externe Abhängigkeiten** - Keine echten API-Calls
6. **Marker setzen** - Für einfaches Filtern
7. **Parametrize für ähnliche Tests** - Reduziert Duplikation

## 🎯 Status

**Aktueller Stand:**
- ✅ Test-Infrastruktur komplett
- ✅ Security-Tests komplett (80+ Tests)
- ✅ Tools-Definitions Tests komplett
- ✅ Filesystem-Tools Tests komplett
- 🔄 Weitere Tools-Tests in Arbeit
- ⏳ Core-Module Tests ausstehend
- ⏳ Auth-Module Tests ausstehend
- ⏳ Utils-Module Tests ausstehend

**Nächste Schritte:**
1. Verbleibende Tools-Tests erstellen
2. Core-Module Tests erstellen
3. Auth-Module Tests erstellen
4. Utils-Module Tests erstellen
5. Integration-Tests hinzufügen
6. CI/CD Pipeline einrichten

## 📧 Kontakt

Bei Fragen oder Problemen mit den Tests:
- Issue erstellen im GitHub-Repository
- Test-Dokumentation lesen in diesem README
