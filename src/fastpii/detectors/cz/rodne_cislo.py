from datetime import datetime

from typing import ClassVar

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class RodneCisloDetector(Detector):
    CONFIDENCE_VALID: ClassVar[float] = 0.90
    CONFIDENCE_NEAR_VALID: ClassVar[float] = 0.65
    CONFIDENCE_9_DIGIT: ClassVar[float] = 0.85
    CONFIDENCE_CONTEXT_BOOST: ClassVar[float] = 0.05
    CONTEXT_WINDOW: ClassVar[int] = 50
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
            cleaned = raw_value

            if len(cleaned) not in (9, 10) or not cleaned.isdigit():
                continue

            if not self._validate_date(cleaned):
                continue

            if len(cleaned) == 10:
                checksum_valid = self._validate_checksum(cleaned)
                if checksum_valid:
                    confidence = self.CONFIDENCE_VALID
                else:
                    confidence = self.CONFIDENCE_NEAR_VALID
            else:
                confidence = self.CONFIDENCE_9_DIGIT
                checksum_valid = None

            context_start = max(0, match.start() - self.CONTEXT_WINDOW)
            context_end = min(len(text), match.end() + self.CONTEXT_WINDOW)
            context_window = text[context_start:context_end].lower()
            if any(word.lower() in context_window for word in pattern_def.context_words):
                confidence = min(1.0, confidence + self.CONFIDENCE_CONTEXT_BOOST)

            metadata = self._extract_metadata(cleaned)
            if "checksum_valid" not in metadata:
                metadata["checksum_valid"] = checksum_valid

            findings.append(Finding(
                type="rodne_cislo",
                value=raw_value,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
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
        metadata: dict[str, object] = {
            "checksum_valid": self._validate_checksum(rc) if len(rc) == 10 else None,
        }

        try:
            year = int(rc[0:2])
            month = int(rc[2:4])
            day = int(rc[4:6])

            is_female = month > 50

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
