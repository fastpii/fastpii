from typing import TYPE_CHECKING, ClassVar

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry

if TYPE_CHECKING:
    from fastpii.countries.cz.data.bank_codes import CzechBankCodesData


class BankAccountDetector(Detector):
    registry: PatternRegistry
    EMPTY_BANK_NAME: ClassVar[str] = ""
    bank_codes_data: "CzechBankCodesData"

    def __init__(self, registry: PatternRegistry | None = None, bank_codes_data: "CzechBankCodesData | None" = None) -> None:
        super().__init__(
            name="bank_account",
            region="cz",
            description="Czech bank account number detector with MOD11 checksum validation"
        )
        self.registry = registry or get_shared_registry()
        if bank_codes_data is not None:
            self.bank_codes_data = bank_codes_data
        else:
            from fastpii.countries.cz.data.bank_codes import CzechBankCodesData
            self.bank_codes_data = CzechBankCodesData()

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("bank_account", "cz")
        if not patterns:
            return []

        pattern_def = patterns[0]
        findings: list[Finding] = []

        for match in pattern_def.compiled.finditer(text):
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
                    confidence=pattern_def.score,
                    region="cz",
                    metadata=metadata
                ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        from fastpii.countries.cz.validators import validate_bank_account

        is_valid, _error = validate_bank_account(value)
        return is_valid

    def _extract_metadata(self, value: str) -> dict[str, object]:
        from fastpii.countries.cz.validators import parse_bank_account

        prefix, base, bank_code = parse_bank_account(value)

        bank_names = self.bank_codes_data.get_data()
        resolved_bank_code = bank_code or ""
        bank_name = bank_names.get(resolved_bank_code, self.EMPTY_BANK_NAME)

        metadata: dict[str, object] = {
            "bank_code": resolved_bank_code,
            "bank_name": bank_name,
            "base": base or "",
        }

        if prefix:
            metadata["prefix"] = prefix

        return metadata
