"""
Czech Address Detector.

Detects Czech addresses with pattern matching for:
- Street names (common patterns)
- House numbers (č.p. / č.e.)
- City names (major Czech cities)
- Postal codes (integrated with existing postal code detector)
"""

import re

from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., object])

try:
    from typing_extensions import override
except ImportError:
    def override(method: F, /) -> F:
        return method

from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


# Major Czech cities
CZECH_CITIES = {
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

# Words that look like addresses (Capitalized + number) but are NOT addresses.
# These are common Czech context words, months, identifiers, etc.
NON_ADDRESS_WORDS = {
    # Identifier context words
    "narozen", "narozena", "narození", "nar", "datum", "rodné", "rodného",
    # Title/prefix words
    "číslo", "čís", "č", "p", "psč", "ičo", "ič", "dič", "dpč",
    # Months
    "leden", "únor", "březen", "duben", "květen", "červen", "červenec",
    "srpen", "září", "říjen", "listopad", "prosinec",
    "ledna", "února", "března", "dubna", "května", "června", "července",
    "srpna", "září", "října", "listopadu", "prosince",
    # Common non-street words that appear before numbers
    "roku", "den", "dnů", "strana", "str", "část", "období",
    "tel", "telefon", "mobil", "fax",
    # English context words (for multilingual texts)
    "born", "before", "after", "from", "date", "year", "age",
    # English months
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december",
    # Non-street headings/labels
    "postal",
}

# Shared address fragments. Use horizontal whitespace only so matches never cross lines.
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

# Common Czech street patterns
STREET_PATTERNS = [
    r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+\s+\d+[/\s]?\d*',  # Name + number
    r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+\s+[a-záčďéěíňóřšťúůýž]+\s+\d+',  # Two words + number
]

class AddressDetector(Detector):
    """Czech address detector."""
    
    # Pattern for Czech addresses
    # Format: Street Name + Number, City, Postal Code
    ADDRESS_PATTERN: re.Pattern[str] = re.compile(
        rf'\b({STREET_NAME_PART}){HORIZONTAL_WS}({HOUSE_NUMBER_PART})(?:,{OPTIONAL_HORIZONTAL_WS}|{HORIZONTAL_WS})'
        + rf'(?:({POSTAL_CODE_PART}){HORIZONTAL_WS}({CITY_PART})|({CITY_PART})(?:,{OPTIONAL_HORIZONTAL_WS}|{HORIZONTAL_WS})({POSTAL_CODE_PART}))\b'
    )
    
    # Simpler pattern: Street + Number
    SIMPLE_ADDRESS_PATTERN: re.Pattern[str] = re.compile(
        rf'\b({STREET_NAME_PART}){HORIZONTAL_WS}({HOUSE_NUMBER_PART})\b'
    )
    registry: PatternRegistry
    
    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="address",
            region="cz",
            description="Czech address detector"
        )
        self.registry = registry or get_shared_registry()
    
    # Minimum score to accept an address finding
    MIN_ADDRESS_SCORE: int = 60

    @override
    def detect(self, text: str) -> list[Finding]:
        """Detect Czech addresses."""
        findings: list[Finding] = []
        
        # Try full address pattern first
        for match in self.ADDRESS_PATTERN.finditer(text):
            street = match.group(1).strip()
            number = match.group(2).strip()
            postal_code = (match.group(3) or match.group(6) or "").strip()
            city = (match.group(4) or match.group(5) or "").strip()
            
            full_address = match.group(0)
            
            # Validate city
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
        
        # Try simpler pattern for street + number
        for match in self.SIMPLE_ADDRESS_PATTERN.finditer(text):
            # Skip if already matched in full pattern
            if any(f.start <= match.start() <= f.end for f in findings):
                continue
            
            street = match.group(1).strip()
            number = match.group(2).strip()
            
            # Validate
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
        """Validate if string looks like an address."""
        if not value or len(value) < 10:
            return False
        
        # Must contain at least a number
        if not re.search(r'\d+', value):
            return False
        
        # Must contain letters
        if not re.search(r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽa-záčďéěíňóřšťúůýž]', value):
            return False
        
        return True
    
    def _is_valid_city(self, city: str) -> bool:
        """Check if city is a known Czech city."""
        city_lower = city.lower().strip()
        return city_lower in CZECH_CITIES or any(c in city_lower for c in CZECH_CITIES)
    
    def _is_likely_address(self, street: str, number: str) -> bool:
        """Check if this looks like a real address."""
        # Street name should be reasonable length
        if len(street) < 3:
            return False
        
        # Filter out common Czech words that are NOT street names.
        # Check each WORD in the street part against the exclusion list.
        # We use exact word matching (not substring) to avoid false positives
        # like "str" matching inside "Ostravská".
        words_lower = street.lower().split()
        for word in words_lower:
            if word in NON_ADDRESS_WORDS:
                return False

        if street.lower().strip() in CZECH_CITIES:
            if re.fullmatch(HOUSE_NUMBER_PART, number) is None:
                return False

            number_value = int(number.split("/", 1)[0].split(" ", 1)[0])
            if "/" not in number and number_value <= 20:
                return False
        
        # Number should be reasonable
        if re.fullmatch(HOUSE_NUMBER_PART, number) is None:
            return False
        
        return True
    
    def _calculate_address_score(self, street: str, number: str, city: str, postal_code: str) -> int:
        """Calculate an address quality score (0-100).

        Score components:
        - Street word present (+30) — a capitalized word that's not a month/heading
        - House number present (+30) — digit(s) optionally with slash
        - Postal code present (+20) — XXX XX format
        - Known Czech city (+20) — city in dictionary

        Minimum score to accept: 60 (street + number is baseline)
        """
        score = 0

        # Street word: +30 if we have a plausible street name
        if street and len(street) >= 3:
            words_lower = street.lower().split()
            # Check that no word is a NON_ADDRESS_WORD
            if not any(w in NON_ADDRESS_WORDS for w in words_lower):
                score += 30

        # House number: +30 if we have a valid house number
        if number and re.fullmatch(HOUSE_NUMBER_PART, number):
            score += 30

        # Postal code: +20 if present
        if postal_code and re.fullmatch(POSTAL_CODE_PART, postal_code):
            score += 20

        # Known city: +20 if city is in dictionary
        if city and self._is_valid_city(city):
            score += 20

        return score
