import re
from typing import Any

from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class DICDetector(Detector):
    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="dic",
            region="cz",
            description="Czech VAT number (DIČ) detector"
        )
        # Use shared registry if none provided (singleton pattern)
        self.registry = registry or get_shared_registry()

    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("dic", "cz")
        if not patterns:
            return []
        
        pattern_def = patterns[0]  # Use the standard pattern
        findings: list[Finding] = []

        for match in pattern_def.compiled.finditer(text):
            value = match.group(1)
            
            is_valid = self.validate(value)
            
            if is_valid:
                metadata = self._extract_metadata(value)
                
                findings.append(Finding(
                    type="dic",
                    value=f"CZ{value}",
                    start=match.start(),
                    end=match.end(),
                    confidence=pattern_def.score,
                    region="cz",
                    metadata=metadata
                ))

        return findings

    def validate(self, value: str) -> bool:
        if value.startswith("CZ"):
            value = value[2:]
        
        if len(value) == 8:
            return self._validate_ico_format(value)
        elif len(value) == 9:
            return value[0] == "6"
        elif len(value) == 10:
            return self._validate_birth_number_format(value)
        
        return False

    def _validate_ico_format(self, value: str) -> bool:
        from fastpii.validators.ico_validator import validate_ico
        is_valid, _ = validate_ico(value)
        return is_valid

    def _validate_birth_number_format(self, value: str) -> bool:
        from fastpii.validators.birth_number import validate_birth_number_format
        is_valid, _, _ = validate_birth_number_format(value)
        return is_valid

    def _extract_metadata(self, value: str) -> dict[str, Any]:
        metadata: dict[str, Any] = {}
        
        if len(value) == 8:
            metadata["type"] = "company"
        elif len(value) == 9:
            metadata["type"] = "special"
        elif len(value) == 10:
            metadata["type"] = "individual"
        
        return metadata