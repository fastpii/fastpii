from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., object])

try:
    from typing_extensions import override
except ImportError:
    def override(method: F, /) -> F:
        return method

from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class BankAccountDetector(Detector):
    registry: PatternRegistry

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="bank_account",
            region="cz",
            description="Czech bank account number detector with MOD11 checksum validation"
        )
        self.registry = registry or get_shared_registry()

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

        if prefix is None:
            return {"bank_code": ""}

        metadata: dict[str, object] = {
            "bank_code": bank_code or "",
            "base": base or ""
        }

        if prefix:
            metadata["prefix"] = prefix

        return metadata
