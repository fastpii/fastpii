import re

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class PolishAddressDetector(Detector):
    registry: PatternRegistry
    MAJOR_POLISH_STREETS: set[str] = {
        "marszałkowska", "piotrkowska", "długa", "floriańska", "grodzka",
        "rynek", "kościuszki", "sienkiewicza", "mickiewicza", "piłsudskiego",
    }
    MAJOR_POLISH_CITIES: set[str] = {
        "warszawa", "kraków", "krakow", "wrocław", "wroclaw", "gdańsk", "gdansk",
        "poznań", "poznan", "szczecin", "bydgoszcz", "lublin", "katowice",
        "bialystok", "białystok", "gdynia", "lodź", "lodz",
    }
    STREET_PART_PATTERN: str = r"[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:\s+[a-ząćęłńóśźż]+){0,2}"
    HOUSE_PART_PATTERN: str = r"\d{1,4}(?:[A-Z]?|[a-z]?)(?:/\d{1,4})?(?:\s+[A-Z]?m\.?\s*\d+)?"
    POSTAL_PART_PATTERN: str = r"\d{2}[-\s]?\d{3}"
    CITY_PART_PATTERN: str = r"[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+){0,2}"
    MIN_STREET_LENGTH: int = 4
    BASE_SCORE: int = 80
    CITY_BONUS_SCORE: int = 20
    SCORE_DIVISOR: float = 100.0
    MAX_CONFIDENCE: float = 1.0
    SIMPLE_MATCH_CONFIDENCE: float = 0.60
    SIMPLE_MATCH_SCORE: int = 60
    MIN_VALIDATE_LENGTH: int = 8

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="address",
            region="pl",
            description="Polish address detector"
        )
        self.registry = registry or get_shared_registry()
        self._address_pattern = re.compile(
            rf"\b({self.STREET_PART_PATTERN})\s+({self.HOUSE_PART_PATTERN})(?:,\s*|,\s*({self.POSTAL_PART_PATTERN})\s+({self.CITY_PART_PATTERN})|\s+({self.CITY_PART_PATTERN})(?:,\s*({self.POSTAL_PART_PATTERN}))?)\b"
        )
        self._simple_pattern = re.compile(rf"\b({self.STREET_PART_PATTERN})\s+({self.HOUSE_PART_PATTERN})\b")

    @override
    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []

        for match in self._address_pattern.finditer(text):
            street = match.group(1).strip()
            number = match.group(2).strip()

            if len(street) < self.MIN_STREET_LENGTH:
                continue

            full_address = match.group(0)
            score = self.BASE_SCORE

            if any(c in full_address.lower() for c in self.MAJOR_POLISH_CITIES):
                score += self.CITY_BONUS_SCORE

            findings.append(Finding(
                type="address",
                value=full_address,
                start=match.start(),
                end=match.end(),
                confidence=min(score / self.SCORE_DIVISOR, self.MAX_CONFIDENCE),
                region="pl",
                metadata={"street": street, "house_number": number, "score": score}
            ))

        for match in self._simple_pattern.finditer(text):
            if any(f.start <= match.start() <= f.end for f in findings):
                continue

            street = match.group(1).strip()
            number = match.group(2).strip()

            if len(street) < self.MIN_STREET_LENGTH:
                continue

            findings.append(Finding(
                type="address",
                value=match.group(0),
                start=match.start(),
                end=match.end(),
                confidence=self.SIMPLE_MATCH_CONFIDENCE,
                region="pl",
                metadata={"street": street, "house_number": number, "score": self.SIMPLE_MATCH_SCORE}
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        if not value or len(value) < self.MIN_VALIDATE_LENGTH:
            return False
        return bool(re.search(r"\d+", value)) and bool(re.search(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]", value))

    def _extract_metadata(self, value: str) -> dict[str, object]:
        return {"raw": value}