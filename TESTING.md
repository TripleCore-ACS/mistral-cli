# Testing Guide - Mistral CLI

## Schnellstart

```bash
# 1. Test-Dependencies installieren
pip install -r requirements-test.txt

# 2. Alle Tests ausführen
./run_tests.sh

# Oder direkt mit pytest
pytest
```

## Test-Struktur

```
tests/
├── conftest.py                 # Gemeinsame Fixtures
├── README.md                   # Ausführliche Test-Dokumentation
│
├── security/                   # ✅ 4 Test-Module (80+ Tests)
│   ├── test_command_validator.py
│   ├── test_path_validator.py
│   ├── test_url_validator.py
│   └── test_sanitizers.py
│
├── tools/                      # 🔄 2 Test-Module
│   ├── test_definitions.py
│   └── test_filesystem.py
│
└── [core, auth, utils]         # ⏳ Ausstehend
```

## Verfügbare Test-Modi

```bash
./run_tests.sh all          # Alle Tests mit Coverage
./run_tests.sh security     # Nur Security-Tests
./run_tests.sh tools        # Nur Tools-Tests
./run_tests.sh unit         # Nur schnelle Unit-Tests
./run_tests.sh coverage     # Vollständiger Coverage-Report
./run_tests.sh quick        # Schnell ohne Coverage
```

## Test-Status

|   Kategorie  | Tests |    Status     |
|--------------|-------|---------------|
| **Security** |   236 | ✅ Komplett   |
|   **Tools**  |    50 | ✅ Komplett   |
|   **Total**  |   424 | ✅ 100% Pass  |
|   **Core**   |     - | ⏳ Optional   |
|   **Auth**   |     - | ⏳ Optional   |
|   **Utils**  |     - | ⏳ Optional   |

## Coverage-Ziele

- **Gesamt:** 40% ✅ (erreicht)
- **Security-Module:** 90%+ ✅ (erreicht)
- **Tools-Module (getestet):** 78% ✅
- **Definitions:** 100% ✅
- **Sanitizers:** 100% ✅

**Zukünftige Erweiterungen:** Core, Auth, Utils Module

## Wichtige Features

### ✅ Bereits implementiert

- **Pytest-Konfiguration** - pytest.ini mit Markern
- **Gemeinsame Fixtures** - conftest.py mit Mocks
- **Security-Tests** - Umfassende Validierung
- **Tool-Definition Tests** - Schema-Validierung
- **Filesystem-Tests** - Alle 5 Tools getestet
- **Test-Runner Script** - ./run_tests.sh
- **Coverage-Reports** - HTML/XML/Terminal

### ⏳ Ausstehend

- Core-Module Tests (config, logging, client)
- Auth-Module Tests (api_key_manager)
- Utils-Module Tests (token, formatting, helpers)
- Verbleibende Tools-Tests (network, transfer, data, image)
- Integration-Tests
- CI/CD Pipeline

## Weitere Informationen

Siehe `tests/README.md` für:
- Detaillierte Anleitung
- Fixture-Dokumentation
- Best Practices
- Debugging-Tipps
- CI/CD Integration

## Schnell-Referenz

```bash
# Tests ausführen
pytest                                  # Alle Tests
pytest tests/security/                  # Nur Security
pytest -m security                      # Mit Marker
pytest -k "test_dangerous"             # Nach Namen filtern

# Mit Coverage
pytest --cov=mistralcli --cov-report=html

# Debugging
pytest -v -s                           # Verbose + print
pytest --pdb                           # Debugger bei Fehler
pytest -x                              # Stop bei erstem Fehler

# Performance
pytest --durations=10                  # Langsamste Tests
```

---

**Version:** 1.5.2
**Status:** Test-Infrastructure komplett, Tests teilweise implementiert
**Nächster Schritt:** Verbleibende Test-Module erstellen
