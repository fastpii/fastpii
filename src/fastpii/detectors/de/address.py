import re

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class GermanAddressDetector(Detector):
    registry: PatternRegistry
    MAJOR_STREETS: frozenset[str] = frozenset({
        "hauptstraße", "schillerstraße", "friedrichstraße", "goethestraße",
        "gartenstraße", "bahnhofstraße", "berliner straße", "münchner straße",
        "wilhelmstraße", "schulstraße", "kirchstraße", "bergstraße",
    })
    MAJOR_CITIES: frozenset[str] = frozenset({
        "berlin", "münchen", "muenchen", "hamburg", "köln", "koeln", "frankfurt",
        "stuttgart", "düsseldorf", "duesseldorf", "dortmund", "essen", "leipzig",
        "bremen", "dresden", "hannover", "nürnberg", "nuernberg",
    })
    STREET_PART_PATTERN: str = r"(?:[A-ZÄÖÜ][a-zäöüß]+(?:[-\s]?[a-zäöüß]+)*)(?:straße|str\.|weg|platz|allee|gasse|ring)"
    HOUSE_PART_PATTERN: str = r"\d{1,4}[a-zA-Z]?(?:\s*-\s*\d{1,4}[a-zA-Z]?)?"
    POSTAL_PART_PATTERN: str = r"\d{5}"
    CITY_PART_PATTERN: str = r"[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜa-zäöüß]+){0,2}"
    BASE_SCORE: int = 80
    POSTAL_CITY_BONUS: int = 20
    MAJOR_STREET_BONUS: int = 10
    MAJOR_CITY_BONUS: int = 10
    SIMPLE_SCORE: int = 60
    MIN_STREET_LENGTH: int = 4
    MIN_ADDRESS_LENGTH: int = 8

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="address",
            region="de",
            description="German address detector"
        )
        self.registry = registry or get_shared_registry()
        self._address_pattern: re.Pattern[str] = re.compile(
            rf"\b({self.STREET_PART_PATTERN})\s+({self.HOUSE_PART_PATTERN})(?:,\s*({self.POSTAL_PART_PATTERN})\s+({self.CITY_PART_PATTERN}))?\b"
        )
        self._simple_pattern: re.Pattern[str] = re.compile(rf"\b({self.STREET_PART_PATTERN})\s+({self.HOUSE_PART_PATTERN})\b")

    @override
    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []

        for match in self._address_pattern.finditer(text):
            street = match.group(1).strip()
            number = match.group(2).strip()
            postal = match.group(3)
            city = match.group(4)

            if len(street) < self.MIN_STREET_LENGTH:
                continue

            full_address = match.group(0)
            score = self.BASE_SCORE

            if postal and city:
                score += self.POSTAL_CITY_BONUS
            if any(s in full_address.lower() for s in self.MAJOR_STREETS):
                score += self.MAJOR_STREET_BONUS
            if any(c in full_address.lower() for c in self.MAJOR_CITIES):
                score += self.MAJOR_CITY_BONUS

            findings.append(Finding(
                type="address",
                value=full_address,
                start=match.start(),
                end=match.end(),
                confidence=min(score / 100.0, 1.0),
                region="de",
                metadata={
                    "street": street,
                    "house_number": number,
                    "postal_code": postal or "",
                    "city": city.strip() if city else "",
                    "score": score,
                }
            ))

        for match in self._simple_pattern.finditer(text):
            if any(f.start <= match.start() < f.end for f in findings):
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
                confidence=self.SIMPLE_SCORE / 100.0,
                region="de",
                metadata={"street": street, "house_number": number, "score": self.SIMPLE_SCORE}
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        if not value or len(value) < self.MIN_ADDRESS_LENGTH:
            return False
        return bool(re.search(r"\d+", value)) and bool(re.search(r"[A-Za-zÄÖÜäöüß]", value))

    def _extract_metadata(self, value: str) -> dict[str, object]:
        return {"raw": value}