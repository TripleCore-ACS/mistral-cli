#!/usr/bin/env python3
"""
Mistral CLI - Tool Definitions and Execution
Contains all 13 tools for Mistral AI function calling
"""

import os
import subprocess
import json
import shutil
import csv
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import quote_plus
import html
from ftplib import FTP


# Tool-Definitionen für Function Calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_bash_command",
            "description": "Führt einen Bash-Befehl auf dem System aus. Verwende dies, um Dateien zu erstellen, Ordner anzulegen, Programme auszuführen, etc.",
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
            "description": "Liest den Inhalt einer Datei",
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
            "description": "Schreibt Inhalt in eine Datei (erstellt oder überschreibt)",
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
            "description": "Ruft den Inhalt einer URL ab (Webseiten, APIs, etc.). Gibt HTML, JSON oder Text zurück.",
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
            "description": "Lädt eine Datei von einer URL herunter und speichert sie lokal",
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
                        "description": "Anzahl der gewünschten Ergebnisse (Standard: 5)",
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
            "description": "Lädt eine Datei via FTP auf einen Server hoch",
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
                        "description": "FTP-Benutzername"
                    },
                    "password": {
                        "type": "string",
                        "description": "FTP-Passwort"
                    },
                    "remote_path": {
                        "type": "string",
                        "description": "Zielpfad auf dem FTP-Server"
                    }
                },
                "required": ["local_file", "host", "username", "password", "remote_path"]
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
    }
]


