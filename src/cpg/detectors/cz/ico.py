import re
from typing import Any

from cpg.detectors.base import Detector
from cpg.models import Finding


class ICODetector(Detector):
    def __init__(self) -> None:
        super().__init__(
            name="ico",
            region="cz",
            description="Czech company ID (IČO) detector with checksum validation"
        )

    def detect(self, text: str) -> list[Finding]:
        pattern = r'\b(\d{8})\b'
        findings: list[Finding] = []

        for match in re.finditer(pattern, text):
            value = match.group(1)
            
            is_valid = self.validate(value)
            
            if is_valid:
                metadata = self._extract_metadata(value)
                
                findings.append(Finding(
                    type="ico",
                    value=value,
                    start=match.start(),
                    end=match.end(),
                    confidence=1.0,
                    region="cz",
                    metadata=metadata
                ))

        return findings

    def validate(self, value: str) -> bool:
        cleaned = value.replace('/', '').replace(' ', '')
        
        if len(cleaned) != 8:
            return False
        
        if not cleaned.isdigit():
            return False
        
        return self._validate_checksum(cleaned)

    def _validate_checksum(self, ico: str) -> bool:
        try:
            weights = [8, 7, 6, 5, 4, 3, 2]
            
            total = sum(int(ico[i]) * weights[i] for i in range(7))
            
            remainder = total % 11
            
            if remainder == 0:
                expected_check = 1
            elif remainder == 1:
                expected_check = 0
            else:
                expected_check = 11 - remainder
            
            return int(ico[7]) == expected_check
        except (ValueError, IndexError):
            return False

    def _extract_metadata(self, ico: str) -> dict[str, Any]:
        return {
            "checksum_valid": self._validate_checksum(ico)
        }