import re

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry
from fastpii.countries.pl.validators import is_valid_pesel, extract_pesel_metadata


class PeseleDetector(Detector):
    registry: PatternRegistry
    CONTEXT_REGEX_PATTERN: str = r"(?i)\b(?:PESEL|pesel|numer PESEL|identyfikacji)\b\s*:?"
    CONTEXT_WINDOW: int = 50
    NO_CONTEXT_CONFIDENCE: float = 0.80

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="pesel",
            region="pl",
            description="Polish national ID (PESEL) detector with checksum validation"
        )
        self.registry = registry or get_shared_registry()
        self._context_regex: re.Pattern[str] = re.compile(self.CONTEXT_REGEX_PATTERN)

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("pesel", "pl")
        if not patterns:
            return []

        pattern_def = patterns[0]
        findings: list[Finding] = []

        for match in pattern_def.compiled.finditer(text):
            value = match.group(1)

            if not is_valid_pesel(value):
                continue

            has_context = bool(self._context_regex.search(text[max(0, match.start() - self.CONTEXT_WINDOW):match.start()]))

            metadata = extract_pesel_metadata(value)

            findings.append(Finding(
                type="pesel",
                value=value,
                start=match.start(),
                end=match.end(),
                confidence=pattern_def.score if has_context else self.NO_CONTEXT_CONFIDENCE,
                region="pl",
                metadata=metadata
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        return is_valid_pesel(value)

    def _extract_metadata(self, value: str) -> dict[str, object]:
        return extract_pesel_metadata(value)