def execute_tool(tool_name, tool_args, auto_confirm=False):
    """Führt ein Tool aus und gibt das Ergebnis zurück."""

    if tool_name == "execute_bash_command":
        command = tool_args.get("command")
        explanation = tool_args.get("explanation", "")

        print(f"\n[Tool Call] Bash-Befehl ausführen:")
        print(f"  Befehl: {command}")
        print(f"  Erklärung: {explanation}")

        if not auto_confirm:
            response = input("  Ausführen? (y/n): ").strip().lower()
            if response not in ['y', 'yes', 'j', 'ja']:
                return {"success": False, "output": "Benutzer hat Ausführung abgelehnt"}

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                timeout=30
            )

            output = result.stdout if result.stdout else result.stderr
            return {
                "success": result.returncode == 0,
                "output": output,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "Befehl hat Timeout überschritten (30s)"}
        except Exception as e:
            return {"success": False, "output": f"Fehler: {str(e)}"}

    elif tool_name == "read_file":
        file_path = tool_args.get("file_path")

        print(f"\n[Tool Call] Datei lesen: {file_path}")

        try:
            with open(os.path.expanduser(file_path), 'r') as f:
                content = f.read()
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "write_file":
        file_path = tool_args.get("file_path")
        content = tool_args.get("content")

        print(f"\n[Tool Call] Datei schreiben: {file_path}")
        print(f"  Inhalt: {content[:100]}..." if len(content) > 100 else f"  Inhalt: {content}")

        if not auto_confirm:
            response = input("  Schreiben? (y/n): ").strip().lower()
            if response not in ['y', 'yes', 'j', 'ja']:
                return {"success": False, "error": "Benutzer hat Schreiben abgelehnt"}

        try:
            with open(os.path.expanduser(file_path), 'w') as f:
                f.write(content)
            return {"success": True, "message": "Datei erfolgreich geschrieben"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "fetch_url":
        url = tool_args.get("url")
        method = tool_args.get("method", "GET")

        print(f"\n[Tool Call] URL abrufen: {url}")
        print(f"  Methode: {method}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
            req = Request(url, headers=headers)
            with urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8')
                content_type = response.headers.get('Content-Type', '')

                # Begrenze die Ausgabe auf 10000 Zeichen
                if len(content) > 10000:
                    content = content[:10000] + "\n... (gekürzt)"

                return {
                    "success": True,
                    "content": content,
                    "content_type": content_type,
                    "status_code": response.status
                }
        except HTTPError as e:
            return {"success": False, "error": f"HTTP Fehler {e.code}: {e.reason}"}
        except URLError as e:
            return {"success": False, "error": f"URL Fehler: {str(e.reason)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "download_file":
        url = tool_args.get("url")
        destination = tool_args.get("destination")

        print(f"\n[Tool Call] Datei herunterladen:")
        print(f"  Von: {url}")
        print(f"  Nach: {destination}")

        if not auto_confirm:
            response = input("  Herunterladen? (y/n): ").strip().lower()
            if response not in ['y', 'yes', 'j', 'ja']:
                return {"success": False, "error": "Benutzer hat Download abgelehnt"}

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
            req = Request(url, headers=headers)

            with urlopen(req, timeout=30) as response:
                content = response.read()

                dest_path = os.path.expanduser(destination)
                with open(dest_path, 'wb') as f:
                    f.write(content)

                file_size = len(content)
                return {
                    "success": True,
                    "message": f"Datei erfolgreich heruntergeladen ({file_size} Bytes)",
                    "file_size": file_size,
                    "destination": dest_path
                }
        except HTTPError as e:
            return {"success": False, "error": f"HTTP Fehler {e.code}: {e.reason}"}
        except URLError as e:
            return {"success": False, "error": f"URL Fehler: {str(e.reason)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "search_web":
        query = tool_args.get("query")
        num_results = tool_args.get("num_results", 5)

        print(f"\n[Tool Call] Web-Suche: '{query}'")
        print(f"  Anzahl Ergebnisse: {num_results}")

        try:
            # Verwende DuckDuckGo HTML (keine API-Key erforderlich)
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
            req = Request(search_url, headers=headers)

            with urlopen(req, timeout=10) as response:
                html_content = response.read().decode('utf-8')

            # Einfaches Parsing der Suchergebnisse (Regex-basiert)
            results = []

            # Finde Ergebnisse im HTML
            import re
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
                return {
                    "success": False,
                    "error": "Keine Suchergebnisse gefunden"
                }

            return {
                "success": True,
                "query": query,
                "results": results,
                "num_results": len(results)
            }
        except Exception as e:
            return {"success": False, "error": f"Suche fehlgeschlagen: {str(e)}"}

    elif tool_name == "rename_file":
        old_path = tool_args.get("old_path")
        new_path = tool_args.get("new_path")

        print(f"\n[Tool Call] Datei umbenennen:")
        print(f"  Von: {old_path}")
        print(f"  Nach: {new_path}")

        if not auto_confirm:
            response = input("  Umbenennen? (y/n): ").strip().lower()
            if response not in ['y', 'yes', 'j', 'ja']:
                return {"success": False, "error": "Benutzer hat Umbenennen abgelehnt"}

        try:
            old_path = os.path.expanduser(old_path)
            new_path = os.path.expanduser(new_path)
            os.rename(old_path, new_path)
            return {"success": True, "message": f"Erfolgreich umbenannt von {old_path} zu {new_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "copy_file":
        source = tool_args.get("source")
        destination = tool_args.get("destination")

        print(f"\n[Tool Call] Datei/Ordner kopieren:")
        print(f"  Von: {source}")
        print(f"  Nach: {destination}")

        if not auto_confirm:
            response = input("  Kopieren? (y/n): ").strip().lower()
            if response not in ['y', 'yes', 'j', 'ja']:
                return {"success": False, "error": "Benutzer hat Kopieren abgelehnt"}

        try:
            source = os.path.expanduser(source)
            destination = os.path.expanduser(destination)

            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)

            return {"success": True, "message": f"Erfolgreich kopiert von {source} zu {destination}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "move_file":
        source = tool_args.get("source")
        destination = tool_args.get("destination")

        print(f"\n[Tool Call] Datei/Ordner verschieben:")
        print(f"  Von: {source}")
        print(f"  Nach: {destination}")

        if not auto_confirm:
            response = input("  Verschieben? (y/n): ").strip().lower()
            if response not in ['y', 'yes', 'j', 'ja']:
                return {"success": False, "error": "Benutzer hat Verschieben abgelehnt"}

        try:
            source = os.path.expanduser(source)
            destination = os.path.expanduser(destination)
            shutil.move(source, destination)
            return {"success": True, "message": f"Erfolgreich verschoben von {source} zu {destination}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "parse_json":
        json_string = tool_args.get("json_string")
        query = tool_args.get("query")

        print(f"\n[Tool Call] JSON parsen")
        if query:
            print(f"  Query: {query}")

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
                        return {"success": False, "error": f"Key '{key}' nicht gefunden"}

                return {"success": True, "data": result}
            else:
                return {"success": True, "data": data}

        except json.JSONDecodeError as e:
            return {"success": False, "error": f"JSON Parsing Fehler: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "parse_csv":
        file_path = tool_args.get("file_path")
        delimiter = tool_args.get("delimiter", ",")

        print(f"\n[Tool Call] CSV-Datei parsen: {file_path}")

        try:
            file_path = os.path.expanduser(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                rows = list(reader)

            return {
                "success": True,
                "data": rows,
                "num_rows": len(rows),
                "columns": list(rows[0].keys()) if rows else []
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif tool_name == "upload_ftp":
        local_file = tool_args.get("local_file")
        host = tool_args.get("host")
        username = tool_args.get("username")
        password = tool_args.get("password")
        remote_path = tool_args.get("remote_path")

        print(f"\n[Tool Call] FTP Upload:")
        print(f"  Lokale Datei: {local_file}")
        print(f"  Server: {host}")
        print(f"  Remote Pfad: {remote_path}")

        if not auto_confirm:
            response = input("  Hochladen? (y/n): ").strip().lower()
            if response not in ['y', 'yes', 'j', 'ja']:
                return {"success": False, "error": "Benutzer hat Upload abgelehnt"}

        try:
            local_file = os.path.expanduser(local_file)

            with FTP(host) as ftp:
                ftp.login(username, password)

                with open(local_file, 'rb') as f:
                    ftp.storbinary(f'STOR {remote_path}', f)

            return {
                "success": True,
                "message": f"Datei erfolgreich hochgeladen zu {host}:{remote_path}"
            }
        except Exception as e:
            return {"success": False, "error": f"FTP Upload fehlgeschlagen: {str(e)}"}

    elif tool_name == "get_image_info":
        image_path = tool_args.get("image_path")

        print(f"\n[Tool Call] Bild analysieren: {image_path}")

        try:
            # Versuche PIL/Pillow zu importieren (optional)
            try:
                from PIL import Image

                image_path = os.path.expanduser(image_path)
                with Image.open(image_path) as img:
                    return {
                        "success": True,
                        "format": img.format,
                        "mode": img.mode,
                        "size": img.size,
                        "width": img.width,
                        "height": img.height,
                        "file_size": os.path.getsize(image_path)
                    }
            except ImportError:
                # Fallback ohne PIL - nur Dateigröße
                image_path = os.path.expanduser(image_path)
                if os.path.exists(image_path):
                    file_size = os.path.getsize(image_path)
                    return {
                        "success": True,
                        "file_size": file_size,
                        "message": "PIL nicht installiert - nur Dateigröße verfügbar. Installiere mit: pip install Pillow"
                    }
                else:
                    return {"success": False, "error": "Datei nicht gefunden"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    return {"success": False, "error": f"Unbekanntes Tool: {tool_name}"}
