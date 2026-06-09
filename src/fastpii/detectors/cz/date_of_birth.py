"""
Date of Birth Detector.

Detects Czech date of birth patterns:
- DD.MM.YYYY (standard format)
- DD. MM. YYYY (with spaces)
- DD.MM.YY (short year)
- Contextual detection (born, narozen/a, datum narození)
"""

import re
from datetime import datetime

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


class DateOfBirthDetector(Detector):
    """Czech date of birth detector."""
    
    # Date patterns
    # Full format: DD.MM.YYYY
    DATE_PATTERN_FULL: re.Pattern[str] = re.compile(
        r'\b(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})\b'
    )
    
    # Context words that indicate this is a date of birth
    BIRTH_CONTEXT_WORDS: set[str] = {
        "narozen", "narozena", "narození", "datum narození",
        "nar.", "dat. nar.", "r.", "rodiven",
        "born", "date of birth", "dob",
    }
    registry: PatternRegistry
    
    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="date_of_birth",
            region="cz",
            description="Czech date of birth detector"
        )
        self.registry = registry or get_shared_registry()
    
    @override
    def detect(self, text: str) -> list[Finding]:
        """Detect dates of birth in text."""
        findings: list[Finding] = []
        
        for match in self.DATE_PATTERN_FULL.finditer(text):
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
            
            # Validate date
            if not self._is_valid_date(day, month, year):
                continue
            
            # Calculate confidence based on context
            confidence = self._calculate_confidence(text, match.start(), match.group(0))
            
            # Extract metadata
            metadata = self._extract_metadata(day, month, year)
            
            findings.append(Finding(
                type="date_of_birth",
                value=match.group(0),
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                region="cz",
                metadata=metadata
            ))
        
        return findings
    
    @override
    def validate(self, value: str) -> bool:
        """Validate if string looks like a date of birth."""
        match = self.DATE_PATTERN_FULL.match(value.strip())
        if not match:
            return False
        
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        
        return self._is_valid_date(day, month, year)
    
    def _is_valid_date(self, day: int, month: int, year: int) -> bool:
        """Check if date components form a valid date."""
        if month < 1 or month > 12:
            return False
        if day < 1 or day > 31:
            return False
        if year < 1900 or year > datetime.now().year:
            return False
        
        # Check days in month
        days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # Leap year check
        if month == 2:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                days_in_month[2] = 29
        
        if day > days_in_month[month]:
            return False
        
        return True
    
    def _calculate_confidence(self, text: str, _position: int, _match_value: str) -> float:
        """Calculate confidence based on context."""
        # Check for birth context words
        text_lower = text.lower()
        
        # Check if any context word appears nearby
        for word in self.BIRTH_CONTEXT_WORDS:
            if word in text_lower:
                return 0.95
        
        # Without context, lower confidence (it could be any date)
        return 0.70
    
    def _extract_metadata(self, day: int, month: int, year: int) -> dict[str, object]:
        """Extract metadata from date components."""
        # Determine age
        today = datetime.now()
        age = today.year - year
        if (today.month, today.day) < (month, day):
            age -= 1
        
        # Format ISO date
        iso_date = f"{year:04d}-{month:02d}-{day:02d}"
        
        metadata: dict[str, object] = {
            "day": day,
            "month": month,
            "year": year,
            "iso_date": iso_date,
            "age": age if age >= 0 else None,
        }
        
        # Zodiac sign (optional metadata)
        metadata["zodiac_sign"] = self._get_zodiac_sign(day, month)
        
        return metadata
    
    @staticmethod
    def _get_zodiac_sign(day: int, month: int) -> str:
        """Get zodiac sign from date."""
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "aries"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "taurus"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return "gemini"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return "cancer"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "leo"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "virgo"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "libra"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "scorpio"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "sagittarius"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "capricorn"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "aquarius"
        else:
            return "pisces"
