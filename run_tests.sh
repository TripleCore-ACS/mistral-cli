#!/bin/bash
# Test Runner für Mistral CLI
# Version: 1.5.2

set -e  # Exit bei Fehler

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       MISTRAL CLI - TEST SUITE RUNNER                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Prüfe ob pytest installiert ist
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest ist nicht installiert!${NC}"
    echo -e "${YELLOW}Installiere mit: pip install -r requirements-test.txt${NC}"
    exit 1
fi

# Prüfe ob mistralcli-Package installiert ist
if ! python -c "import mistralcli" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  mistralcli-Package nicht gefunden${NC}"
    echo -e "${YELLOW}Installiere mit: pip install -e .${NC}"
    echo ""
fi

# Parse Command-Line Arguments
MODE=${1:-"all"}
VERBOSE=${2:-""}

# Zeige Hilfe
if [ "$MODE" = "--help" ] || [ "$MODE" = "-h" ]; then
    echo "Usage: ./run_tests.sh [MODE] [VERBOSE]"
    echo ""
    echo "Modes:"
    echo "  all           - Alle Tests ausführen (default)"
    echo "  security      - Nur Security-Tests"
    echo "  tools         - Nur Tools-Tests"
    echo "  core          - Nur Core-Tests"
    echo "  unit          - Nur Unit-Tests (schnell)"
    echo "  coverage      - Mit Coverage-Report"
    echo "  quick         - Schnelle Tests ohne Coverage"
    echo ""
    echo "Verbose:"
    echo "  -v            - Verbose-Modus"
    echo "  -vv           - Sehr verbose"
    echo ""
    echo "Beispiele:"
    echo "  ./run_tests.sh all -v"
    echo "  ./run_tests.sh security"
    echo "  ./run_tests.sh coverage"
    exit 0
fi

echo -e "${GREEN}📋 Test-Modus: ${MODE}${NC}"
echo ""

# Führe Tests basierend auf Modus aus
case $MODE in
    "all")
        echo -e "${BLUE}🧪 Führe alle Tests aus...${NC}"
        pytest tests/ $VERBOSE --cov=mistralcli --cov-report=term-missing --cov-report=html
        ;;

    "security")
        echo -e "${BLUE}🔒 Führe Security-Tests aus...${NC}"
        pytest tests/security/ $VERBOSE -m security
        ;;

    "tools")
        echo -e "${BLUE}🔧 Führe Tools-Tests aus...${NC}"
        pytest tests/tools/ $VERBOSE
        ;;

    "core")
        echo -e "${BLUE}⚙️  Führe Core-Tests aus...${NC}"
        pytest tests/core/ $VERBOSE
        ;;

    "unit")
        echo -e "${BLUE}⚡ Führe Unit-Tests aus (schnell)...${NC}"
        pytest tests/ $VERBOSE -m unit --tb=short
        ;;

    "coverage")
        echo -e "${BLUE}📊 Führe Tests mit vollständigem Coverage-Report aus...${NC}"
        pytest tests/ $VERBOSE \
            --cov=mistralcli \
            --cov-report=html \
            --cov-report=term-missing \
            --cov-report=xml \
            --cov-branch

        echo ""
        echo -e "${GREEN}✅ Coverage-Report generiert:${NC}"
        echo -e "   HTML: ${BLUE}htmlcov/index.html${NC}"
        echo -e "   XML:  ${BLUE}coverage.xml${NC}"
        ;;

    "quick")
        echo -e "${BLUE}⚡ Schnelle Tests ohne Coverage...${NC}"
        pytest tests/ $VERBOSE --tb=short -x
        ;;

    *)
        echo -e "${RED}❌ Unbekannter Modus: ${MODE}${NC}"
        echo "Verwende './run_tests.sh --help' für Hilfe"
        exit 1
        ;;
esac

# Zeige Test-Ergebnis
EXIT_CODE=$?

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ ALLE TESTS ERFOLGREICH!${NC}"

    # Zeige Coverage-Zusammenfassung wenn verfügbar
    if [ "$MODE" = "all" ] || [ "$MODE" = "coverage" ]; then
        echo ""
        echo -e "${BLUE}📊 Coverage-Report:${NC}"
        echo -e "   Öffne ${YELLOW}htmlcov/index.html${NC} im Browser"
    fi
else
    echo -e "${RED}❌ EINIGE TESTS FEHLGESCHLAGEN!${NC}"
    echo -e "${YELLOW}Verwende -v oder -vv für Details${NC}"
fi

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

exit $EXIT_CODE
