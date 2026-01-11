#!/usr/bin/env python3
"""
Mistral CLI - Tool Definitions
Definitions of all 14 tools for Function Calling

Version: 1.5.2
"""

from typing import List, Dict, Any


# ============================================================================
# Tool Definitions for Function Calling
# ============================================================================

TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "execute_bash_command",
            "description": "Executes a Bash command on the system. Use this to create files, create folders, run programs, etc. NOTE: Dangerous commands are automatically blocked.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The Bash command to execute"
                    },
                    "explanation": {
                        "type": "string",
                        "description": "A brief explanation of what the command does"
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
            "description": "Reads the contents of a file. NOTE: Access to system files is restricted.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file"
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
            "description": "Writes content to a file (creates or overwrites). NOTE: Writing to system directories is not allowed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file"
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
            "description": "Retrieves the content of a URL (websites, APIs, etc.). Returns HTML, JSON or text. NOTE: Local/private IP addresses are blocked.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The complete URL (with http:// or https://)"
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET or POST)",
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
            "description": "Downloads a file from a URL and saves it locally. NOTE: Downloads from local/private IPs are blocked.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the file to download"
                    },
                    "destination": {
                        "type": "string",
                        "description": "The local path where the file should be saved"
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
            "description": "Searches the internet for information. Returns a list of search results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of desired results (default: 5, maximum: 10)",
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
            "description": "Renames a file or folder",
            "parameters": {
                "type": "object",
                "properties": {
                    "old_path": {
                        "type": "string",
                        "description": "The current path of the file/folder"
                    },
                    "new_path": {
                        "type": "string",
                        "description": "The new path/name"
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
            "description": "Copies a file or folder",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "The source path"
                    },
                    "destination": {
                        "type": "string",
                        "description": "The destination path"
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
            "description": "Moves a file or folder",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "The source path"
                    },
                    "destination": {
                        "type": "string",
                        "description": "The destination path"
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
            "description": "Parses JSON data and extracts information",
            "parameters": {
                "type": "object",
                "properties": {
                    "json_string": {
                        "type": "string",
                        "description": "The JSON string to parse"
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional JSONPath or key to extract specific data"
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
            "description": "Reads and parses CSV data",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the CSV file"
                    },
                    "delimiter": {
                        "type": "string",
                        "description": "Delimiter (default: comma)",
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
            "description": "Uploads a file to a server via FTP. NOTE: Use environment variables FTP_USER and FTP_PASS for credentials.",
            "parameters": {
                "type": "object",
                "properties": {
                    "local_file": {
                        "type": "string",
                        "description": "Path to the local file"
                    },
                    "host": {
                        "type": "string",
                        "description": "FTP server host"
                    },
                    "username": {
                        "type": "string",
                        "description": "FTP username (optional, uses FTP_USER env variable)"
                    },
                    "password": {
                        "type": "string",
                        "description": "FTP password (optional, uses FTP_PASS env variable)"
                    },
                    "remote_path": {
                        "type": "string",
                        "description": "Destination path on the FTP server"
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
            "description": "Analyzes an image and returns information (format, size, dimensions)",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image"
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
            "description": "Uploads a file securely via SFTP (SSH File Transfer Protocol) to a server. Encrypted alternative to FTP. NOTE: Use environment variables SFTP_USER, SFTP_PASS or SFTP_KEY_PATH for credentials.",
            "parameters": {
                "type": "object",
                "properties": {
                    "local_file": {
                        "type": "string",
                        "description": "Path to the local file"
                    },
                    "host": {
                        "type": "string",
                        "description": "SFTP server host"
                    },
                    "port": {
                        "type": "integer",
                        "description": "SFTP server port (default: 22)",
                        "default": 22
                    },
                    "username": {
                        "type": "string",
                        "description": "SFTP username (optional, uses SFTP_USER env variable)"
                    },
                    "password": {
                        "type": "string",
                        "description": "SFTP password (optional, uses SFTP_PASS env variable)"
                    },
                    "key_path": {
                        "type": "string",
                        "description": "Path to SSH private key (optional, uses SFTP_KEY_PATH env variable)"
                    },
                    "remote_path": {
                        "type": "string",
                        "description": "Destination path on the SFTP server"
                    }
                },
                "required": ["local_file", "host", "remote_path"]
            }
        }
    }
]
