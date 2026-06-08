import re
from typing import Any

from fastpii.detectors.base import Detector
from fastpii.models import Finding


class DICDetector(Detector):
    def __init__(self) -> None:
        super().__init__(
            name="dic",
            region="cz",
            description="Czech VAT number (DIČ) detector"
        )

    def detect(self, text: str) -> list[Finding]:
        pattern = r'\bCZ(\d{8,10})\b'
        findings: list[Finding] = []

        for match in re.finditer(pattern, text):
            value = match.group(1)
            
            is_valid = self.validate(value)
            
            if is_valid:
                metadata = self._extract_metadata(value)
                
                findings.append(Finding(
                    type="dic",
                    value=f"CZ{value}",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95,
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
        return validate_ico(value)

    def _validate_birth_number_format(self, value: str) -> bool:
        from fastpii.validators.birth_number import validate_birth_number
        result = validate_birth_number(value)
        return result.get("valid", False)

    def _extract_metadata(self, value: str) -> dict[str, Any]:
        metadata: dict[str, Any] = {}
        
        if len(value) == 8:
            metadata["type"] = "company"
        elif len(value) == 9:
            metadata["type"] = "special"
        elif len(value) == 10:
            metadata["type"] = "individual"
        
        return metadata