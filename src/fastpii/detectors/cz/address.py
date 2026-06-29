import re

from collections.abc import Callable
from typing import ClassVar, TypeVar

F = TypeVar("F", bound=Callable[..., object])

try:
    from typing_extensions import override
except ImportError:
    def override(method: F, /) -> F:
        return method

from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry

try:
    from fastpii.countries.cz.data.cities import CzechCitiesData
    from fastpii.countries.cz.data.postal_codes import CzechPostalCodesData
    from fastpii.countries.cz.data.streets import CzechStreetsData
except ImportError:
    CzechCitiesData = None
    CzechPostalCodesData = None
    CzechStreetsData = None

HORIZONTAL_WS = r'[^\S\n]+'
OPTIONAL_HORIZONTAL_WS = r'[^\S\n]*'
STREET_NAME_PART = (
    r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+'
    r'(?:[^\S\n]+(?:[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+|[a-záčďéěíňóřšťúůýž]+)){0,2}'
)
HOUSE_NUMBER_PART = r'\d{1,5}(?:[/ ]\d{1,5})?'
CITY_PART = (
    r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+'
    r'(?:[^\S\n]+[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽa-záčďéěíňóřšťúůýž]+){0,3}'
    r'(?:[^\S\n]+\d{1,2})?'
)
POSTAL_CODE_PART = r'\d{3}[^\S\n]?\d{2}'

STREET_PATTERNS = [
    r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+\s+\d+[/\s]?\d*',
    r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+\s+[a-záčďéěíňóřšťúůýž]+\s+\d+',
]

FALLBACK_CITIES: set[str] = {
    "praha", "brno", "ostrava", "plzeň", "liberec", "olomouc", "české budějovice",
    "hradec králové", "pardubice", "most", "karlovy vary", "jíhlava", "písek",
    "jablonec nad nisou", "těšínsko", "kladno", "mladá boleslav", "děčín",
    "třinec", "ústí nad labem", "opava", "havířov", "kolin", "kolín", "zlín",
    "příbram", "bruntál", "cheb", "trutnov", "šumperk", "litoměřice", "kadaň",
    "mělník", "neratovice", "beroun", "bílina", "krnov", "králíky", "kroměříž",
    "hodonín", "chrudim", "rychnov nad kněžnou", "pelhřimov", "žďár nad sázavou",
    "sokolov", "sokolnice", "kyjov", "blansko", "velké mezířící", "velké opatovice",
    "chotěboř", "náchod", "broumov", "tábor", "český krumlov",
    "třebíč", "vsetín", "nový jíčín", "přerov", "frenštát pod radhoštěm",
    "uherské hradiště", "uherský brod", "znojmo", "břeclav", "veselí nad moravou",
}

NON_ADDRESS_WORDS: ClassVar[set[str]] = {
    "narozen", "narozena", "narození", "nar", "datum", "rodné", "rodného",
    "číslo", "čís", "č", "p", "psč", "ičo", "ič", "dič", "dpč",
    "leden", "únor", "březen", "duben", "květen", "červen", "červenec",
    "srpen", "září", "říjen", "listopad", "prosinec",
    "ledna", "února", "března", "dubna", "května", "června", "července",
    "srpna", "září", "října", "listopadu", "prosince",
    "roku", "den", "dnů", "strana", "str", "část", "období",
    "tel", "telefon", "mobil", "fax",
    "born", "before", "after", "from", "date", "year", "age",
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december",
    "postal",
}


