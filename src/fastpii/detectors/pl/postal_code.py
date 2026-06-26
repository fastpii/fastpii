import re

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class PolishPostalCodeDetector(Detector):
    registry: PatternRegistry
    MAJOR_POLISH_CITIES: set[str] = {
        "warszawa", "kraków", "krakow", "wrocław", "wroclaw", "gdańsk", "gdansk",
        "poznań", "poznan", "szczecin", "bydgoszcz", "lublin", "katowice",
        "bialystok", "białystok", "gdynia", "czestochowa", "częstochowa",
        "radom", "sosnowiec", "toruń", "torun", "kielce", "lodź", "lodz",
        "rzeszów", "rzeszow", "olsztyn", "zabrze", "bielsko-biała", "bytom",
    }
    CONTEXT_REGEX_PATTERN: str = r"(?i)\b(?:kod pocztowy|postal code|zip|p\.p\.)\b\s*:?"
    CONTEXT_WINDOW: int = 30
    CONFIDENCE_WITH_CONTEXT: float = 0.95
    CONFIDENCE_WITHOUT_CONTEXT: float = 0.80

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="postal_code",
            region="pl",
            description="Polish postal code detector"
        )
        self.registry = registry or get_shared_registry()
        self._context_regex = re.compile(self.CONTEXT_REGEX_PATTERN)
        self._city_regex = re.compile(
            r"(?i)\b(?:" + "|".join(re.escape(c) for c in self.MAJOR_POLISH_CITIES) + r")\b"
        )

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("postal_code", "pl")
        if not patterns:
            return []

        pattern_def = patterns[0]
        findings: list[Finding] = []

        for match in pattern_def.compiled.finditer(text):
            prefix = match.group(1)
            suffix = match.group(2)
            value = f"{prefix}-{suffix}"

            if match.start() > 0 and text[match.start() - 1] == '+':
                continue

            context_start = max(0, match.start() - self.CONTEXT_WINDOW)
            before_window = text[context_start:match.start()]
            after_window = text[match.end():min(len(text), match.end() + self.CONTEXT_WINDOW)]

            has_context = (
                bool(self._context_regex.search(before_window))
                or bool(self._city_regex.search(after_window))
                or "-" in match.group(0)
            )

            if not has_context:
                continue

            confidence = self.CONFIDENCE_WITH_CONTEXT if bool(self._context_regex.search(before_window)) else self.CONFIDENCE_WITHOUT_CONTEXT

            findings.append(Finding(
                type="postal_code",
                value=value,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                region="pl",
                metadata={}
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        cleaned = value.replace("-", "").replace(" ", "")
        if len(cleaned) != 5:
            return False
        return cleaned.isdigit()

    def _extract_metadata(self, value: str) -> dict[str, object]:
        return {}