from typing import cast

from fastpii import FastPII, DEFAULT_PRIORITY, DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries import get_country_pack


__all__ = ["MCPServer"]


class MCPServer:
    engine: FastPII

    def __init__(self, engine: FastPII) -> None:
        self.engine = engine

    @classmethod
    def from_regions(cls, regions: list[str]) -> "MCPServer":
        scorer = ConfidenceScorer(
            base_scores=DEFAULT_CONFIDENCE_SCORES,
            context_boost=DEFAULT_CONTEXT_BOOST,
        )
        engine = FastPII(priority=DEFAULT_PRIORITY, confidence_scorer=scorer)
        for region_code in regions:
            pack_cls = get_country_pack(region_code)
            if pack_cls is not None:
                engine.register(pack_cls())
        return cls(engine=engine)

    def list_tools(self) -> list[dict[str, object]]:
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
                        }
                    },
                    "required": ["value", "detector_name"]
                }
            },
            {
                "name": "list_detectors",
                "description": "List all available PII detectors for the configured regions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    def call_tool(self, name: str, arguments: dict[str, object]) -> dict[str, object]:
        if name == "detect_pii":
            return self._handle_detect_pii(arguments)
        elif name == "validate_identifier":
            return self._handle_validate_identifier(arguments)
        elif name == "list_detectors":
            return self._handle_list_detectors(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    def _handle_detect_pii(self, arguments: dict[str, object]) -> dict[str, object]:
        text = arguments.get("text")
        detector_names = arguments.get("detector_names")
        detector_list: list[str] | None = None
        if isinstance(detector_names, list):
            detector_names_list = cast(list[object], detector_names)
            if all(isinstance(item, str) for item in detector_names_list):
                detector_list = [item for item in detector_names_list if isinstance(item, str)]

        if not isinstance(text, str) or not text:
            return {"error": "Missing required parameter: text"}

        result = self.engine.detect(text, detector_names=detector_list)

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

    def _handle_validate_identifier(self, arguments: dict[str, object]) -> dict[str, object]:
        value = arguments.get("value")
        detector_name = arguments.get("detector_name")

        if not isinstance(value, str) or not value:
            return {"error": "Missing required parameter: value"}
        if not isinstance(detector_name, str) or not detector_name:
            return {"error": "Missing required parameter: detector_name"}

        try:
            result = self.engine.validate(value, detector_name=detector_name)
            return {
                "detector": result.detector,
                "value": result.value,
                "is_valid": result.is_valid,
                "metadata": result.metadata
            }
        except KeyError:
            return {
                "error": f"Detector '{detector_name}' not found",
                "available_detectors": [d.name for d in self.engine.list_detectors()]
            }

    def _handle_list_detectors(self, arguments: dict[str, object]) -> dict[str, object]:
        _ = arguments
        detectors = self.engine.list_detectors()

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
