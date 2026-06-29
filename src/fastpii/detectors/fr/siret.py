import re

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry
from fastpii.countries.fr.validators import is_valid_siret


class SIRETDetector(Detector):
    CONTEXT_PATTERN: str = r"(?i)\b(?:SIRET|siret|establishment)\b\s*:?"
    NO_CONTEXT_CONFIDENCE: float = 0.85
    CONTEXT_WINDOW: int = 50
    registry: PatternRegistry

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="siret",
            region="fr",
            description="French establishment ID (SIRET) detector with Luhn checksum validation"
        )
        self.registry = registry or get_shared_registry()
        self._context_regex: re.Pattern[str] = re.compile(self.CONTEXT_PATTERN)

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("siret", "fr")
        if not patterns:
            return []

        pattern_def = patterns[0]
        findings: list[Finding] = []

        for match in pattern_def.compiled.finditer(text):
            value = match.group(1)

            if not is_valid_siret(value):
                continue

            has_context = bool(self._context_regex.search(text[max(0, match.start() - self.CONTEXT_WINDOW):match.start()]))

            findings.append(Finding(
                type="siret",
                value=value,
                start=match.start(),
                end=match.end(),
                confidence=pattern_def.score if has_context else self.NO_CONTEXT_CONFIDENCE,
                region="fr",
                metadata={"checksum_valid": True, "siren": value[:9]}
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        return is_valid_siret(value)

    def _extract_metadata(self, value: str) -> dict[str, object]:
        valid = is_valid_siret(value)
        return {"checksum_valid": valid, "siren": value[:9] if len(value) >= 9 else ""}
