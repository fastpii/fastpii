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
}

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
        r'\b([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]{2,}(?:\s+[a-záčďéěíňóřšťúůýž]+)?)\s+(\d+[/\s]?\d*)[,\s]+([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž\s]{2,})[,\s]+(\d{3}\s?\d{2})\b',
        re.IGNORECASE
    )
    
    # Simpler pattern: Street + Number
    SIMPLE_ADDRESS_PATTERN: re.Pattern[str] = re.compile(
        r'\b([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]{2,}(?:\s+[a-záčďéěíňóřšťúůýž]+)?)\s+(\d+[/\s]?\d*)\b'
    )
    registry: PatternRegistry
    
    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="address",
            region="cz",
            description="Czech address detector"
        )
        self.registry = registry or get_shared_registry()
    
    @override
    def detect(self, text: str) -> list[Finding]:
        """Detect Czech addresses."""
        findings: list[Finding] = []
        
        # Try full address pattern first
        for match in self.ADDRESS_PATTERN.finditer(text):
            street = match.group(1).strip()
            number = match.group(2).strip()
            city = match.group(3).strip()
            postal_code = match.group(4).strip()
            
            full_address = match.group(0)
            
            # Validate city
            if not self._is_valid_city(city):
                continue
            
            confidence = self._calculate_confidence(street, city)
            
            address_metadata: dict[str, object] = {
                "street": street,
                "house_number": number,
                "city": city,
                "postal_code": postal_code,
                "full_address": full_address,
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
            
            confidence = 0.70  # Lower confidence for simple pattern
            
            simple_metadata: dict[str, object] = {
                "street": street,
                "house_number": number,
                "full_address": full_address,
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
        
        # Number should be reasonable
        if not number.isdigit() and '/' not in number:
            return False
        
        return True
    
    def _calculate_confidence(self, street: str, city: str) -> float:
        """Calculate confidence based on components."""
        confidence = 0.80  # Base confidence
        
        # Boost for known city
        if self._is_valid_city(city):
            confidence += 0.10
        
        # Boost for reasonable street name
        if len(street) >= 3:
            confidence += 0.05
        
        return min(confidence, 0.95)
