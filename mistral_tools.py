#!/usr/bin/env python3
"""
Mistral CLI - Tool Definitions and Execution
Contains all 14 tools for Mistral AI function calling

Tools:
1. execute_bash_command - Bash-Befehle ausführen
2. read_file - Dateien lesen
3. write_file - Dateien schreiben
4. fetch_url - URLs abrufen
5. download_file - Dateien herunterladen
6. search_web - Web-Suche (DuckDuckGo)
7. rename_file - Dateien umbenennen
8. copy_file - Dateien kopieren
9. move_file - Dateien verschieben
10. parse_json - JSON parsen
11. parse_csv - CSV parsen
12. upload_ftp - FTP Upload (unverschlüsselt)
13. get_image_info - Bild-Informationen
14. upload_sftp - SFTP Upload (verschlüsselt, SSH-basiert)
"""

import os
import subprocess
import json
import shutil
import csv
import html
import re
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import quote_plus
from ftplib import FTP
from typing import Dict, Any, List, Optional

# Lokale Imports
from mistral_utils import (
    logger,
    is_dangerous_command,
    get_command_risk_info,
    format_risk_warning,
    sanitize_path,
    validate_url,
    validate_path,
    check_file_operation_safety,
    RiskLevel,
    DEFAULT_TIMEOUT,
)


# ============================================================================
# Tool-Definitionen für Function Calling
# ============================================================================

TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "execute_bash_command",
            "description": "Führt einen Bash-Befehl auf dem System aus. Verwende dies, um Dateien zu erstellen, Ordner anzulegen, Programme auszuführen, etc. HINWEIS: Gefährliche Befehle werden automatisch blockiert.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Der auszuführende Bash-Befehl"
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Eine kurze Erklärung, was der Befehl macht"
                    }
                },
                "required": ["command", "explanation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Liest den Inhalt einer Datei. HINWEIS: Zugriff auf Systemdateien ist eingeschränkt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Der Pfad zur Datei"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Schreibt Inhalt in eine Datei (erstellt oder überschreibt). HINWEIS: Schreiben in Systemverzeichnisse ist nicht erlaubt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Der Pfad zur Datei"
                    },
                    "content": {
                        "type": "string",
                        "description": "Der Inhalt, der in die Datei geschrieben werden soll"
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Ruft den Inhalt einer URL ab (Webseiten, APIs, etc.). Gibt HTML, JSON oder Text zurück. HINWEIS: Lokale/private IP-Adressen sind blockiert.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Die vollständige URL (mit http:// oder https://)"
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP-Methode (GET oder POST)",
                        "enum": ["GET", "POST"]
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "download_file",
            "description": "Lädt eine Datei von einer URL herunter und speichert sie lokal. HINWEIS: Downloads von lokalen/privaten IPs sind blockiert.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Die URL der herunterzuladenden Datei"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Der lokale Pfad, wo die Datei gespeichert werden soll"
                    }
                },
                "required": ["url", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Sucht im Internet nach Informationen. Gibt eine Liste von Suchergebnissen zurück.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Die Suchanfrage"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Anzahl der gewünschten Ergebnisse (Standard: 5, Maximum: 10)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rename_file",
            "description": "Benennt eine Datei oder einen Ordner um",
            "parameters": {
                "type": "object",
                "properties": {
                    "old_path": {
                        "type": "string",
                        "description": "Der aktuelle Pfad der Datei/des Ordners"
                    },
                    "new_path": {
                        "type": "string",
                        "description": "Der neue Pfad/Name"
                    }
                },
                "required": ["old_path", "new_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "copy_file",
            "description": "Kopiert eine Datei oder einen Ordner",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Der Quellpfad"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Der Zielpfad"
                    }
                },
                "required": ["source", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_file",
            "description": "Verschiebt eine Datei oder einen Ordner",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Der Quellpfad"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Der Zielpfad"
                    }
                },
                "required": ["source", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "parse_json",
            "description": "Parst JSON-Daten und extrahiert Informationen",
            "parameters": {
                "type": "object",
                "properties": {
                    "json_string": {
                        "type": "string",
                        "description": "Der JSON-String zum Parsen"
                    },
                    "query": {
                        "type": "string",
                        "description": "Optionaler JSONPath oder Key zum Extrahieren spezifischer Daten"
                    }
                },
                "required": ["json_string"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "parse_csv",
            "description": "Liest und parst CSV-Daten",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Pfad zur CSV-Datei"
                    },
                    "delimiter": {
                        "type": "string",
                        "description": "Trennzeichen (Standard: Komma)",
                        "default": ","
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "upload_ftp",
            "description": "Lädt eine Datei via FTP auf einen Server hoch. HINWEIS: Verwende Umgebungsvariablen FTP_USER und FTP_PASS für Credentials.",
            "parameters": {
                "type": "object",
                "properties": {
                    "local_file": {
                        "type": "string",
                        "description": "Pfad zur lokalen Datei"
                    },
                    "host": {
                        "type": "string",
                        "description": "FTP-Server Host"
                    },
                    "username": {
                        "type": "string",
                        "description": "FTP-Benutzername (optional, nutzt FTP_USER Env-Variable)"
                    },
                    "password": {
                        "type": "string",
                        "description": "FTP-Passwort (optional, nutzt FTP_PASS Env-Variable)"
                    },
                    "remote_path": {
                        "type": "string",
                        "description": "Zielpfad auf dem FTP-Server"
                    }
                },
                "required": ["local_file", "host", "remote_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_image_info",
            "description": "Analysiert ein Bild und gibt Informationen zurück (Format, Größe, Dimensionen)",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Pfad zum Bild"
                    }
                },
                "required": ["image_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "upload_sftp",
            "description": "Lädt eine Datei sicher via SFTP (SSH File Transfer Protocol) auf einen Server hoch. Verschlüsselte Alternative zu FTP. HINWEIS: Verwende Umgebungsvariablen SFTP_USER, SFTP_PASS oder SFTP_KEY_PATH für Credentials.",
            "parameters": {
                "type": "object",
                "properties": {
                    "local_file": {
                        "type": "string",
                        "description": "Pfad zur lokalen Datei"
                    },
                    "host": {
                        "type": "string",
                        "description": "SFTP-Server Host"
                    },
                    "port": {
                        "type": "integer",
                        "description": "SFTP-Server Port (Standard: 22)",
                        "default": 22
                    },
                    "username": {
                        "type": "string",
                        "description": "SFTP-Benutzername (optional, nutzt SFTP_USER Env-Variable)"
                    },
                    "password": {
                        "type": "string",
                        "description": "SFTP-Passwort (optional, nutzt SFTP_PASS Env-Variable)"
                    },
                    "key_path": {
                        "type": "string",
                        "description": "Pfad zum SSH Private Key (optional, nutzt SFTP_KEY_PATH Env-Variable)"
                    },
                    "remote_path": {
                        "type": "string",
                        "description": "Zielpfad auf dem SFTP-Server"
                    }
                },
                "required": ["local_file", "host", "remote_path"]
            }
        }
    }
]


# ============================================================================
# Hilfsfunktionen
# ============================================================================

def _get_user_confirmation(prompt: str) -> bool:
    """
    Fragt den Benutzer nach Bestätigung.
    
    Args:
        prompt: Die Frage an den Benutzer
    
    Returns:
        True wenn bestätigt, False sonst
    """
    response = input(f"  {prompt} (y/n): ").strip().lower()
    return response in ['y', 'yes', 'j', 'ja']


def _create_result(
    success: bool,
    message: Optional[str] = None,
    error: Optional[str] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Erstellt ein standardisiertes Ergebnis-Dictionary.
    
    Args:
        success: Ob die Operation erfolgreich war
        message: Erfolgsmeldung
        error: Fehlermeldung
        **kwargs: Zusätzliche Felder
    
    Returns:
        Ergebnis-Dictionary
    """
    result: Dict[str, Any] = {"success": success}
    if message:
        result["message"] = message
    if error:
        result["error"] = error
    result.update(kwargs)
    return result


# ============================================================================
# Tool-Implementierungen
# ============================================================================

def _execute_bash_command(
    command: str,
    explanation: str,
    auto_confirm: bool
) -> Dict[str, Any]:
    """Führt einen Bash-Befehl aus mit erweiterter Sicherheitsprüfung."""
    logger.info(f"Bash-Befehl: {command}")
    logger.debug(f"Erklärung: {explanation}")

    print(f"\n[Tool Call] Bash-Befehl ausführen:")
    print(f"  Befehl: {command}")
    print(f"  Erklärung: {explanation}")

    # Erweiterte Sicherheitsprüfung
    risk_info = get_command_risk_info(command)
    
    if risk_info["is_blocked"]:
        logger.warning(f"Gefährlicher Befehl blockiert: {command}")
        print(format_risk_warning(risk_info))
        return _create_result(
            success=False,
            error=f"Befehl blockiert: {risk_info['description']}",
            risk_level=risk_info["risk_level"],
            category=risk_info["category"]
        )
    
    if risk_info["needs_confirmation"]:
        print(format_risk_warning(risk_info))
        if not _get_user_confirmation("Trotzdem ausführen?"):
            logger.info("Benutzer hat Ausführung eines Medium-Risk Befehls abgelehnt")
            return _create_result(success=False, output="Benutzer hat Ausführung abgelehnt")

    if not auto_confirm and risk_info["risk_level"] == "SAFE":
        if not _get_user_confirmation("Ausführen?"):
            logger.info("Benutzer hat Ausführung abgelehnt")
            return _create_result(success=False, output="Benutzer hat Ausführung abgelehnt")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=DEFAULT_TIMEOUT
        )

        output = result.stdout if result.stdout else result.stderr
        logger.info(f"Befehl ausgeführt, Exit-Code: {result.returncode}")
        
        return _create_result(
            success=result.returncode == 0,
            output=output,
            exit_code=result.returncode
        )
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout bei Befehl: {command}")
        return _create_result(success=False, output=f"Befehl hat Timeout überschritten ({DEFAULT_TIMEOUT}s)")
    except Exception as e:
        logger.error(f"Fehler bei Befehl: {e}")
        return _create_result(success=False, error=str(e))


def _read_file(file_path: str) -> Dict[str, Any]:
    """Liest den Inhalt einer Datei mit Pfad-Validierung."""
    logger.info(f"Datei lesen: {file_path}")
    print(f"\n[Tool Call] Datei lesen: {file_path}")

    # Pfad-Validierung
    is_safe, message = validate_path(file_path)
    if not is_safe:
        logger.warning(f"Pfad-Validierung fehlgeschlagen: {file_path} - {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    try:
        path = sanitize_path(file_path)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Datei gelesen: {len(content)} Zeichen")
        return _create_result(success=True, content=content)
    except FileNotFoundError:
        logger.error(f"Datei nicht gefunden: {file_path}")
        return _create_result(success=False, error=f"Datei nicht gefunden: {file_path}")
    except PermissionError:
        logger.error(f"Keine Berechtigung: {file_path}")
        return _create_result(success=False, error=f"Keine Berechtigung zum Lesen: {file_path}")
    except Exception as e:
        logger.error(f"Fehler beim Lesen: {e}")
        return _create_result(success=False, error=str(e))


def _write_file(
    file_path: str,
    content: str,
    auto_confirm: bool
) -> Dict[str, Any]:
    """Schreibt Inhalt in eine Datei mit Pfad-Validierung."""
    logger.info(f"Datei schreiben: {file_path}")
    
    print(f"\n[Tool Call] Datei schreiben: {file_path}")
    preview = content[:100] + "..." if len(content) > 100 else content
    print(f"  Inhalt: {preview}")

    # Pfad-Validierung
    is_safe, message = validate_path(file_path)
    if not is_safe:
        logger.warning(f"Pfad-Validierung fehlgeschlagen: {file_path} - {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    if not auto_confirm and not _get_user_confirmation("Schreiben?"):
        logger.info("Benutzer hat Schreiben abgelehnt")
        return _create_result(success=False, error="Benutzer hat Schreiben abgelehnt")

    try:
        path = sanitize_path(file_path)
        # Erstelle Verzeichnis falls nötig
        parent_dir = os.path.dirname(path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Datei geschrieben: {len(content)} Zeichen")
        return _create_result(success=True, message="Datei erfolgreich geschrieben")
    except PermissionError:
        logger.error(f"Keine Schreibberechtigung: {file_path}")
        return _create_result(success=False, error=f"Keine Schreibberechtigung: {file_path}")
    except Exception as e:
        logger.error(f"Fehler beim Schreiben: {e}")
        return _create_result(success=False, error=str(e))


def _fetch_url(url: str, method: str = "GET") -> Dict[str, Any]:
    """Ruft den Inhalt einer URL ab mit URL-Validierung."""
    logger.info(f"URL abrufen: {url} ({method})")
    
    print(f"\n[Tool Call] URL abrufen: {url}")
    print(f"  Methode: {method}")

    # URL-Validierung
    is_safe, message = validate_url(url)
    if not is_safe:
        logger.warning(f"URL-Validierung fehlgeschlagen: {url} - {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = Request(url, headers=headers, method=method)
        
        with urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
            content = response.read().decode('utf-8')
            content_type = response.headers.get('Content-Type', '')

            # Begrenze die Ausgabe auf 10000 Zeichen
            if len(content) > 10000:
                content = content[:10000] + "\n... (gekürzt)"

            logger.info(f"URL abgerufen: {len(content)} Zeichen, Status: {response.status}")
            return _create_result(
                success=True,
                content=content,
                content_type=content_type,
                status_code=response.status
            )
    except HTTPError as e:
        logger.error(f"HTTP Fehler: {e.code} {e.reason}")
        return _create_result(success=False, error=f"HTTP Fehler {e.code}: {e.reason}")
    except URLError as e:
        logger.error(f"URL Fehler: {e.reason}")
        return _create_result(success=False, error=f"URL Fehler: {str(e.reason)}")
    except Exception as e:
        logger.error(f"Fehler beim Abrufen: {e}")
        return _create_result(success=False, error=str(e))


def _download_file(
    url: str,
    destination: str,
    auto_confirm: bool
) -> Dict[str, Any]:
    """Lädt eine Datei herunter mit URL- und Pfad-Validierung."""
    logger.info(f"Download: {url} -> {destination}")
    
    print(f"\n[Tool Call] Datei herunterladen:")
    print(f"  Von: {url}")
    print(f"  Nach: {destination}")

    # URL-Validierung
    is_safe, message = validate_url(url)
    if not is_safe:
        logger.warning(f"URL-Validierung fehlgeschlagen: {url} - {message}")
        print(f"  ⚠️  URL: {message}")
        return _create_result(success=False, error=f"URL unsicher: {message}")

    # Pfad-Validierung
    is_safe, message = validate_path(destination)
    if not is_safe:
        logger.warning(f"Pfad-Validierung fehlgeschlagen: {destination} - {message}")
        print(f"  ⚠️  Pfad: {message}")
        return _create_result(success=False, error=f"Pfad unsicher: {message}")

    if not auto_confirm and not _get_user_confirmation("Herunterladen?"):
        logger.info("Benutzer hat Download abgelehnt")
        return _create_result(success=False, error="Benutzer hat Download abgelehnt")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        req = Request(url, headers=headers)

        with urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
            content = response.read()

            dest_path = sanitize_path(destination)
            # Erstelle Verzeichnis falls nötig
            parent_dir = os.path.dirname(dest_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            
            with open(dest_path, 'wb') as f:
                f.write(content)

            file_size = len(content)
            logger.info(f"Download erfolgreich: {file_size} Bytes")
            return _create_result(
                success=True,
                message=f"Datei erfolgreich heruntergeladen ({file_size} Bytes)",
                file_size=file_size,
                destination=dest_path
            )
    except HTTPError as e:
        logger.error(f"HTTP Fehler beim Download: {e.code}")
        return _create_result(success=False, error=f"HTTP Fehler {e.code}: {e.reason}")
    except URLError as e:
        logger.error(f"URL Fehler beim Download: {e.reason}")
        return _create_result(success=False, error=f"URL Fehler: {str(e.reason)}")
    except Exception as e:
        logger.error(f"Download-Fehler: {e}")
        return _create_result(success=False, error=str(e))


def _search_web(query: str, num_results: int = 5) -> Dict[str, Any]:
    """Sucht im Web mit DuckDuckGo."""
    # Begrenze Ergebnisse auf maximal 10
    num_results = min(num_results, 10)
    
    logger.info(f"Web-Suche: '{query}' (max {num_results} Ergebnisse)")
    
    print(f"\n[Tool Call] Web-Suche: '{query}'")
    print(f"  Anzahl Ergebnisse: {num_results}")

    # Einfache Query-Validierung
    if len(query) < 2:
        return _create_result(success=False, error="Suchanfrage zu kurz (min. 2 Zeichen)")
    
    if len(query) > 500:
        return _create_result(success=False, error="Suchanfrage zu lang (max. 500 Zeichen)")

    try:
        # Verwende DuckDuckGo HTML (keine API-Key erforderlich)
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        req = Request(search_url, headers=headers)

        with urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
            html_content = response.read().decode('utf-8')

        # Einfaches Parsing der Suchergebnisse (Regex-basiert)
        results: List[Dict[str, str]] = []

        # Finde Ergebnisse im HTML
        result_pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)</a>'
        snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]+)</a>'

        matches = re.findall(result_pattern, html_content)
        snippets = re.findall(snippet_pattern, html_content)

        for i, (url, title) in enumerate(matches[:num_results]):
            snippet = snippets[i] if i < len(snippets) else ""
            # Dekodiere HTML-Entities
            title = html.unescape(title)
            snippet = html.unescape(snippet)

            results.append({
                "title": title,
                "url": url,
                "snippet": snippet
            })

        if not results:
            logger.warning(f"Keine Suchergebnisse für: {query}")
            return _create_result(success=False, error="Keine Suchergebnisse gefunden")

        logger.info(f"Suche erfolgreich: {len(results)} Ergebnisse")
        return _create_result(
            success=True,
            query=query,
            results=results,
            num_results=len(results)
        )
    except Exception as e:
        logger.error(f"Suche fehlgeschlagen: {e}")
        return _create_result(success=False, error=f"Suche fehlgeschlagen: {str(e)}")


def _rename_file(
    old_path: str,
    new_path: str,
    auto_confirm: bool
) -> Dict[str, Any]:
    """Benennt eine Datei um mit Pfad-Validierung."""
    logger.info(f"Umbenennen: {old_path} -> {new_path}")
    
    print(f"\n[Tool Call] Datei umbenennen:")
    print(f"  Von: {old_path}")
    print(f"  Nach: {new_path}")

    # Pfad-Validierungen
    for path, label in [(old_path, "Quellpfad"), (new_path, "Zielpfad")]:
        is_safe, message = validate_path(path)
        if not is_safe:
            logger.warning(f"{label}-Validierung fehlgeschlagen: {path} - {message}")
            print(f"  ⚠️  {label}: {message}")
            return _create_result(success=False, error=f"{label} unsicher: {message}")

    if not auto_confirm and not _get_user_confirmation("Umbenennen?"):
        logger.info("Benutzer hat Umbenennen abgelehnt")
        return _create_result(success=False, error="Benutzer hat Umbenennen abgelehnt")

    try:
        old = sanitize_path(old_path)
        new = sanitize_path(new_path)
        os.rename(old, new)
        logger.info("Umbenennen erfolgreich")
        return _create_result(success=True, message=f"Erfolgreich umbenannt von {old} zu {new}")
    except FileNotFoundError:
        logger.error(f"Datei nicht gefunden: {old_path}")
        return _create_result(success=False, error=f"Datei nicht gefunden: {old_path}")
    except PermissionError:
        logger.error(f"Keine Berechtigung: {old_path}")
        return _create_result(success=False, error=f"Keine Berechtigung zum Umbenennen")
    except Exception as e:
        logger.error(f"Umbenennen fehlgeschlagen: {e}")
        return _create_result(success=False, error=str(e))


def _copy_file(
    source: str,
    destination: str,
    auto_confirm: bool
) -> Dict[str, Any]:
    """Kopiert eine Datei oder einen Ordner mit Sicherheitsprüfung."""
    logger.info(f"Kopieren: {source} -> {destination}")
    
    print(f"\n[Tool Call] Datei/Ordner kopieren:")
    print(f"  Von: {source}")
    print(f"  Nach: {destination}")

    # Sicherheitsprüfung für Dateioperationen
    is_safe, message = check_file_operation_safety("copy", source, destination)
    if not is_safe:
        logger.warning(f"Sicherheitsprüfung fehlgeschlagen: {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    if not auto_confirm and not _get_user_confirmation("Kopieren?"):
        logger.info("Benutzer hat Kopieren abgelehnt")
        return _create_result(success=False, error="Benutzer hat Kopieren abgelehnt")

    try:
        src = sanitize_path(source)
        dst = sanitize_path(destination)

        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            # Erstelle Zielverzeichnis falls nötig
            parent_dir = os.path.dirname(dst)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            shutil.copy2(src, dst)

        logger.info("Kopieren erfolgreich")
        return _create_result(success=True, message=f"Erfolgreich kopiert von {src} zu {dst}")
    except FileNotFoundError:
        logger.error(f"Datei nicht gefunden: {source}")
        return _create_result(success=False, error=f"Datei nicht gefunden: {source}")
    except PermissionError:
        logger.error(f"Keine Berechtigung zum Kopieren")
        return _create_result(success=False, error="Keine Berechtigung zum Kopieren")
    except Exception as e:
        logger.error(f"Kopieren fehlgeschlagen: {e}")
        return _create_result(success=False, error=str(e))


def _move_file(
    source: str,
    destination: str,
    auto_confirm: bool
) -> Dict[str, Any]:
    """Verschiebt eine Datei oder einen Ordner mit Sicherheitsprüfung."""
    logger.info(f"Verschieben: {source} -> {destination}")
    
    print(f"\n[Tool Call] Datei/Ordner verschieben:")
    print(f"  Von: {source}")
    print(f"  Nach: {destination}")

    # Sicherheitsprüfung für Dateioperationen
    is_safe, message = check_file_operation_safety("move", source, destination)
    if not is_safe:
        logger.warning(f"Sicherheitsprüfung fehlgeschlagen: {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    if not auto_confirm and not _get_user_confirmation("Verschieben?"):
        logger.info("Benutzer hat Verschieben abgelehnt")
        return _create_result(success=False, error="Benutzer hat Verschieben abgelehnt")

    try:
        src = sanitize_path(source)
        dst = sanitize_path(destination)
        # Erstelle Zielverzeichnis falls nötig
        parent_dir = os.path.dirname(dst)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        shutil.move(src, dst)
        logger.info("Verschieben erfolgreich")
        return _create_result(success=True, message=f"Erfolgreich verschoben von {src} zu {dst}")
    except FileNotFoundError:
        logger.error(f"Datei nicht gefunden: {source}")
        return _create_result(success=False, error=f"Datei nicht gefunden: {source}")
    except PermissionError:
        logger.error(f"Keine Berechtigung zum Verschieben")
        return _create_result(success=False, error="Keine Berechtigung zum Verschieben")
    except Exception as e:
        logger.error(f"Verschieben fehlgeschlagen: {e}")
        return _create_result(success=False, error=str(e))


def _parse_json(json_string: str, query: Optional[str] = None) -> Dict[str, Any]:
    """Parst JSON-Daten."""
    logger.info(f"JSON parsen, Query: {query}")
    
    print(f"\n[Tool Call] JSON parsen")
    if query:
        print(f"  Query: {query}")

    # Begrenzen der Eingabelänge
    if len(json_string) > 1_000_000:  # 1 MB
        return _create_result(success=False, error="JSON zu groß (max. 1 MB)")

    try:
        data = json.loads(json_string)

        # Wenn ein Query angegeben ist, versuche den Wert zu extrahieren
        if query:
            keys = query.split('.')
            result = data
            for key in keys:
                if isinstance(result, dict):
                    result = result.get(key)
                elif isinstance(result, list) and key.isdigit():
                    result = result[int(key)]
                else:
                    logger.warning(f"Key nicht gefunden: {key}")
                    return _create_result(success=False, error=f"Key '{key}' nicht gefunden")

            return _create_result(success=True, data=result)
        else:
            return _create_result(success=True, data=data)

    except json.JSONDecodeError as e:
        logger.error(f"JSON Parsing Fehler: {e}")
        return _create_result(success=False, error=f"JSON Parsing Fehler: {str(e)}")
    except Exception as e:
        logger.error(f"Fehler beim JSON Parsing: {e}")
        return _create_result(success=False, error=str(e))


def _parse_csv(file_path: str, delimiter: str = ",") -> Dict[str, Any]:
    """Liest und parst CSV-Daten mit Pfad-Validierung."""
    logger.info(f"CSV parsen: {file_path}")
    
    print(f"\n[Tool Call] CSV-Datei parsen: {file_path}")

    # Pfad-Validierung
    is_safe, message = validate_path(file_path)
    if not is_safe:
        logger.warning(f"Pfad-Validierung fehlgeschlagen: {file_path} - {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    try:
        path = sanitize_path(file_path)
        
        # Prüfe Dateigröße
        file_size = os.path.getsize(path)
        if file_size > 10_000_000:  # 10 MB
            return _create_result(success=False, error="CSV zu groß (max. 10 MB)")
        
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            rows = list(reader)

        logger.info(f"CSV gelesen: {len(rows)} Zeilen")
        return _create_result(
            success=True,
            data=rows,
            num_rows=len(rows),
            columns=list(rows[0].keys()) if rows else []
        )
    except FileNotFoundError:
        logger.error(f"CSV nicht gefunden: {file_path}")
        return _create_result(success=False, error=f"Datei nicht gefunden: {file_path}")
    except PermissionError:
        logger.error(f"Keine Berechtigung: {file_path}")
        return _create_result(success=False, error=f"Keine Berechtigung zum Lesen: {file_path}")
    except Exception as e:
        logger.error(f"CSV Parsing Fehler: {e}")
        return _create_result(success=False, error=str(e))


def _upload_ftp(
    local_file: str,
    host: str,
    username: Optional[str],
    password: Optional[str],
    remote_path: str,
    auto_confirm: bool
) -> Dict[str, Any]:
    """Lädt eine Datei via FTP hoch mit Sicherheitsprüfungen."""
    # Verwende Umgebungsvariablen als Fallback für Credentials
    ftp_user = username or os.environ.get('FTP_USER', '')
    ftp_pass = password or os.environ.get('FTP_PASS', '')
    
    logger.info(f"FTP Upload: {local_file} -> {host}:{remote_path}")
    
    print(f"\n[Tool Call] FTP Upload:")
    print(f"  Lokale Datei: {local_file}")
    print(f"  Server: {host}")
    print(f"  Remote Pfad: {remote_path}")
    print(f"  Benutzer: {ftp_user or '(nicht gesetzt)'}")

    # Pfad-Validierung für lokale Datei
    is_safe, message = validate_path(local_file)
    if not is_safe:
        logger.warning(f"Pfad-Validierung fehlgeschlagen: {local_file} - {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    if not ftp_user or not ftp_pass:
        logger.error("FTP Credentials fehlen")
        return _create_result(
            success=False,
            error="FTP Credentials fehlen. Setze FTP_USER und FTP_PASS Umgebungsvariablen oder übergebe sie direkt."
        )

    if not auto_confirm and not _get_user_confirmation("Hochladen?"):
        logger.info("Benutzer hat Upload abgelehnt")
        return _create_result(success=False, error="Benutzer hat Upload abgelehnt")

    try:
        local = sanitize_path(local_file)
        
        if not os.path.exists(local):
            return _create_result(success=False, error=f"Lokale Datei nicht gefunden: {local_file}")

        with FTP(host, timeout=DEFAULT_TIMEOUT) as ftp:
            ftp.login(ftp_user, ftp_pass)

            with open(local, 'rb') as f:
                ftp.storbinary(f'STOR {remote_path}', f)

        logger.info("FTP Upload erfolgreich")
        return _create_result(
            success=True,
            message=f"Datei erfolgreich hochgeladen zu {host}:{remote_path}"
        )
    except Exception as e:
        logger.error(f"FTP Upload fehlgeschlagen: {e}")
        return _create_result(success=False, error=f"FTP Upload fehlgeschlagen: {str(e)}")


def _upload_sftp(
    local_file: str,
    host: str,
    port: int,
    username: Optional[str],
    password: Optional[str],
    key_path: Optional[str],
    remote_path: str,
    auto_confirm: bool
) -> Dict[str, Any]:
    """
    Lädt eine Datei sicher via SFTP hoch.
    
    Unterstützt Authentifizierung via:
    - Passwort (SFTP_PASS oder password Parameter)
    - SSH Private Key (SFTP_KEY_PATH oder key_path Parameter)
    
    Args:
        local_file: Pfad zur lokalen Datei
        host: SFTP-Server Hostname
        port: SFTP-Server Port (Standard: 22)
        username: Benutzername (oder SFTP_USER Env-Variable)
        password: Passwort (oder SFTP_PASS Env-Variable)
        key_path: Pfad zum SSH Private Key (oder SFTP_KEY_PATH Env-Variable)
        remote_path: Zielpfad auf dem Server
        auto_confirm: Automatische Bestätigung
    
    Returns:
        Ergebnis-Dictionary
    """
    # Verwende Umgebungsvariablen als Fallback für Credentials
    sftp_user = username or os.environ.get('SFTP_USER', '')
    sftp_pass = password or os.environ.get('SFTP_PASS', '')
    sftp_key = key_path or os.environ.get('SFTP_KEY_PATH', '')
    
    logger.info(f"SFTP Upload: {local_file} -> {host}:{port}{remote_path}")
    
    print(f"\n[Tool Call] SFTP Upload (verschlüsselt):")
    print(f"  Lokale Datei: {local_file}")
    print(f"  Server: {host}:{port}")
    print(f"  Remote Pfad: {remote_path}")
    print(f"  Benutzer: {sftp_user or '(nicht gesetzt)'}")
    print(f"  Auth-Methode: {'SSH-Key' if sftp_key else 'Passwort'}")

    # Prüfe ob paramiko verfügbar ist
    try:
        import paramiko
    except ImportError:
        logger.error("paramiko nicht installiert")
        return _create_result(
            success=False,
            error="SFTP benötigt die 'paramiko' Library. Installiere mit: pip install paramiko"
        )

    # Pfad-Validierung für lokale Datei
    is_safe, message = validate_path(local_file)
    if not is_safe:
        logger.warning(f"Pfad-Validierung fehlgeschlagen: {local_file} - {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    if not sftp_user:
        logger.error("SFTP Benutzername fehlt")
        return _create_result(
            success=False,
            error="SFTP Benutzername fehlt. Setze SFTP_USER Umgebungsvariable oder übergebe username."
        )

    # Prüfe Auth-Methode
    if not sftp_pass and not sftp_key:
        logger.error("SFTP Authentifizierung fehlt")
        return _create_result(
            success=False,
            error="SFTP Auth fehlt. Setze SFTP_PASS oder SFTP_KEY_PATH Umgebungsvariable."
        )

    if not auto_confirm and not _get_user_confirmation("Hochladen?"):
        logger.info("Benutzer hat SFTP Upload abgelehnt")
        return _create_result(success=False, error="Benutzer hat Upload abgelehnt")

    try:
        local = sanitize_path(local_file)
        
        if not os.path.exists(local):
            return _create_result(success=False, error=f"Lokale Datei nicht gefunden: {local_file}")

        # SSH-Verbindung aufbauen
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Verbindungsparameter
        connect_kwargs = {
            'hostname': host,
            'port': port,
            'username': sftp_user,
            'timeout': DEFAULT_TIMEOUT
        }
        
        # Authentifizierung
        if sftp_key:
            # SSH-Key Authentifizierung
            key_file = sanitize_path(sftp_key)
            if not os.path.exists(key_file):
                return _create_result(success=False, error=f"SSH-Key nicht gefunden: {sftp_key}")
            
            # Versuche verschiedene Key-Typen
            try:
                private_key = paramiko.RSAKey.from_private_key_file(key_file)
            except paramiko.SSHException:
                try:
                    private_key = paramiko.Ed25519Key.from_private_key_file(key_file)
                except paramiko.SSHException:
                    try:
                        private_key = paramiko.ECDSAKey.from_private_key_file(key_file)
                    except paramiko.SSHException:
                        return _create_result(
                            success=False,
                            error="SSH-Key konnte nicht gelesen werden. Unterstützt: RSA, Ed25519, ECDSA"
                        )
            
            connect_kwargs['pkey'] = private_key
            logger.info("SFTP: Verwende SSH-Key Authentifizierung")
        else:
            # Passwort-Authentifizierung
            connect_kwargs['password'] = sftp_pass
            logger.info("SFTP: Verwende Passwort-Authentifizierung")
        
        # Verbinden
        ssh.connect(**connect_kwargs)
        
        # SFTP-Session öffnen
        sftp = ssh.open_sftp()
        
        # Datei hochladen
        file_size = os.path.getsize(local)
        sftp.put(local, remote_path)
        
        # Verbindung schließen
        sftp.close()
        ssh.close()

        logger.info(f"SFTP Upload erfolgreich: {file_size} Bytes")
        return _create_result(
            success=True,
            message=f"Datei sicher hochgeladen zu {host}:{remote_path}",
            file_size=file_size,
            protocol="SFTP",
            encrypted=True
        )
        
    except paramiko.AuthenticationException:
        logger.error("SFTP Authentifizierung fehlgeschlagen")
        return _create_result(success=False, error="SFTP Authentifizierung fehlgeschlagen. Prüfe Benutzername/Passwort/Key.")
    except paramiko.SSHException as e:
        logger.error(f"SSH Fehler: {e}")
        return _create_result(success=False, error=f"SSH Fehler: {str(e)}")
    except Exception as e:
        logger.error(f"SFTP Upload fehlgeschlagen: {e}")
        return _create_result(success=False, error=f"SFTP Upload fehlgeschlagen: {str(e)}")


def _get_image_info(image_path: str) -> Dict[str, Any]:
    """Analysiert ein Bild mit Pfad-Validierung."""
    logger.info(f"Bild analysieren: {image_path}")
    
    print(f"\n[Tool Call] Bild analysieren: {image_path}")

    # Pfad-Validierung
    is_safe, message = validate_path(image_path)
    if not is_safe:
        logger.warning(f"Pfad-Validierung fehlgeschlagen: {image_path} - {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    try:
        path = sanitize_path(image_path)
        
        if not os.path.exists(path):
            logger.error(f"Bild nicht gefunden: {image_path}")
            return _create_result(success=False, error="Datei nicht gefunden")

        # Versuche PIL/Pillow zu importieren (optional)
        try:
            from PIL import Image

            with Image.open(path) as img:
                result = _create_result(
                    success=True,
                    format=img.format,
                    mode=img.mode,
                    size=img.size,
                    width=img.width,
                    height=img.height,
                    file_size=os.path.getsize(path)
                )
                logger.info(f"Bild analysiert: {img.format} {img.width}x{img.height}")
                return result
                
        except ImportError:
            # Fallback ohne PIL - nur Dateigröße
            file_size = os.path.getsize(path)
            logger.info(f"Bild-Dateigröße (ohne PIL): {file_size} Bytes")
            return _create_result(
                success=True,
                file_size=file_size,
                message="PIL nicht installiert - nur Dateigröße verfügbar. Installiere mit: pip install Pillow"
            )

    except PermissionError:
        logger.error(f"Keine Berechtigung: {image_path}")
        return _create_result(success=False, error=f"Keine Berechtigung zum Lesen: {image_path}")
    except Exception as e:
        logger.error(f"Bildanalyse fehlgeschlagen: {e}")
        return _create_result(success=False, error=str(e))


# ============================================================================
# Tool-Dispatcher
# ============================================================================

def execute_tool(
    tool_name: str,
    tool_args: Dict[str, Any],
    auto_confirm: bool = False
) -> Dict[str, Any]:
    """
    Führt ein Tool aus und gibt das Ergebnis zurück.
    
    Args:
        tool_name: Name des Tools
        tool_args: Argumente für das Tool
        auto_confirm: Ob Aktionen automatisch bestätigt werden
    
    Returns:
        Ergebnis-Dictionary mit success, message/error und weiteren Daten
    """
    logger.debug(f"Tool ausführen: {tool_name} mit Args: {tool_args}")

    # Tool-Dispatcher
    tool_handlers = {
        "execute_bash_command": lambda: _execute_bash_command(
            tool_args.get("command", ""),
            tool_args.get("explanation", ""),
            auto_confirm
        ),
        "read_file": lambda: _read_file(tool_args.get("file_path", "")),
        "write_file": lambda: _write_file(
            tool_args.get("file_path", ""),
            tool_args.get("content", ""),
            auto_confirm
        ),
        "fetch_url": lambda: _fetch_url(
            tool_args.get("url", ""),
            tool_args.get("method", "GET")
        ),
        "download_file": lambda: _download_file(
            tool_args.get("url", ""),
            tool_args.get("destination", ""),
            auto_confirm
        ),
        "search_web": lambda: _search_web(
            tool_args.get("query", ""),
            tool_args.get("num_results", 5)
        ),
        "rename_file": lambda: _rename_file(
            tool_args.get("old_path", ""),
            tool_args.get("new_path", ""),
            auto_confirm
        ),
        "copy_file": lambda: _copy_file(
            tool_args.get("source", ""),
            tool_args.get("destination", ""),
            auto_confirm
        ),
        "move_file": lambda: _move_file(
            tool_args.get("source", ""),
            tool_args.get("destination", ""),
            auto_confirm
        ),
        "parse_json": lambda: _parse_json(
            tool_args.get("json_string", ""),
            tool_args.get("query")
        ),
        "parse_csv": lambda: _parse_csv(
            tool_args.get("file_path", ""),
            tool_args.get("delimiter", ",")
        ),
        "upload_ftp": lambda: _upload_ftp(
            tool_args.get("local_file", ""),
            tool_args.get("host", ""),
            tool_args.get("username"),
            tool_args.get("password"),
            tool_args.get("remote_path", ""),
            auto_confirm
        ),
        "get_image_info": lambda: _get_image_info(tool_args.get("image_path", "")),
        "upload_sftp": lambda: _upload_sftp(
            tool_args.get("local_file", ""),
            tool_args.get("host", ""),
            tool_args.get("port", 22),
            tool_args.get("username"),
            tool_args.get("password"),
            tool_args.get("key_path"),
            tool_args.get("remote_path", ""),
            auto_confirm
        )
    }

    handler = tool_handlers.get(tool_name)
    if handler:
        return handler()
    else:
        logger.error(f"Unbekanntes Tool: {tool_name}")
        return _create_result(success=False, error=f"Unbekanntes Tool: {tool_name}")
