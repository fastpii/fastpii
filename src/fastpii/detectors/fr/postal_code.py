import re

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class FrenchPostalCodeDetector(Detector):
    MAJOR_FRENCH_CITIES: set[str] = {
        "paris", "marseille", "lyon", "toulouse", "nice", "nantes", "strasbourg",
        "montpellier", "bordeaux", "lille", "rennes", "reims", "le havre",
        "saint-étienne", "saint-etienne", "toulon", "grenoble", "dijon", "angers",
        "nîmes", "nimes", "villeurbanne", "clermont-ferrand", "le mans", "aix-en-provence",
        "brest", "tours", "amiens", "limoges", "annecy", "perpignan",
    }
    CONTEXT_PATTERN: str = r"(?i)\b(?:code postal|postal code|CP)\b\s*:?"
    CONTEXT_LABEL_CONFIDENCE: float = 0.90
    NO_LABEL_CONFIDENCE: float = 0.70
    CONTEXT_WINDOW_BEFORE: int = 30
    CONTEXT_WINDOW_AFTER: int = 30
    MAX_POSTAL_CODE: int = 95999
    registry: PatternRegistry

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="postal_code",
            region="fr",
            description="French postal code detector"
        )
        self.registry = registry or get_shared_registry()
        self._context_regex = re.compile(self.CONTEXT_PATTERN)
        self._city_regex = re.compile(
            r"(?i)\b(?:" + "|".join(re.escape(c) for c in self.MAJOR_FRENCH_CITIES) + r")\b"
        )

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("postal_code", "fr")
        if not patterns:
            return []

        pattern_def = patterns[0]
        findings: list[Finding] = []

        for match in pattern_def.compiled.finditer(text):
            value = match.group(1)

            if int(value) > self.MAX_POSTAL_CODE:
                continue

            context_start = max(0, match.start() - self.CONTEXT_WINDOW_BEFORE)
            before_window = text[context_start:match.start()]
            after_window = text[match.end():min(len(text), match.end() + self.CONTEXT_WINDOW_AFTER)]

            has_context = (
                bool(self._context_regex.search(before_window))
                or bool(self._city_regex.search(after_window))
                or text[max(0, match.start() - 3):match.start()].rstrip().endswith(",")
            )

            if not has_context:
                continue

            confidence = self.CONTEXT_LABEL_CONFIDENCE if bool(self._context_regex.search(before_window)) else self.NO_LABEL_CONFIDENCE

            findings.append(Finding(
                type="postal_code",
                value=value,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                region="fr",
                metadata={"department": value[:2]}
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        return bool(re.match(r"^\d{5}$", value)) and value != "00000"

    def _extract_metadata(self, value: str) -> dict[str, object]:
        return {"department": value[:2] if len(value) >= 2 else ""}