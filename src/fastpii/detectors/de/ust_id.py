import re

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry
from fastpii.countries.de.validators import is_valid_ust_id


class UStIdNrDetector(Detector):
    registry: PatternRegistry
    CONTEXT_PATTERN: str = r"(?i)\b(?:USt-IdNr|Umsatzsteuer|VAT|MwSt)\b\s*:?"
    FALLBACK_CONFIDENCE: float = 0.85
    CONTEXT_WINDOW: int = 50

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="ust_id",
            region="de",
            description="German VAT number (USt-IdNr) detector with checksum validation"
        )
        self.registry = registry or get_shared_registry()
        self._context_regex: re.Pattern[str] = re.compile(self.CONTEXT_PATTERN)

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("ust_id", "de")
        if not patterns:
            return []

        pattern_def = patterns[0]
        findings: list[Finding] = []

        for match in pattern_def.compiled.finditer(text):
            value = match.group(1)

            if not is_valid_ust_id(f"DE{value}"):
                continue

            has_context = bool(self._context_regex.search(text[max(0, match.start() - self.CONTEXT_WINDOW):match.start()]))

            findings.append(Finding(
                type="ust_id",
                value=f"DE{value}",
                start=match.start(),
                end=match.end(),
                confidence=pattern_def.score if has_context else self.FALLBACK_CONFIDENCE,
                region="de",
                metadata={"checksum_valid": True}
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        cleaned = value.strip().upper()
        if not cleaned.startswith("DE"):
            return False
        return is_valid_ust_id(cleaned)

    def _extract_metadata(self, value: str) -> dict[str, object]:
        cleaned = value.strip().upper()
        if not cleaned.startswith("DE"):
            cleaned = f"DE{cleaned}"
        return {"checksum_valid": is_valid_ust_id(cleaned)}
