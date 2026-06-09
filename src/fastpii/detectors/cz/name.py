"""
Czech Name Detector with Gender Classification.

Detects Czech personal names with gender classification based on:
1. First name + surname pattern matching
2. Known Czech name database
3. Gender-specific surname endings (-ová for married women)
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
from fastpii.data.czech_names import (
    MALE_SURNAMES,
    FEMALE_SURNAMES,
    classify_gender_by_firstname,
    get_name_confidence,
)


class NameDetector(Detector):
    """Czech name detector with gender classification."""
    
    # Pattern for detecting names: "FirstName Surname" or "FirstName LastName"
    # Surname can end with -ová for married women
    NAME_PATTERN: re.Pattern[str] = re.compile(
        r'\b([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+)\s+([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]{2,}(?:ová|ova|ý|á|ý|ec|ek)?)\b'
    )
    registry: PatternRegistry
    
    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="name",
            region="cz",
            description="Czech personal name detector with gender classification"
        )
        # Use shared registry if none provided (singleton pattern)
        self.registry = registry or get_shared_registry()
    
    @override
    def detect(self, text: str) -> list[Finding]:
        """Detect Czech names with gender classification."""
        findings: list[Finding] = []
        
        for match in self.NAME_PATTERN.finditer(text):
            firstname = match.group(1)
            surname = match.group(2)
            full_name = match.group(0)
            
            # Classify gender
            gender = self._classify_gender(firstname, surname)
            confidence = self._calculate_confidence(firstname, surname)
            
            metadata: dict[str, object] = {
                "firstname": firstname,
                "surname": surname,
                "gender": gender,
                "full_name": full_name,
            }
            
            # Determine marital status for female surnames
            if gender == 'f' and surname.lower().endswith(('ová', 'ova')):
                metadata["marital_status"] = "married"
            
            findings.append(Finding(
                type="name",
                value=full_name,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                region="cz",
                metadata=metadata
            ))
        
        return findings
    
    @override
    def validate(self, value: str) -> bool:
        """Validate if string looks like a Czech name."""
        if not value:
            return False
        
        parts = value.strip().split()
        if len(parts) < 2:
            return False
        
        firstname, surname = parts[0], parts[-1]
        
        # Check if parts start with uppercase
        if not firstname[0].isupper() or not surname[0].isupper():
            return False
        
        # Check if parts are alphabetic (with Czech diacritics)
        czech_alpha_pattern = re.compile(r'^[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+$')
        
        if not czech_alpha_pattern.match(firstname):
            return False
        
        if not czech_alpha_pattern.match(surname):
            return False
        
        return True
    
    def _classify_gender(self, firstname: str, surname: str) -> str:
        """
        Classify gender based on first name and surname patterns.
        
        Priority:
        1. Female surname ending (ová/ova) - married female
        2. Female surname in database
        3. First name in database
        4. First name patterns
        
        Returns:
            'm' for male, 'f' for female
        """
        firstname_lower = firstname.lower()
        surname_lower = surname.lower()
        
        # PRIORITY 1: Female surname ending (-ová indicates married female)
        if surname_lower.endswith(('ová', 'ova')):
            return 'f'
        
        # PRIORITY 2: Check if surname is in known databases
        if surname_lower in FEMALE_SURNAMES:
            return 'f'
        elif surname_lower in MALE_SURNAMES:
            return 'm'
        
        # PRIORITY 3: Check first name in database
        gender = classify_gender_by_firstname(firstname)
        if gender:
            return gender
        
        # PRIORITY 4: First name patterns fallback
        # Female names often end in -a, -e, -ě
        if firstname_lower.endswith(('a', 'e', 'ě')):
            return 'f'
        
        # Most Czech male names end in consonants
        return 'm'
    
    def _calculate_confidence(self, firstname: str, surname: str) -> float:
        """
        Calculate confidence based on name database membership.
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        surname_lower = surname.lower()
        
        firstname_confidence = get_name_confidence(firstname)
        
        # Check surname database
        if surname_lower in MALE_SURNAMES or surname_lower in FEMALE_SURNAMES:
            surname_confidence = 0.95
        elif surname_lower.endswith(('ová', 'ova')):
            surname_confidence = 0.90  # -ová is strong female indicator
        else:
            surname_confidence = 0.70  # Unknown surname
        
        # Average confidence
        return (firstname_confidence + surname_confidence) / 2
