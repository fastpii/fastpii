import re

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class FrenchAddressDetector(Detector):
    MAJOR_FRENCH_STREETS: set[str] = {
        "rue de rivoli", "avenue des champs-élysées", "boulevard saint-germain",
        "rue de la paix", "avenue de l'opéra", "rue du faubourg",
        "boulevard haussmann", "rue saint-honoré", "avenue montaigne",
    }
    MAJOR_FRENCH_CITIES: set[str] = {
        "paris", "lyon", "marseille", "toulouse", "nice", "nantes", "bordeaux",
        "strasbourg", "lille", "rennes", "montpellier", "grenoble", "nice",
        "le havre", "reims", "dijon",
    }
    STREET_PREFIX_PATTERN: str = r"(?:rue|avenue|boulevard|bd|allée|allee|place|pl\.?|chemin|impasse|cours|quai)"
    STREET_NAME_PATTERN: str = r"(?:[A-Za-zÀÂÄÇÉÈÊËÎÏÔÖÙÛÜàâäçéèêëîïôöùûü]+(?:[-'\s]+[A-Za-zÀÂÄÇÉÈÊËÎÏÔÖÙÛÜàâäçéèêëîïôöùûü]+)*)"
    HOUSE_PART_PATTERN: str = r"\d{1,4}(?:\s*bis|\s*ter)?"
    POSTAL_PART_PATTERN: str = r"\d{5}"
    CITY_PART_PATTERN: str = r"[A-ZÀÂÄÇÉÈÊËÎÏÔÖÙÛÜ][a-zàâäçéèêëîïôöùûü]+(?:[-'\s]+[A-ZÀÂÄÇÉÈÊËÎÏÔÖÙÛÜa-zàâäçéèêëîïôöùûü]+){0,2}"
    BASE_SCORE: int = 80
    POSTAL_CITY_BONUS: int = 20
    MAJOR_STREET_BONUS: int = 10
    MAJOR_CITY_BONUS: int = 10
    SCORE_DIVISOR: float = 100.0
    MAX_CONFIDENCE: float = 1.0
    SIMPLE_PATTERN_CONFIDENCE: float = 0.60
    SIMPLE_PATTERN_SCORE: int = 60
    MIN_VALIDATE_LENGTH: int = 8
    registry: PatternRegistry

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="address",
            region="fr",
            description="French address detector"
        )
        self.registry = registry or get_shared_registry()
        self._address_pattern = re.compile(
            rf"\b({self.HOUSE_PART_PATTERN})\s+({self.STREET_PREFIX_PATTERN}\s+{self.STREET_NAME_PATTERN})(?:,\s*({self.POSTAL_PART_PATTERN})\s+({self.CITY_PART_PATTERN}))?\b",
            re.IGNORECASE
        )
        self._simple_pattern = re.compile(
            rf"\b({self.HOUSE_PART_PATTERN})\s+({self.STREET_PREFIX_PATTERN}\s+{self.STREET_NAME_PATTERN})\b",
            re.IGNORECASE
        )

    @override
    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []

        for match in self._address_pattern.finditer(text):
            number = match.group(1).strip()
            street = match.group(2).strip()
            postal = match.group(3)
            city = match.group(4)

            full_address = match.group(0)
            score = self.BASE_SCORE

            if postal and city:
                score += self.POSTAL_CITY_BONUS
            if any(s in full_address.lower() for s in self.MAJOR_FRENCH_STREETS):
                score += self.MAJOR_STREET_BONUS
            if any(c in full_address.lower() for c in self.MAJOR_FRENCH_CITIES):
                score += self.MAJOR_CITY_BONUS

            findings.append(Finding(
                type="address",
                value=full_address,
                start=match.start(),
                end=match.end(),
                confidence=min(score / self.SCORE_DIVISOR, self.MAX_CONFIDENCE),
                region="fr",
                metadata={
                    "house_number": number,
                    "street": street,
                    "postal_code": postal or "",
                    "city": city.strip() if city else "",
                    "score": score,
                }
            ))

        for match in self._simple_pattern.finditer(text):
            if any(f.start <= match.start() < f.end for f in findings):
                continue

            number = match.group(1).strip()
            street = match.group(2).strip()

            findings.append(Finding(
                type="address",
                value=match.group(0),
                start=match.start(),
                end=match.end(),
                confidence=self.SIMPLE_PATTERN_CONFIDENCE,
                region="fr",
                metadata={"house_number": number, "street": street, "score": self.SIMPLE_PATTERN_SCORE}
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        if not value or len(value) < self.MIN_VALIDATE_LENGTH:
            return False
        return bool(re.search(r"\d+", value)) and bool(re.search(r"[A-Za-zÀÂÄÇÉÈÊËÎÏÔÖÙÛÜàâäçéèêëîïôöùûü]", value))

    def _extract_metadata(self, value: str) -> dict[str, object]:
        return {"raw": value}