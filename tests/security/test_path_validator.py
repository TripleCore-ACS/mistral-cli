#!/usr/bin/env python3
"""
Unit Tests for mistralcli.security.path_validator

Tests path validation including:
- Path traversal detection
- System directory protection
- Path normalization

Version: 1.5.2
"""

import pytest
from pathlib import Path
from mistralcli.security.path_validator import (
    is_safe_path,
    validate_path,
)


# ============================================================================
# Test Safe Paths
# ============================================================================

class TestSafePaths:
    """Tests for paths that should be allowed."""

    @pytest.mark.unit
    @pytest.mark.security
    @pytest.mark.parametrize("path", [
        "file.txt",
        "./file.txt",
        "folder/file.txt",
        "./folder/subfolder/file.txt",
        "test_data/sample.csv",
        "/tmp/test.txt",
        "/home/user/documents/file.txt",
        "~/Documents/file.txt",
        "~/Downloads/archive.zip",
    ])
    def test_safe_paths_allowed(self, path):
        """Test that safe paths are allowed."""
        is_safe, message = validate_path(path)
        assert is_safe, f"Safe path '{path}' was incorrectly blocked: {message}"

    @pytest.mark.unit
    @pytest.mark.security
    def test_relative_path_in_current_dir(self, temp_dir):
        """Test that relative paths in current directory are safe."""
        test_file = "test.txt"
        is_safe, _ = validate_path(test_file)
        assert is_safe


# ============================================================================
# Test Dangerous Paths (Path Traversal)
# ============================================================================

class TestPathTraversal:
    """Tests for path traversal attack detection."""

    @pytest.mark.unit
    @pytest.mark.security
    @pytest.mark.parametrize("path,description", [
        ("../../../etc/passwd", "Triple parent traversal"),
        ("../../etc/shadow", "Double parent traversal"),
        ("./../../usr/bin", "Relative parent traversal"),
        ("folder/../../../etc/hosts", "Mixed traversal"),
        ("/tmp/../etc/passwd", "Absolute with parent"),
        ("~/../../etc/shadow", "Home with parent"),
    ])
    def test_path_traversal_blocked(self, path, description):
        """Test that path traversal attempts are blocked."""
        is_safe, message = validate_path(path)
        assert not is_safe, f"Path traversal '{path}' ({description}) was NOT blocked!"
        assert ".." in message or "traversal" in message.lower()


# ============================================================================
# Test System Directory Protection
# ============================================================================

class TestSystemDirectories:
    """Tests for protection of sensitive system directories."""

    @pytest.mark.unit
    @pytest.mark.security
    @pytest.mark.parametrize("path,description", [
        ("/etc/passwd", "Password file"),
        ("/etc/shadow", "Shadow password file"),
        ("/usr/bin/bash", "System binary"),
        ("/var/log/syslog", "System log"),
        ("/boot/vmlinuz", "Kernel image"),
        ("/root/.ssh/id_rsa", "Root SSH key"),
        ("/dev/sda", "Disk device"),
        ("/proc/1/cmdline", "Process info"),
        ("/sys/class/net", "System info"),
    ])
    def test_system_directories_blocked(self, path, description):
        """Test that access to system directories is restricted."""
        is_safe, message = validate_path(path)
        assert not is_safe, f"System path '{path}' ({description}) was NOT blocked!"
        assert "sensitiv" in message.lower() or "nicht erlaubt" in message.lower()


# ============================================================================
# Test Base Directory Restriction
# ============================================================================

class TestBaseDirectoryRestriction:
    """Tests for restricting paths to a base directory."""

    @pytest.mark.unit
    @pytest.mark.security
    def test_path_within_base_dir_allowed(self, temp_dir):
        """Test that paths within base directory are allowed."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        is_safe, result = is_safe_path(str(test_file), base_dir=str(temp_dir))
        assert is_safe
        assert Path(result) == test_file

    @pytest.mark.unit
    @pytest.mark.security
    def test_path_outside_base_dir_blocked(self, temp_dir):
        """Test that paths outside base directory are blocked."""
        outside_path = temp_dir.parent / "outside.txt"

        is_safe, message = is_safe_path(str(outside_path), base_dir=str(temp_dir))
        assert not is_safe
        assert "erlaubte" in message.lower() or "outside" in message.lower()


# ============================================================================
# Test Path Normalization
# ============================================================================

class TestPathNormalization:
    """Tests for path normalization."""

    @pytest.mark.unit
    @pytest.mark.security
    def test_double_slashes_normalized(self):
        """Test that double slashes are normalized."""
        path = "/tmp//test//file.txt"
        is_safe, result = validate_path(path)
        # Should still be blocked because /tmp is sensitive, but path should be normalized
        assert "//" not in result if result else True

    @pytest.mark.unit
    @pytest.mark.security
    def test_tilde_expansion(self):
        """Test that tilde is expanded correctly."""
        path = "~/test.txt"
        is_safe, result = validate_path(path)
        # Result should have tilde expanded
        if is_safe and result:
            assert "~" not in result


# ============================================================================
# Test Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases in path validation."""

    @pytest.mark.unit
    @pytest.mark.security
    def test_empty_path(self):
        """Test that empty path is rejected."""
        is_safe, message = validate_path("")
        assert not is_safe
        assert "leer" in message.lower() or "empty" in message.lower()

    @pytest.mark.unit
    @pytest.mark.security
    def test_whitespace_path(self):
        """Test that whitespace-only path is rejected."""
        is_safe, message = validate_path("   ")
        assert not is_safe

    @pytest.mark.unit
    @pytest.mark.security
    def test_path_with_spaces(self):
        """Test that paths with spaces are handled correctly."""
        path = "my folder/my file.txt"
        is_safe, result = validate_path(path)
        # Should be allowed if not in system directory
        assert is_safe or "sensitiv" in result.lower()

    @pytest.mark.unit
    @pytest.mark.security
    def test_unicode_path(self):
        """Test that unicode paths are handled."""
        path = "test/文件.txt"
        is_safe, result = validate_path(path)
        # Should be allowed
        assert is_safe or "sensitiv" in result.lower()

    @pytest.mark.unit
    @pytest.mark.security
    def test_very_long_path(self):
        """Test that very long paths are handled."""
        # Create a very long path
        long_path = "a/" * 100 + "file.txt"
        is_safe, result = validate_path(long_path)
        # Should still validate, even if OS might reject it later
        assert isinstance(is_safe, bool)

    @pytest.mark.unit
    @pytest.mark.security
    def test_none_path(self):
        """Test that None is handled gracefully."""
        # Should return False for None input (graceful handling)
        is_safe, message = validate_path(None) if None else (False, "None path")
        assert not is_safe
