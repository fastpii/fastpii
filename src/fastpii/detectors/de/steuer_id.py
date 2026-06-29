import re

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry
from fastpii.countries.de.validators import is_valid_steuer_id, extract_steuer_id_metadata


class SteuerIdDetector(Detector):
    registry: PatternRegistry
    CONTEXT_PATTERN: str = r"(?i)\b(?:Steuer-ID|Steueridentifikationsnummer|IdNr|tax ID|Steuernummer)\b\s*:?"
    FALLBACK_CONFIDENCE: float = 0.80
    CONTEXT_WINDOW: int = 50

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="steuer_id",
            region="de",
            description="German tax ID (Steuer-ID) detector with checksum validation"
        )
        self.registry = registry or get_shared_registry()
        self._context_regex = re.compile(self.CONTEXT_PATTERN)

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("steuer_id", "de")
        if not patterns:
            return []

        pattern_def = patterns[0]
        findings: list[Finding] = []

        for match in pattern_def.compiled.finditer(text):
            value = match.group(1)

            if not is_valid_steuer_id(value):
                continue

            has_context = bool(self._context_regex.search(text[max(0, match.start() - self.CONTEXT_WINDOW):match.start()]))
            metadata = extract_steuer_id_metadata(value)

            findings.append(Finding(
                type="steuer_id",
                value=value,
                start=match.start(),
                end=match.end(),
                confidence=pattern_def.score if has_context else self.FALLBACK_CONFIDENCE,
                region="de",
                metadata=metadata
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        return is_valid_steuer_id(value)

    def _extract_metadata(self, value: str) -> dict[str, object]:
        return extract_steuer_id_metadata(value)
