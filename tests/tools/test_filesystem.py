#!/usr/bin/env python3
"""
Unit Tests for mistralcli.tools.filesystem

Tests all filesystem tool functions:
- read_file
- write_file
- rename_file
- copy_file
- move_file

Version: 1.5.2
"""

import pytest
from pathlib import Path
from mistralcli.tools.filesystem import (
    read_file,
    write_file,
    rename_file,
    copy_file,
    move_file,
)


# ============================================================================
# Test read_file
# ============================================================================

class TestReadFile:
    """Tests for read_file function."""

    @pytest.mark.unit
    def test_read_existing_file(self, sample_text_file):
        """Test reading an existing file."""
        result = read_file(str(sample_text_file))

        assert result["success"] is True
        assert "content" in result
        assert "Hello World" in result["content"]
        assert "test file" in result["content"]

    @pytest.mark.unit
    def test_read_nonexistent_file(self, temp_dir):
        """Test reading a file that doesn't exist."""
        nonexistent = temp_dir / "nonexistent.txt"
        result = read_file(str(nonexistent))

        assert result["success"] is False
        assert "error" in result
        assert "nicht gefunden" in result["error"].lower() or "not found" in result["error"].lower()

    @pytest.mark.unit
    @pytest.mark.security
    def test_read_system_file_blocked(self):
        """Test that reading system files is blocked."""
        result = read_file("/etc/passwd")

        assert result["success"] is False
        assert "error" in result
        # Should mention security/validation
        assert any(word in result["error"].lower() for word in ["validierung", "sensitiv", "validation", "sensitive"])

    @pytest.mark.unit
    @pytest.mark.security
    def test_read_path_traversal_blocked(self, temp_dir):
        """Test that path traversal is blocked."""
        result = read_file(str(temp_dir / "../../../etc/passwd"))

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.unit
    def test_read_empty_file(self, temp_dir):
        """Test reading an empty file."""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")

        result = read_file(str(empty_file))

        assert result["success"] is True
        assert result["content"] == ""

    @pytest.mark.unit
    def test_read_binary_file(self, temp_dir):
        """Test reading a binary file."""
        binary_file = temp_dir / "binary.dat"
        binary_file.write_bytes(b"\x00\x01\x02\x03")

        result = read_file(str(binary_file))

        # Should either succeed with encoded content or fail gracefully
        assert "success" in result
        if result["success"]:
            assert "content" in result
        else:
            assert "error" in result


# ============================================================================
# Test write_file
# ============================================================================

class TestWriteFile:
    """Tests for write_file function."""

    @pytest.mark.unit
    def test_write_new_file(self, temp_dir):
        """Test writing to a new file."""
        new_file = temp_dir / "new.txt"
        content = "New file content"

        result = write_file(str(new_file), content, auto_confirm=True)

        assert result["success"] is True
        assert new_file.exists()
        assert new_file.read_text() == content

    @pytest.mark.unit
    def test_overwrite_existing_file(self, sample_text_file):
        """Test overwriting an existing file."""
        new_content = "Overwritten content"

        result = write_file(str(sample_text_file), new_content, auto_confirm=True)

        assert result["success"] is True
        assert sample_text_file.read_text() == new_content

    @pytest.mark.unit
    @pytest.mark.security
    def test_write_system_file_blocked(self):
        """Test that writing to system files is blocked."""
        result = write_file("/etc/test", "content", auto_confirm=True)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.unit
    @pytest.mark.security
    def test_write_path_traversal_blocked(self, temp_dir):
        """Test that path traversal is blocked."""
        result = write_file(str(temp_dir / "../../../tmp/test"), "content", auto_confirm=True)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.unit
    def test_write_empty_content(self, temp_dir):
        """Test writing empty content."""
        empty_file = temp_dir / "empty.txt"

        result = write_file(str(empty_file), "", auto_confirm=True)

        assert result["success"] is True
        assert empty_file.read_text() == ""

    @pytest.mark.unit
    def test_write_unicode_content(self, temp_dir):
        """Test writing unicode content."""
        unicode_file = temp_dir / "unicode.txt"
        content = "Hello 世界 🌍"

        result = write_file(str(unicode_file), content, auto_confirm=True)

        assert result["success"] is True
        assert unicode_file.read_text(encoding='utf-8') == content

    @pytest.mark.unit
    def test_write_creates_parent_directory(self, temp_dir):
        """Test that parent directories are created if needed."""
        nested_file = temp_dir / "level1" / "level2" / "file.txt"

        result = write_file(str(nested_file), "content", auto_confirm=True)

        # Should either succeed (creating dirs) or fail with clear message
        assert "success" in result
        if result["success"]:
            assert nested_file.exists()


# ============================================================================
# Test rename_file
# ============================================================================

