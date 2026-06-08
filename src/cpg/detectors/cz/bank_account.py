import re
from typing import Any

from cpg.detectors.base import Detector
from cpg.models import Finding


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
                metadata = self._extract_metadata(account_part, bank_code)
                
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
        from cpg.validators.bank_account import validate_bank_account
        
        is_valid, error = validate_bank_account(value)
        return is_valid

    def _extract_metadata(self, account: str, bank_code: str) -> dict[str, Any]:
        from cpg.validators.bank_account import parse_bank_account
        
        metadata: dict[str, Any] = {
            "bank_code": bank_code
        }
        
        parsed = parse_bank_account(f"{account}/{bank_code}")
        if parsed:
            if parsed[0]:
                metadata["prefix"] = parsed[0]
            metadata["base"] = parsed[1]
        
        return metadata