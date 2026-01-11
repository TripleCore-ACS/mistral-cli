#!/usr/bin/env python3
"""
Mistral CLI - Image Analysis Tools
Image analysis with PIL/Pillow

Version: 1.5.2
"""

import os
from typing import Dict, Any

from ..core.logging_config import logger
from ..security.path_validator import validate_path
from ..security.sanitizers import sanitize_path
from .system import _create_result


# ============================================================================
# Image Analysis
# ============================================================================

def get_image_info(image_path: str) -> Dict[str, Any]:
    """Analyzes an image with path validation."""
    logger.info(f"Analyzing image: {image_path}")

    print(f"\n[Tool Call] Analyze image: {image_path}")

    # Path validation
    is_safe, message = validate_path(image_path)
    if not is_safe:
        logger.warning(f"Path validation failed: {image_path} - {message}")
        print(f"  ⚠️  {message}")
        return _create_result(success=False, error=message)

    try:
        path = sanitize_path(image_path)

        if not os.path.exists(path):
            logger.error(f"Image not found: {image_path}")
            return _create_result(success=False, error="File not found")

        # Try to import PIL/Pillow (optional)
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
                logger.info(f"Image analyzed: {img.format} {img.width}x{img.height}")
                return result

        except ImportError:
            # Fallback without PIL - only file size
            file_size = os.path.getsize(path)
            logger.info(f"Image file size (without PIL): {file_size} bytes")
            return _create_result(
                success=True,
                file_size=file_size,
                message="PIL not installed - only file size available. Install with: pip install Pillow"
            )

    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        return _create_result(success=False, error=str(e))