class AddressDetector(Detector):

    MIN_ADDRESS_SCORE: int = 60
    SCORE_STREET: int = 30
    SCORE_NUMBER: int = 30
    SCORE_POSTAL: int = 20
    SCORE_CITY: int = 20
    SCORE_STREET_VALIDATED: int = 10

    SCORE_POSTAL_VALIDATED: int = 5

    ADDRESS_PATTERN: re.Pattern[str] = re.compile(
        rf'\b({STREET_NAME_PART}){HORIZONTAL_WS}({HOUSE_NUMBER_PART})(?:,{OPTIONAL_HORIZONTAL_WS}|{HORIZONTAL_WS})'
        + rf'(?:({POSTAL_CODE_PART}){HORIZONTAL_WS}({CITY_PART})|({CITY_PART})(?:,{OPTIONAL_HORIZONTAL_WS}|{HORIZONTAL_WS})({POSTAL_CODE_PART}))\b'
    )

    SIMPLE_ADDRESS_PATTERN: re.Pattern[str] = re.compile(
        rf'\b({STREET_NAME_PART}){HORIZONTAL_WS}({HOUSE_NUMBER_PART})\b'
    )
    registry: PatternRegistry
    cities: set[str]
    streets: set[str]
    postal_codes: set[str]

    def __init__(
        self,
        registry: PatternRegistry | None = None,
        cities_data: CzechCitiesData | None = None,
        streets_data: CzechStreetsData | None = None,
        postal_codes_data: CzechPostalCodesData | None = None,
    ) -> None:
        super().__init__(
            name="address",
            region="cz",
            description="Czech address detector"
        )
        self.registry = registry or get_shared_registry()

        if cities_data is not None:
            self.cities = cities_data.get_data()
        elif CzechCitiesData is not None:
            self.cities = CzechCitiesData().get_data()
        else:
            self.cities = FALLBACK_CITIES

        if streets_data is not None:
            self.streets = streets_data.get_data()
        elif CzechStreetsData is not None:
            self.streets = CzechStreetsData().get_data()
        else:
            self.streets = set()

        if postal_codes_data is not None:
            self.postal_codes = postal_codes_data.get_data()
        elif CzechPostalCodesData is not None:
            self.postal_codes = CzechPostalCodesData().get_data()
        else:
            self.postal_codes = set()

    @override
    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []

        for match in self.ADDRESS_PATTERN.finditer(text):
            street = match.group(1).strip()
            number = match.group(2).strip()
            postal_code = (match.group(3) or match.group(6) or "").strip()
            city = (match.group(4) or match.group(5) or "").strip()

            full_address = match.group(0)

            if not self._is_valid_city(city):
                continue

            if not self._is_likely_address(street, number):
                continue

            score = self._calculate_address_score(street, number, city, postal_code)
            if score < self.MIN_ADDRESS_SCORE:
                continue

            confidence = score / 100.0

            address_metadata: dict[str, object] = {
                "street": street,
                "house_number": number,
                "city": city,
                "postal_code": postal_code,
                "full_address": full_address,
                "score": score,
            }

            findings.append(Finding(
                type="address",
                value=full_address,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                region="cz",
                metadata=address_metadata
            ))

        for match in self.SIMPLE_ADDRESS_PATTERN.finditer(text):
            if any(f.start <= match.start() <= f.end for f in findings):
                continue

            street = match.group(1).strip()
            number = match.group(2).strip()

            if not self._is_likely_address(street, number):
                continue

            full_address = match.group(0)

            score = self._calculate_address_score(street, number, "", "")
            if score < self.MIN_ADDRESS_SCORE:
                continue

            confidence = score / 100.0

            simple_metadata: dict[str, object] = {
                "street": street,
                "house_number": number,
                "full_address": full_address,
                "score": score,
            }

            findings.append(Finding(
                type="address",
                value=full_address,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                region="cz",
                metadata=simple_metadata
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        if not value or len(value) < 10:
            return False

        if not re.search(r'\d+', value):
            return False

        if not re.search(r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽa-záčďéěíňóřšťúůýž]', value):
            return False

        return True

    def _is_valid_city(self, city: str) -> bool:
        city_lower = city.lower().strip()
        return city_lower in self.cities or any(c in city_lower for c in self.cities)

    def _is_valid_street(self, street: str) -> bool:
        if not self.streets:
            return False
        return street.lower().strip() in self.streets

    def _is_valid_postal_code(self, postal_code: str) -> bool:
        cleaned = postal_code.replace(" ", "")
        if not self.postal_codes:
            return False
        return cleaned in self.postal_codes

    def _is_likely_address(self, street: str, number: str) -> bool:
        if len(street) < 3:
            return False

        words_lower = street.lower().split()
        for word in words_lower:
            if word in NON_ADDRESS_WORDS:
                return False

        if street.lower().strip() in self.cities:
            if re.fullmatch(HOUSE_NUMBER_PART, number) is None:
                return False

            number_value = int(number.split("/", 1)[0].split(" ", 1)[0])
            if "/" not in number and number_value <= 20:
                return False

        if re.fullmatch(HOUSE_NUMBER_PART, number) is None:
            return False

        return True

    def _calculate_address_score(self, street: str, number: str, city: str, postal_code: str) -> int:
        score = 0

        if street and len(street) >= 3:
            words_lower = street.lower().split()
            if not any(w in NON_ADDRESS_WORDS for w in words_lower):
                score += self.SCORE_STREET

        if number and re.fullmatch(HOUSE_NUMBER_PART, number):
            score += self.SCORE_NUMBER

        if postal_code and re.fullmatch(POSTAL_CODE_PART, postal_code):
            score += self.SCORE_POSTAL
            if self._is_valid_postal_code(postal_code):
                score += self.SCORE_POSTAL_VALIDATED

        if city and self._is_valid_city(city):
            score += self.SCORE_CITY

        if street and self._is_valid_street(street):
            score += self.SCORE_STREET_VALIDATED

        return score