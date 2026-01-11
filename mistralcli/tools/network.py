#!/usr/bin/env python3
"""
Mistral CLI - Network Tools
HTTP requests, downloads and web search

Version: 1.5.2
"""

import re
import html
from typing import Dict, Any, List
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import quote_plus

from ..core.config import DEFAULT_TIMEOUT
from ..core.logging_config import logger
from ..security.url_validator import validate_url
from .system import _create_result


# ============================================================================
# HTTP Operations
# ============================================================================

def fetch_url(url: str, method: str = "GET") -> Dict[str, Any]:
    """Retrieves the content of a URL with URL validation."""
    logger.info(f"Fetching URL: {url} ({method})")

    print(f"\n[Tool Call] Fetch URL: {url}")
    print(f"  Method: {method}")

    # URL validation
    is_safe, message = validate_url(url)
    if not is_safe:
        logger.warning(f"URL validation failed: {url} - {message}")
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

            # Limit output to 10000 characters
            if len(content) > 10000:
                content = content[:10000] + "\n... (truncated)"

            logger.info(f"URL fetched: {len(content)} characters, status: {response.status}")
            return _create_result(
                success=True,
                content=content,
                content_type=content_type,
                status_code=response.status
            )
    except HTTPError as e:
        logger.error(f"HTTP error: {e.code} {e.reason}")
        return _create_result(success=False, error=f"HTTP error {e.code}: {e.reason}")
    except URLError as e:
        logger.error(f"URL error: {e.reason}")
        return _create_result(success=False, error=f"URL error: {str(e.reason)}")
    except Exception as e:
        logger.error(f"Error fetching URL: {e}")
        return _create_result(success=False, error=str(e))


def download_file(
    url: str,
    destination: str,
    auto_confirm: bool = False
) -> Dict[str, Any]:
    """Downloads a file with URL and path validation."""
    import os
    from ..security.path_validator import validate_path
    from ..security.sanitizers import sanitize_path
    from .system import _get_user_confirmation

    logger.info(f"Download: {url} -> {destination}")

    print(f"\n[Tool Call] Download file:")
    print(f"  From: {url}")
    print(f"  To: {destination}")

    # URL validation
    is_safe, message = validate_url(url)
    if not is_safe:
        logger.warning(f"URL validation failed: {url} - {message}")
        print(f"  ⚠️  URL: {message}")
        return _create_result(success=False, error=f"URL unsafe: {message}")

    # Path validation
    is_safe, message = validate_path(destination)
    if not is_safe:
        logger.warning(f"Path validation failed: {destination} - {message}")
        print(f"  ⚠️  Path: {message}")
        return _create_result(success=False, error=f"Path unsafe: {message}")

    if not auto_confirm and not _get_user_confirmation("Download?"):
        logger.info("User declined download")
        return _create_result(success=False, error="User declined download")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        req = Request(url, headers=headers)

        with urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
            content = response.read()

            # Check download limit (100 MB)
            MAX_DOWNLOAD_SIZE = 100 * 1024 * 1024  # 100 MB
            if len(content) > MAX_DOWNLOAD_SIZE:
                logger.warning(f"Download too large: {len(content)} bytes")
                return _create_result(
                    success=False,
                    error=f"File too large ({len(content) / 1024 / 1024:.1f} MB). Maximum: 100 MB"
                )

            dest_path = sanitize_path(destination)
            # Create directory if necessary
            parent_dir = os.path.dirname(dest_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            with open(dest_path, 'wb') as f:
                f.write(content)

            file_size = len(content)
            logger.info(f"Download successful: {file_size} bytes")
            return _create_result(
                success=True,
                message=f"File downloaded successfully ({file_size} bytes)",
                file_size=file_size,
                destination=dest_path
            )
    except HTTPError as e:
        logger.error(f"HTTP error during download: {e.code}")
        return _create_result(success=False, error=f"HTTP error {e.code}: {e.reason}")
    except URLError as e:
        logger.error(f"URL error during download: {e.reason}")
        return _create_result(success=False, error=f"URL error: {str(e.reason)}")
    except Exception as e:
        logger.error(f"Download error: {e}")
        return _create_result(success=False, error=str(e))


def search_web(query: str, num_results: int = 5) -> Dict[str, Any]:
    """Searches the web with DuckDuckGo."""
    # Limit results to maximum 10
    num_results = min(num_results, 10)

    logger.info(f"Web search: '{query}' (max {num_results} results)")

    print(f"\n[Tool Call] Web search: '{query}'")
    print(f"  Number of results: {num_results}")

    # Simple query validation
    if len(query) < 2:
        return _create_result(success=False, error="Search query too short (min. 2 characters)")

    if len(query) > 500:
        return _create_result(success=False, error="Search query too long (max. 500 characters)")

    try:
        # Use DuckDuckGo HTML (no API key required)
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        req = Request(search_url, headers=headers)

        with urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
            html_content = response.read().decode('utf-8')

        # Simple parsing of search results (regex-based)
        results: List[Dict[str, str]] = []

        # Find results in HTML
        result_pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)</a>'
        snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]+)</a>'

        matches = re.findall(result_pattern, html_content)
        snippets = re.findall(snippet_pattern, html_content)

        for i, (url, title) in enumerate(matches[:num_results]):
            snippet = snippets[i] if i < len(snippets) else ""
            # Decode HTML entities
            title = html.unescape(title)
            snippet = html.unescape(snippet)

            results.append({
                "title": title,
                "url": url,
                "snippet": snippet
            })

        if not results:
            logger.warning(f"No search results for: {query}")
            return _create_result(success=False, error="No search results found")

        logger.info(f"Search successful: {len(results)} results")
        return _create_result(
            success=True,
            query=query,
            results=results,
            num_results=len(results)
        )
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return _create_result(success=False, error=f"Search failed: {str(e)}")
