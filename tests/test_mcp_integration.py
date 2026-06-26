import pytest

from fastpii import FastPII, DEFAULT_PRIORITY, DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.cz import CzechPack
from fastpii.integrations.mcp import MCPServer


@pytest.fixture
def engine():
    scorer = ConfidenceScorer(
        base_scores=DEFAULT_CONFIDENCE_SCORES,
        context_boost=DEFAULT_CONTEXT_BOOST,
    )
    eng = FastPII(priority=DEFAULT_PRIORITY, confidence_scorer=scorer)
    eng.register(CzechPack())
    return eng


class TestMCPServerWithEngine:
    def test_list_tools(self, engine):
        mcp = MCPServer(engine=engine)
        tools = mcp.list_tools()

        assert isinstance(tools, list)
        assert len(tools) == 3

        tool_names = {t["name"] for t in tools}
        assert "detect_pii" in tool_names
        assert "validate_identifier" in tool_names
        assert "list_detectors" in tool_names

    def test_call_tool_detect_pii(self, engine):
        mcp = MCPServer(engine=engine)

        result = mcp.call_tool("detect_pii", {
            "text": "Jan Novák, RČ: 8001011238",
        })

        assert "findings" in result
        assert len(result["findings"]) >= 1
        types = [f["type"] for f in result["findings"]]
        assert "rodne_cislo" in types

    def test_call_tool_detect_pii_with_detector_names(self, engine):
        mcp = MCPServer(engine=engine)

        result = mcp.call_tool("detect_pii", {
            "text": "IČO: 25596641, RČ: 8001011238",
            "detector_names": ["ico"]
        })

        assert len(result["findings"]) >= 1
        assert all(f["type"] == "ico" for f in result["findings"])

    def test_call_tool_validate_identifier(self, engine):
        mcp = MCPServer(engine=engine)

        result = mcp.call_tool("validate_identifier", {
            "value": "8001011238",
            "detector_name": "rodne_cislo",
        })

        assert result["is_valid"] is True
        assert "birth_date" in result["metadata"]
        assert "gender" in result["metadata"]

    def test_call_tool_validate_identifier_invalid(self, engine):
        mcp = MCPServer(engine=engine)

        result = mcp.call_tool("validate_identifier", {
            "value": "invalid_identifier",
            "detector_name": "rodne_cislo",
        })

        assert result["is_valid"] is False

    def test_call_tool_validate_identifier_nonexistent_detector(self, engine):
        mcp = MCPServer(engine=engine)

        result = mcp.call_tool("validate_identifier", {
            "value": "8001011238",
            "detector_name": "nonexistent",
        })

        assert "error" in result
        assert "not found" in result["error"]
        assert "available_detectors" in result

    def test_call_tool_list_detectors(self, engine):
        mcp = MCPServer(engine=engine)

        result = mcp.call_tool("list_detectors", {})

        assert "detectors" in result
        assert isinstance(result["detectors"], list)
        assert len(result["detectors"]) >= 6

        detector_names = {d["name"] for d in result["detectors"]}
        assert "rodne_cislo" in detector_names

    def test_call_tool_unknown_tool(self, engine):
        mcp = MCPServer(engine=engine)

        with pytest.raises(ValueError, match="Unknown tool"):
            mcp.call_tool("unknown_tool", {})

    def test_metadata_extraction(self, engine):
        mcp = MCPServer(engine=engine)

        result = mcp.call_tool("detect_pii", {
            "text": "RČ: 8001011238",
        })

        finding = result["findings"][0]
        assert "metadata" in finding
        assert "birth_date" in finding["metadata"]
        assert "gender" in finding["metadata"]


class TestMCPServerFromRegions:
    def test_from_regions(self):
        mcp = MCPServer.from_regions(["cz"])

        result = mcp.call_tool("detect_pii", {
            "text": "RČ: 8001011238",
        })

        assert len(result["findings"]) >= 1

    def test_list_tools_from_regions(self):
        mcp = MCPServer.from_regions(["cz"])
        tools = mcp.list_tools()

        assert len(tools) == 3

    def test_detect_pii_error_handling_missing_text(self):
        mcp = MCPServer.from_regions(["cz"])

        result = mcp.call_tool("detect_pii", {})

        assert "error" in result
        assert "text" in result["error"]

    def test_validate_identifier_error_handling_missing_value(self):
        mcp = MCPServer.from_regions(["cz"])

        result = mcp.call_tool("validate_identifier", {
            "detector_name": "rodne_cislo",
        })

        assert "error" in result
        assert "value" in result["error"]

    def test_validate_identifier_error_handling_missing_detector(self):
        mcp = MCPServer.from_regions(["cz"])

        result = mcp.call_tool("validate_identifier", {
            "value": "8001011238",
        })

        assert "error" in result
        assert "detector_name" in result["error"]