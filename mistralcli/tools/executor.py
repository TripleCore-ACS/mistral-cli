#!/usr/bin/env python3
"""
Mistral CLI - Tool Executor
Dispatcher for all 14 tools

Version: 1.5.2
"""

from typing import Dict, Any

from ..core.logging_config import logger
from .system import execute_bash_command, _create_result
from .filesystem import read_file, write_file, rename_file, copy_file, move_file
from .network import fetch_url, download_file, search_web
from .transfer import upload_ftp, upload_sftp
from .data import parse_json, parse_csv
from .image import get_image_info


# ============================================================================
# Tool Executor/Dispatcher
# ============================================================================

def execute_tool(
    tool_name: str,
    tool_args: Dict[str, Any],
    auto_confirm: bool = False
) -> Dict[str, Any]:
    """
    Executes a tool and returns the result.

    Args:
        tool_name: Name of the tool
        tool_args: Arguments for the tool
        auto_confirm: Whether actions are automatically confirmed

    Returns:
        Result dictionary with success, message/error and additional data
    """
    logger.debug(f"Executing tool: {tool_name} with args: {tool_args}")

    # Tool-Dispatcher
    tool_handlers = {
        "execute_bash_command": lambda: execute_bash_command(
            tool_args.get("command", ""),
            tool_args.get("explanation", ""),
            auto_confirm
        ),
        "read_file": lambda: read_file(tool_args.get("file_path", "")),
        "write_file": lambda: write_file(
            tool_args.get("file_path", ""),
            tool_args.get("content", ""),
            auto_confirm
        ),
        "fetch_url": lambda: fetch_url(
            tool_args.get("url", ""),
            tool_args.get("method", "GET")
        ),
        "download_file": lambda: download_file(
            tool_args.get("url", ""),
            tool_args.get("destination", ""),
            auto_confirm
        ),
        "search_web": lambda: search_web(
            tool_args.get("query", ""),
            tool_args.get("num_results", 5)
        ),
        "rename_file": lambda: rename_file(
            tool_args.get("old_path", ""),
            tool_args.get("new_path", ""),
            auto_confirm
        ),
        "copy_file": lambda: copy_file(
            tool_args.get("source", ""),
            tool_args.get("destination", ""),
            auto_confirm
        ),
        "move_file": lambda: move_file(
            tool_args.get("source", ""),
            tool_args.get("destination", ""),
            auto_confirm
        ),
        "parse_json": lambda: parse_json(
            tool_args.get("json_string", ""),
            tool_args.get("query")
        ),
        "parse_csv": lambda: parse_csv(
            tool_args.get("file_path", ""),
            tool_args.get("delimiter", ",")
        ),
        "upload_ftp": lambda: upload_ftp(
            tool_args.get("local_file", ""),
            tool_args.get("host", ""),
            tool_args.get("username"),
            tool_args.get("password"),
            tool_args.get("remote_path", ""),
            auto_confirm
        ),
        "get_image_info": lambda: get_image_info(tool_args.get("image_path", "")),
        "upload_sftp": lambda: upload_sftp(
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
        logger.error(f"Unknown tool: {tool_name}")
        return _create_result(success=False, error=f"Unknown tool: {tool_name}")
