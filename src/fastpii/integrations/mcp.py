from typing import Any

from fastpii import PrivacyGuard


class MCPServer:
    def __init__(self, regions: list[str] | None = None):
        self.gateway = PrivacyGuard(regions=regions or ["cz"])

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "detect_pii",
                "description": "Detect PII (Personally Identifiable Information) in text. Returns list of detected identifiers with type, value, position, and confidence.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to analyze for PII"
                        },
                        "regions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Region codes for detectors (e.g., ['cz'])",
                            "default": ["cz"]
                        },
                        "detector_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific detectors to use (optional)",
                            "default": None
                        }
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "validate_identifier",
                "description": "Validate a specific identifier (e.g., Czech birth number, company ID). Returns validation result with metadata.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "value": {
                            "type": "string",
                            "description": "Value to validate"
                        },
                        "detector_name": {
                            "type": "string",
                            "description": "Detector name (e.g., 'rodne_cislo', 'ico', 'dic')"
                        },
                        "regions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Region codes for detectors (e.g., ['cz'])",
                            "default": ["cz"]
                        }
                    },
                    "required": ["value", "detector_name"]
                }
            },
            {
                "name": "list_detectors",
                "description": "List all available PII detectors for enabled regions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "regions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Region codes (e.g., ['cz'])",
                            "default": ["cz"]
                        }
                    },
                    "required": []
                }
            }
        ]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "detect_pii":
            return self._handle_detect_pii(arguments)
        elif name == "validate_identifier":
            return self._handle_validate_identifier(arguments)
        elif name == "list_detectors":
            return self._handle_list_detectors(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    def _handle_detect_pii(self, arguments: dict[str, Any]) -> dict[str, Any]:
        text = arguments.get("text")
        regions = arguments.get("regions", ["cz"])
        detector_names = arguments.get("detector_names")
        
        if not text:
            return {"error": "Missing required parameter: text"}
        
        result = self.gateway.detect(text, detector_names=detector_names)
        
        return {
            "text": result.text,
            "findings": [
                {
                    "type": f.type,
                    "value": f.value,
                    "start": f.start,
                    "end": f.end,
                    "confidence": f.confidence,
                    "region": f.region,
                    "metadata": f.metadata
                }
                for f in result.findings
            ],
            "detector_names": result.detector_names,
            "processing_time_ms": result.processing_time_ms
        }

    def _handle_validate_identifier(self, arguments: dict[str, Any]) -> dict[str, Any]:
        value = arguments.get("value")
        detector_name = arguments.get("detector_name")
        regions = arguments.get("regions", ["cz"])
        
        if not value:
            return {"error": "Missing required parameter: value"}
        if not detector_name:
            return {"error": "Missing required parameter: detector_name"}
        
        try:
            result = self.gateway.validate(value, detector_name=detector_name)
            return {
                "detector": result.detector,
                "value": result.value,
                "is_valid": result.is_valid,
                "metadata": result.metadata
            }
        except KeyError:
            return {
                "error": f"Detector '{detector_name}' not found",
                "available_detectors": [d.name for d in self.gateway.list_detectors()]
            }

    def _handle_list_detectors(self, arguments: dict[str, Any]) -> dict[str, Any]:
        regions = arguments.get("regions", ["cz"])
        detectors = self.gateway.list_detectors()
        
        return {
            "detectors": [
                {
                    "name": d.name,
                    "region": d.region,
                    "description": d.description
                }
                for d in detectors
            ]
        }