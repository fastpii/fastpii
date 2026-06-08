import re
from typing import Any

from fastpii.detectors.base import Detector
from fastpii.models import Finding


class BankAccountDetector(Detector):
    def __init__(self) -> None:
        super().__init__(
            name="bank_account",
            region="cz",
            description="Czech bank account number detector with MOD11 checksum validation"
        )

    def detect(self, text: str) -> list[Finding]:
        pattern = r'\b(\d{1,6}-?\d{1,10})/(\d{4})\b'
        findings: list[Finding] = []

        for match in re.finditer(pattern, text):
            account_part = match.group(1)
            bank_code = match.group(2)
            full_value = f"{account_part}/{bank_code}"
            
            is_valid = self.validate(full_value)
            
            if is_valid:
                metadata = self._extract_metadata(full_value)
                
                findings.append(Finding(
                    type="bank_account",
                    value=full_value,
                    start=match.start(),
                    end=match.end(),
                    confidence=1.0,
                    region="cz",
                    metadata=metadata
                ))

        return findings

    def validate(self, value: str) -> bool:
        from fastpii.validators.bank_account import validate_bank_account
        
        is_valid, error = validate_bank_account(value)
        return is_valid

    def _extract_metadata(self, value: str) -> dict[str, Any]:
        from fastpii.validators.bank_account import parse_bank_account
        
        # Parse the full account number (format: prefix-base/bank_code or base/bank_code)
        match = re.match(r'(\d{1,6}-)?(\d{1,10})/(\d{4})', value)
        if not match:
            return {"bank_code": ""}
        
        prefix = match.group(1).rstrip('-') if match.group(1) else None
        base = match.group(2)
        bank_code = match.group(3)
        
        metadata: dict[str, Any] = {
            "bank_code": bank_code,
            "base": base
        }
        
        if prefix:
            metadata["prefix"] = prefix
        
        return metadata