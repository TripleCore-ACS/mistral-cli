#!/usr/bin/env python3
"""
Unit Tests for mistralcli.tools.definitions

Tests the TOOLS array and tool definitions for:
- Correct structure
- Required fields
- Valid JSON schemas
- Complete tool coverage

Version: 1.5.2
"""

import pytest
import json
from mistralcli.tools.definitions import TOOLS


# ============================================================================
# Test TOOLS Array Structure
# ============================================================================

class TestToolsArrayStructure:
    """Tests for the TOOLS array structure."""

    @pytest.mark.unit
    def test_tools_is_list(self):
        """Test that TOOLS is a list."""
        assert isinstance(TOOLS, list)

    @pytest.mark.unit
    def test_tools_not_empty(self):
        """Test that TOOLS contains tool definitions."""
        assert len(TOOLS) > 0

    @pytest.mark.unit
    def test_tools_count(self):
        """Test that we have all 14 tools."""
        assert len(TOOLS) == 14, f"Expected 14 tools, found {len(TOOLS)}"


# ============================================================================
# Test Individual Tool Definitions
# ============================================================================

class TestToolDefinitions:
    """Tests for individual tool definitions."""

    @pytest.mark.unit
    @pytest.mark.parametrize("tool_index", range(14))
    def test_tool_has_type(self, tool_index):
        """Test that each tool has a 'type' field."""
        tool = TOOLS[tool_index]
        assert "type" in tool
        assert tool["type"] == "function"

    @pytest.mark.unit
    @pytest.mark.parametrize("tool_index", range(14))
    def test_tool_has_function(self, tool_index):
        """Test that each tool has a 'function' field."""
        tool = TOOLS[tool_index]
        assert "function" in tool
        assert isinstance(tool["function"], dict)

    @pytest.mark.unit
    @pytest.mark.parametrize("tool_index", range(14))
    def test_tool_has_name(self, tool_index):
        """Test that each tool has a name."""
        tool = TOOLS[tool_index]
        assert "name" in tool["function"]
        assert isinstance(tool["function"]["name"], str)
        assert len(tool["function"]["name"]) > 0

    @pytest.mark.unit
    @pytest.mark.parametrize("tool_index", range(14))
    def test_tool_has_description(self, tool_index):
        """Test that each tool has a description."""
        tool = TOOLS[tool_index]
        assert "description" in tool["function"]
        assert isinstance(tool["function"]["description"], str)
        assert len(tool["function"]["description"]) > 10  # Meaningful description

    @pytest.mark.unit
    @pytest.mark.parametrize("tool_index", range(14))
    def test_tool_has_parameters(self, tool_index):
        """Test that each tool has parameters definition."""
        tool = TOOLS[tool_index]
        assert "parameters" in tool["function"]
        assert isinstance(tool["function"]["parameters"], dict)


# ============================================================================
# Test Tool Names
# ============================================================================

class TestToolNames:
    """Tests for tool names."""

    EXPECTED_TOOLS = [
        "execute_bash_command",
        "read_file",
        "write_file",
        "fetch_url",
        "download_file",
        "search_web",
        "rename_file",
        "copy_file",
        "move_file",
        "parse_json",
        "parse_csv",
        "upload_ftp",
        "get_image_info",
        "upload_sftp",
    ]

    @pytest.mark.unit
    def test_all_expected_tools_present(self):
        """Test that all expected tools are present."""
        tool_names = [tool["function"]["name"] for tool in TOOLS]

        for expected_name in self.EXPECTED_TOOLS:
            assert expected_name in tool_names, f"Tool '{expected_name}' not found in TOOLS"

    @pytest.mark.unit
    def test_no_duplicate_tool_names(self):
        """Test that there are no duplicate tool names."""
        tool_names = [tool["function"]["name"] for tool in TOOLS]
        assert len(tool_names) == len(set(tool_names)), "Duplicate tool names found"

    @pytest.mark.unit
    def test_tool_names_follow_convention(self):
        """Test that tool names follow snake_case convention."""
        tool_names = [tool["function"]["name"] for tool in TOOLS]

        for name in tool_names:
            # Should be snake_case (lowercase with underscores)
            assert name.islower() or '_' in name, f"Tool name '{name}' doesn't follow snake_case"
            assert ' ' not in name, f"Tool name '{name}' contains spaces"
            assert name.replace('_', '').isalnum(), f"Tool name '{name}' contains invalid characters"


# ============================================================================
# Test Parameter Schemas
# ============================================================================

class TestParameterSchemas:
    """Tests for parameter JSON schemas."""

    @pytest.mark.unit
    @pytest.mark.parametrize("tool_index", range(14))
    def test_parameters_has_type(self, tool_index):
        """Test that parameters have a type field."""
        tool = TOOLS[tool_index]
        params = tool["function"]["parameters"]

        assert "type" in params
        assert params["type"] == "object"

    @pytest.mark.unit
    @pytest.mark.parametrize("tool_index", range(14))
    def test_parameters_has_properties(self, tool_index):
        """Test that parameters have properties."""
        tool = TOOLS[tool_index]
        params = tool["function"]["parameters"]

        assert "properties" in params
        assert isinstance(params["properties"], dict)
        assert len(params["properties"]) > 0  # At least one parameter

    @pytest.mark.unit
    @pytest.mark.parametrize("tool_index", range(14))
    def test_parameters_has_required(self, tool_index):
        """Test that parameters have required field."""
        tool = TOOLS[tool_index]
        params = tool["function"]["parameters"]

        assert "required" in params
        assert isinstance(params["required"], list)

    @pytest.mark.unit
    @pytest.mark.parametrize("tool_index", range(14))
    def test_required_params_in_properties(self, tool_index):
        """Test that required parameters are defined in properties."""
        tool = TOOLS[tool_index]
        params = tool["function"]["parameters"]
        properties = params["properties"]
        required = params["required"]

        for req_param in required:
            assert req_param in properties, \
                f"Required param '{req_param}' not in properties for tool {tool['function']['name']}"


