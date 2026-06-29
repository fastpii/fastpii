import re

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class GermanPostalCodeDetector(Detector):
    registry: PatternRegistry
    MAJOR_CITIES: frozenset[str] = frozenset({
        "berlin", "hamburg", "münchen", "munchen", "munich", "köln", "koln", "cologne",
        "frankfurt", "stuttgart", "düsseldorf", "dusseldorf", "dortmund", "essen",
        "leipzig", "bremen", "dresden", "hannover", "nürnberg", "nurnberg", "nuernberg",
    })
    CONTEXT_PATTERN: str = r"(?i)\b(?:PLZ|Postleitzahl|postal code|zip)\b\s*:?"
    CONTEXT_WINDOW: int = 30
    CONFIDENCE_WITH_CONTEXT_LABEL: float = 0.95
    CONFIDENCE_WITH_CITY_OR_COMMA: float = 0.75
    INVALID_POSTAL_CODE: str = "00000"

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="postal_code",
            region="de",
            description="German postal code detector"
        )
        self.registry = registry or get_shared_registry()
        self._context_regex: re.Pattern[str] = re.compile(self.CONTEXT_PATTERN)
        self._city_regex: re.Pattern[str] = re.compile(
            r"(?i)\b(?:" + "|".join(re.escape(c) for c in self.MAJOR_CITIES) + r")\b"
        )

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("postal_code", "de")
        if not patterns:
            return []

        pattern_def = patterns[0]
        findings: list[Finding] = []

        for match in pattern_def.compiled.finditer(text):
            value = match.group(1)

            context_start = max(0, match.start() - self.CONTEXT_WINDOW)
            before_window = text[context_start:match.start()]
            after_window = text[match.end():min(len(text), match.end() + self.CONTEXT_WINDOW)]

            has_context = (
                bool(self._context_regex.search(before_window))
                or bool(self._city_regex.search(after_window))
                or text[max(0, match.start() - 3):match.start()].rstrip().endswith(",")
            )

            if not has_context:
                continue

            confidence = self.CONFIDENCE_WITH_CONTEXT_LABEL if bool(self._context_regex.search(before_window)) else self.CONFIDENCE_WITH_CITY_OR_COMMA

            findings.append(Finding(
                type="postal_code",
                value=value,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                region="de",
                metadata={"zone": value[0]}
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        return bool(re.match(r"^\d{5}$", value)) and value != self.INVALID_POSTAL_CODE

    def _extract_metadata(self, value: str) -> dict[str, object]:
        return {"zone": value[0] if value else ""}