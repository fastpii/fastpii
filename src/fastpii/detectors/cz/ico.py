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


class ICODetector(Detector):
    CHECKSUM_WEIGHTS: list[int] = [8, 7, 6, 5, 4, 3, 2]
    registry: PatternRegistry

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="ico",
            region="cz",
            description="Czech company ID (IČO) detector with checksum validation"
        )
        self.registry = registry or get_shared_registry()

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("ico", "cz")
        if not patterns:
            return []

        pattern_def = patterns[0]
        findings: list[Finding] = []

        for match in pattern_def.compiled.finditer(text):
            value = match.group(1)

            is_valid = self.validate(value)

            if is_valid:
                metadata = self._extract_metadata(value)

                findings.append(Finding(
                    type="ico",
                    value=value,
                    start=match.start(),
                    end=match.end(),
                    confidence=pattern_def.score,
                    region="cz",
                    metadata=metadata
                ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        cleaned = value.replace('/', '').replace(' ', '')

        if len(cleaned) != 8:
            return False

        if not cleaned.isdigit():
            return False

        return self._validate_checksum(cleaned)

    def _validate_checksum(self, ico: str) -> bool:
        try:
            total = sum(int(ico[i]) * self.CHECKSUM_WEIGHTS[i] for i in range(7))

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

    def _extract_metadata(self, ico: str) -> dict[str, object]:
        return {
            "checksum_valid": self._validate_checksum(ico)
        }