# ============================================================================
# Test Specific Tools
# ============================================================================

class TestSpecificTools:
    """Tests for specific tool definitions."""

    @pytest.mark.unit
    def test_execute_bash_command_tool(self):
        """Test execute_bash_command tool definition."""
        tool = next(t for t in TOOLS if t["function"]["name"] == "execute_bash_command")

        # Should have command and explanation parameters
        params = tool["function"]["parameters"]["properties"]
        assert "command" in params
        assert "explanation" in params

        # Both should be required
        required = tool["function"]["parameters"]["required"]
        assert "command" in required
        assert "explanation" in required

    @pytest.mark.unit
    def test_read_file_tool(self):
        """Test read_file tool definition."""
        tool = next(t for t in TOOLS if t["function"]["name"] == "read_file")

        # Should have file_path parameter
        params = tool["function"]["parameters"]["properties"]
        assert "file_path" in params

        # Should be required
        required = tool["function"]["parameters"]["required"]
        assert "file_path" in required

    @pytest.mark.unit
    def test_write_file_tool(self):
        """Test write_file tool definition."""
        tool = next(t for t in TOOLS if t["function"]["name"] == "write_file")

        # Should have file_path and content parameters
        params = tool["function"]["parameters"]["properties"]
        assert "file_path" in params
        assert "content" in params

        # Both should be required
        required = tool["function"]["parameters"]["required"]
        assert "file_path" in required
        assert "content" in required

    @pytest.mark.unit
    def test_fetch_url_tool(self):
        """Test fetch_url tool definition."""
        tool = next(t for t in TOOLS if t["function"]["name"] == "fetch_url")

        # Should have url parameter
        params = tool["function"]["parameters"]["properties"]
        assert "url" in params

        # Should have method parameter with enum
        assert "method" in params
        method_param = params["method"]
        if "enum" in method_param:
            assert "GET" in method_param["enum"]
            assert "POST" in method_param["enum"]

    @pytest.mark.unit
    def test_upload_sftp_tool(self):
        """Test upload_sftp tool definition."""
        tool = next(t for t in TOOLS if t["function"]["name"] == "upload_sftp")

        params = tool["function"]["parameters"]["properties"]

        # Should have all SFTP parameters
        assert "local_file" in params
        assert "host" in params
        assert "port" in params
        assert "username" in params
        assert "password" in params
        assert "key_path" in params
        assert "remote_path" in params

        # Check defaults
        if "default" in params["port"]:
            assert params["port"]["default"] == 22


# ============================================================================
# Test JSON Validity
# ============================================================================

class TestJSONValidity:
    """Tests for JSON schema validity."""

    @pytest.mark.unit
    def test_tools_array_is_json_serializable(self):
        """Test that TOOLS array can be serialized to JSON."""
        try:
            json_str = json.dumps(TOOLS)
            assert len(json_str) > 0
        except (TypeError, ValueError) as e:
            pytest.fail(f"TOOLS array is not JSON serializable: {e}")

    @pytest.mark.unit
    def test_tools_array_can_be_deserialized(self):
        """Test that serialized TOOLS can be deserialized."""
        json_str = json.dumps(TOOLS)
        deserialized = json.loads(json_str)

        assert len(deserialized) == len(TOOLS)
        assert deserialized == TOOLS


# ============================================================================
# Test Documentation Quality
# ============================================================================

class TestDocumentationQuality:
    """Tests for quality of tool documentation."""

    @pytest.mark.unit
    @pytest.mark.parametrize("tool_index", range(14))
    def test_description_mentions_security_where_applicable(self, tool_index):
        """Test that security notes are mentioned where applicable."""
        tool = TOOLS[tool_index]
        name = tool["function"]["name"]
        description = tool["function"]["description"]

        # These tools should mention security constraints
        security_sensitive_tools = [
            "execute_bash_command",
            "read_file",
            "write_file",
            "fetch_url",
            "download_file",
        ]

        if name in security_sensitive_tools:
            # Should mention some security aspect
            security_keywords = ["HINWEIS", "blockiert", "restricted", "not allowed", "eingeschränkt"]
            has_security_note = any(keyword in description for keyword in security_keywords)
            assert has_security_note, f"Tool '{name}' should mention security constraints in description"

    @pytest.mark.unit
    @pytest.mark.parametrize("tool_index", range(14))
    def test_parameter_descriptions_exist(self, tool_index):
        """Test that parameters have descriptions."""
        tool = TOOLS[tool_index]
        params = tool["function"]["parameters"]["properties"]

        for param_name, param_def in params.items():
            assert "description" in param_def, \
                f"Parameter '{param_name}' in tool '{tool['function']['name']}' lacks description"
            assert isinstance(param_def["description"], str)
            assert len(param_def["description"]) > 0
