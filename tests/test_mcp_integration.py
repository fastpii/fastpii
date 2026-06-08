import pytest

from fastpii.integrations.mcp import MCPServer


class TestMCPIntegration:
    def test_list_tools(self):
        mcp = MCPServer(regions=["cz"])
        tools = mcp.list_tools()
        
        assert isinstance(tools, list)
        assert len(tools) == 3
        
        tool_names = {t["name"] for t in tools}
        assert "detect_pii" in tool_names
        assert "validate_identifier" in tool_names
        assert "list_detectors" in tool_names

    def test_tool_schema_detect_pii(self):
        mcp = MCPServer(regions=["cz"])
        tools = mcp.list_tools()
        
        detect_tool = next(t for t in tools if t["name"] == "detect_pii")
        
        assert "description" in detect_tool
        assert "inputSchema" in detect_tool
        assert detect_tool["inputSchema"]["type"] == "object"
        assert "text" in detect_tool["inputSchema"]["properties"]
        assert "regions" in detect_tool["inputSchema"]["properties"]

    def test_call_tool_detect_pii(self):
        mcp = MCPServer(regions=["cz"])
        
        result = mcp.call_tool("detect_pii", {
            "text": "Jan Novák, RČ: 8001011234",
            "regions": ["cz"]
        })
        
        assert "findings" in result
        assert len(result["findings"]) >= 1
        assert result["findings"][0]["type"] == "rodne_cislo"

    def test_call_tool_detect_pii_with_detector_names(self):
        mcp = MCPServer(regions=["cz"])
        
        result = mcp.call_tool("detect_pii", {
            "text": "IČO: 25596641, RČ: 8001011234",
            "regions": ["cz"],
            "detector_names": ["ico"]
        })
        
        assert len(result["findings"]) >= 1
        assert all(f["type"] == "ico" for f in result["findings"])

    def test_call_tool_validate_identifier(self):
        mcp = MCPServer(regions=["cz"])
        
        result = mcp.call_tool("validate_identifier", {
            "value": "8001011234",
            "detector_name": "rodne_cislo",
            "regions": ["cz"]
        })
        
        assert result["is_valid"] is True
        assert "birth_date" in result["metadata"]
        assert "gender" in result["metadata"]

    def test_call_tool_validate_identifier_invalid(self):
        mcp = MCPServer(regions=["cz"])
        
        result = mcp.call_tool("validate_identifier", {
            "value": "invalid_identifier",
            "detector_name": "rodne_cislo",
            "regions": ["cz"]
        })
        
        assert result["is_valid"] is False

    def test_call_tool_validate_identifier_nonexistent_detector(self):
        mcp = MCPServer(regions=["cz"])
        
        result = mcp.call_tool("validate_identifier", {
            "value": "8001011234",
            "detector_name": "nonexistent",
            "regions": ["cz"]
        })
        
        assert "error" in result
        assert "not found" in result["error"]
        assert "available_detectors" in result

    def test_call_tool_list_detectors(self):
        mcp = MCPServer(regions=["cz"])
        
        result = mcp.call_tool("list_detectors", {
            "regions": ["cz"]
        })
        
        assert "detectors" in result
        assert isinstance(result["detectors"], list)
        assert len(result["detectors"]) >= 6
        
        detector_names = {d["name"] for d in result["detectors"]}
        assert "rodne_cislo" in detector_names

    def test_call_tool_unknown_tool(self):
        mcp = MCPServer(regions=["cz"])
        
        with pytest.raises(ValueError, match="Unknown tool"):
            mcp.call_tool("unknown_tool", {})

    def test_multiple_regions(self):
        mcp = MCPServer(regions=["cz"])
        
        result = mcp.call_tool("detect_pii", {
            "text": "RČ: 8001011234",
            "regions": ["cz"]
        })
        
        assert len(result["findings"]) >= 1

    def test_detect_pii_error_handling_missing_text(self):
        mcp = MCPServer(regions=["cz"])
        
        result = mcp.call_tool("detect_pii", {
            "regions": ["cz"]
        })
        
        assert "error" in result
        assert "text" in result["error"]

    def test_validate_identifier_error_handling_missing_value(self):
        mcp = MCPServer(regions=["cz"])
        
        result = mcp.call_tool("validate_identifier", {
            "detector_name": "rodne_cislo",
            "regions": ["cz"]
        })
        
        assert "error" in result
        assert "value" in result["error"]

    def test_validate_identifier_error_handling_missing_detector(self):
        mcp = MCPServer(regions=["cz"])
        
        result = mcp.call_tool("validate_identifier", {
            "value": "8001011234",
            "regions": ["cz"]
        })
        
        assert "error" in result
        assert "detector_name" in result["error"]

    def test_metadata_extraction(self):
        mcp = MCPServer(regions=["cz"])
        
        result = mcp.call_tool("detect_pii", {
            "text": "RČ: 8001011234",
            "regions": ["cz"]
        })
        
        finding = result["findings"][0]
        assert "metadata" in finding
        assert "birth_date" in finding["metadata"]
        assert "gender" in finding["metadata"]