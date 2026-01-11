#!/usr/bin/env python3
"""
Mistral CLI - Data Processing Tools
JSON and CSV Parsing

Version: 1.5.2
"""

import os
import json
import csv
from typing import Dict, Any, Optional

from ..core.logging_config import logger
from ..security.path_validator import validate_path
from ..security.sanitizers import sanitize_path
from .system import _create_result


# ============================================================================
# JSON Processing
# ============================================================================

def parse_json(json_string: str, query: Optional[str] = None) -> Dict[str, Any]:
    """Parses JSON data."""
    logger.info(f"Parsing JSON, Query: {query}")

    print(f"\n[Tool Call] Parse JSON")
    if query:
        print(f"  Query: {query}")

    # Limit input length
    if len(json_string) > 1_000_000:  # 1 MB
        return _create_result(success=False, error="JSON too large (max. 1 MB)")

    try:
        data = json.loads(json_string)

        # If a query is provided, try to extract the value
        if query:
            keys = query.split('.')
            result = data
            for key in keys:
                if isinstance(result, dict):
                    result = result.get(key)
                elif isinstance(result, list) and key.isdigit():
                    result = result[int(key)]
                else:
                    logger.warning(f"Key not found: {key}")
                    return _create_result(success=False, error=f"Key '{key}' not found")

            return _create_result(success=True, data=result)
        else:
            return _create_result(success=True, data=data)

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return _create_result(success=False, error=f"JSON parsing error: {str(e)}")
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return _create_result(success=False, error=str(e))


# ============================================================================
# CSV Processing
# ============================================================================

def parse_csv(file_path: str, delimiter: str = ",") -> Dict[str, Any]:
    """Reads and parses CSV data with path validation."""
    logger.info(f"Parsing CSV: {file_path}")

    print(f"\n[Tool Call] Parse CSV file: {file_path}")

    # Path validation
    is_safe, message = validate_path(file_path)
    if not is_safe:
        logger.warning(f"Path validation failed: {file_path} - {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    try:
        path = sanitize_path(file_path)

        # Check file size
        file_size = os.path.getsize(path)
        if file_size > 10_000_000:  # 10 MB
            return _create_result(success=False, error="CSV too large (max. 10 MB)")

        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            rows = list(reader)

        logger.info(f"CSV read: {len(rows)} rows")
        return _create_result(
            success=True,
            data=rows,
            num_rows=len(rows),
            columns=list(rows[0].keys()) if rows else []
        )
    except FileNotFoundError:
        logger.error(f"CSV not found: {file_path}")
        return _create_result(success=False, error=f"File not found: {file_path}")
    except PermissionError:
        logger.error(f"No permission: {file_path}")
        return _create_result(success=False, error=f"No permission to read: {file_path}")
    except Exception as e:
        logger.error(f"CSV parsing error: {e}")
        return _create_result(success=False, error=str(e))