class TestRenameFile:
    """Tests for rename_file function."""

    @pytest.mark.unit
    def test_rename_file(self, sample_text_file):
        """Test renaming a file."""
        new_name = sample_text_file.parent / "renamed.txt"
        original_content = sample_text_file.read_text()

        result = rename_file(str(sample_text_file), str(new_name), auto_confirm=True)

        assert result["success"] is True
        assert not sample_text_file.exists()
        assert new_name.exists()
        assert new_name.read_text() == original_content

    @pytest.mark.unit
    def test_rename_nonexistent_file(self, temp_dir):
        """Test renaming a file that doesn't exist."""
        nonexistent = temp_dir / "nonexistent.txt"
        new_name = temp_dir / "new.txt"

        result = rename_file(str(nonexistent), str(new_name), auto_confirm=True)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.unit
    def test_rename_to_existing_file(self, temp_dir):
        """Test renaming to a name that already exists."""
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file1.write_text("File 1")
        file2.write_text("File 2")

        result = rename_file(str(file1), str(file2), auto_confirm=True)

        # Should either fail or warn about overwriting
        if result["success"]:
            # If it succeeds, file2 should have file1's content
            assert file2.read_text() == "File 1"
        else:
            assert "error" in result

    @pytest.mark.unit
    @pytest.mark.security
    def test_rename_system_file_blocked(self, temp_dir):
        """Test that renaming system files is blocked."""
        safe_file = temp_dir / "safe.txt"
        safe_file.write_text("content")

        result = rename_file(str(safe_file), "/etc/test", auto_confirm=True)

        assert result["success"] is False
        assert "error" in result


# ============================================================================
# Test copy_file
# ============================================================================

class TestCopyFile:
    """Tests for copy_file function."""

    @pytest.mark.unit
    def test_copy_file(self, sample_text_file, temp_dir):
        """Test copying a file."""
        destination = temp_dir / "copied.txt"

        result = copy_file(str(sample_text_file), str(destination), auto_confirm=True)

        assert result["success"] is True
        assert sample_text_file.exists()  # Original still exists
        assert destination.exists()
        assert destination.read_text() == sample_text_file.read_text()

    @pytest.mark.unit
    def test_copy_nonexistent_file(self, temp_dir):
        """Test copying a file that doesn't exist."""
        nonexistent = temp_dir / "nonexistent.txt"
        destination = temp_dir / "copy.txt"

        result = copy_file(str(nonexistent), str(destination), auto_confirm=True)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.unit
    def test_copy_directory(self, temp_dir):
        """Test copying a directory."""
        source_dir = temp_dir / "source_dir"
        dest_dir = temp_dir / "dest_dir"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")

        result = copy_file(str(source_dir), str(dest_dir), auto_confirm=True)

        # Should succeed and copy directory recursively
        if result["success"]:
            assert dest_dir.exists()
            assert (dest_dir / "file.txt").exists()

    @pytest.mark.unit
    @pytest.mark.security
    def test_copy_to_system_location_blocked(self, sample_text_file):
        """Test that copying to system locations is blocked."""
        result = copy_file(str(sample_text_file), "/etc/test", auto_confirm=True)

        assert result["success"] is False
        assert "error" in result


# ============================================================================
# Test move_file
# ============================================================================

class TestMoveFile:
    """Tests for move_file function."""

    @pytest.mark.unit
    def test_move_file(self, sample_text_file, temp_dir):
        """Test moving a file."""
        destination = temp_dir / "moved.txt"
        original_content = sample_text_file.read_text()

        result = move_file(str(sample_text_file), str(destination), auto_confirm=True)

        assert result["success"] is True
        assert not sample_text_file.exists()  # Original moved
        assert destination.exists()
        assert destination.read_text() == original_content

    @pytest.mark.unit
    def test_move_nonexistent_file(self, temp_dir):
        """Test moving a file that doesn't exist."""
        nonexistent = temp_dir / "nonexistent.txt"
        destination = temp_dir / "moved.txt"

        result = move_file(str(nonexistent), str(destination), auto_confirm=True)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.unit
    def test_move_to_different_directory(self, sample_text_file, temp_dir):
        """Test moving to a different directory."""
        new_dir = temp_dir / "new_directory"
        new_dir.mkdir()
        destination = new_dir / "moved.txt"
        original_content = sample_text_file.read_text()

        result = move_file(str(sample_text_file), str(destination), auto_confirm=True)

        assert result["success"] is True
        assert destination.read_text() == original_content

    @pytest.mark.unit
    @pytest.mark.security
    def test_move_to_system_location_blocked(self, sample_text_file):
        """Test that moving to system locations is blocked."""
        result = move_file(str(sample_text_file), "/etc/test", auto_confirm=True)

        assert result["success"] is False
        assert "error" in result


# ============================================================================
# Test Error Handling
# ============================================================================

class TestErrorHandling:
    """Tests for error handling in filesystem tools."""

    @pytest.mark.unit
    def test_invalid_path_characters(self, temp_dir):
        """Test handling of invalid path characters."""
        # Null bytes are invalid in paths
        invalid_path = temp_dir / "file\x00.txt"

        result = write_file(str(invalid_path), "content", auto_confirm=True)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.unit
    def test_permission_denied(self, temp_dir):
        """Test handling of permission denied errors."""
        # Create a file and make it read-only
        readonly_file = temp_dir / "readonly.txt"
        readonly_file.write_text("original")
        readonly_file.chmod(0o444)

        result = write_file(str(readonly_file), "new content", auto_confirm=True)

        # Should fail with permission error
        # Note: This might succeed on some systems/filesystems
        if not result["success"]:
            assert "error" in result
            # Permission error might be mentioned
