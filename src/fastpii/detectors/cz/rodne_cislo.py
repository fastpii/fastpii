from datetime import datetime

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


class RodneCisloDetector(Detector):
    CONFIDENCE_9_DIGIT: float = 0.85
    registry: PatternRegistry

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="rodne_cislo",
            region="cz",
            description="Czech birth number (rodné číslo) detector with checksum validation"
        )
        self.registry = registry or get_shared_registry()

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("rodne_cislo", "cz")
        if not patterns:
            return []

        pattern_def = patterns[0]
        findings: list[Finding] = []

        for match in pattern_def.compiled.finditer(text):
            raw_value = match.group(1).replace('/', '').replace(' ', '')

            is_valid = self.validate(raw_value)

            if is_valid:
                metadata = self._extract_metadata(raw_value)

                findings.append(Finding(
                    type="rodne_cislo",
                    value=raw_value,
                    start=match.start(),
                    end=match.end(),
                    confidence=pattern_def.score if len(raw_value) == 10 else self.CONFIDENCE_9_DIGIT,
                    region="cz",
                    metadata=metadata
                ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        cleaned = value.replace('/', '').replace(' ', '')

        if len(cleaned) not in (9, 10):
            return False

        if not cleaned.isdigit():
            return False

        if not self._validate_date(cleaned):
            return False

        if len(cleaned) == 10:
            return self._validate_checksum(cleaned)

        return True

    def _validate_date(self, rc: str) -> bool:
        try:
            year = int(rc[0:2])
            month = int(rc[2:4])
            day = int(rc[4:6])

            if month > 70:
                month -= 70
            elif month > 50:
                month -= 50
            elif month > 20:
                month -= 20

            if len(rc) == 10:
                if year < 54:
                    year += 2000
                else:
                    year += 1900
            else:
                if year < 54:
                    year += 1900
                else:
                    year += 1800

            _ = datetime(year, month, day)
            return True

        except ValueError:
            return False

    def _validate_checksum(self, rc: str) -> bool:
        try:
            number = int(rc[:9])
            checksum_digit = int(rc[9])

            mod = number % 11

            if mod == 10:
                expected_checksum = 0
            else:
                expected_checksum = mod

            return checksum_digit == expected_checksum
        except (ValueError, IndexError):
            return False

    def _extract_metadata(self, rc: str) -> dict[str, object]:
        metadata: dict[str, object] = {}

        try:
            year = int(rc[0:2])
            month = int(rc[2:4])
            day = int(rc[4:6])

            is_female = month > 50

            if len(rc) == 10:
                metadata["checksum_valid"] = self._validate_checksum(rc)

            if len(rc) == 10:
                if year < 54:
                    year += 2000
                else:
                    year += 1900
            else:
                if year < 54:
                    year += 1900
                else:
                    year += 1800

            metadata["birth_date"] = f"{year:04d}-{month % 50:02d}-{day:02d}"
            metadata["gender"] = "female" if is_female else "male"
            metadata["article_9"] = True

        except (ValueError, IndexError):
            pass

        return metadata