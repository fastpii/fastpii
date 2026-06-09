"""
Czech Vehicle Plate Detector.

Detects Czech vehicle registration plates:
- Format: 2XXX XXX or 2XXX XXXX (new format since 2001)
- Old format: XXX XXXX (before 2001)
- Letters: Excluding Q, W, CH, O, I specific rules
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


class VehiclePlateDetector(Detector):
    """Czech vehicle registration plate detector."""
    
    # Czech license plate patterns
    # New format (since 2001): 2-3 letters + space/bar + 4-5 digits/letters
    # Examples: 1A2 3456, 2B4 5678, 3A5BCD
    # Old format: XXX XXXX or XXX XXX
    
    # Regional codes (first 1-2 characters)
    REGIONAL_CODES: dict[str, str] = {
        '1': 'Praha',
        '2': 'Středočeský',
        '3': 'Plzeňský',
        '4': 'Karlovarský',
        '5': 'Ústecký',
        '6': 'Liberecký',
        '7': 'Královéhradecký',
        '8': 'Pardubický',
        '9': 'Jihomoravský',
        'A': 'Olomoucký',
        'B': 'Zlínský',
        'C': 'Moravskoslezský',
        'E': 'Vysočina',
        'K': 'Královéhradecký',
        'L': 'Liberecký',
        'M': 'Praha',
        'P': 'Plzeňský',
        'S': 'Středočeský',
        'T': 'Jihomoravský',
        'U': 'Ústecký',
    }
    
    # New format pattern: regional code + letters/digits + space + digits/letters
    NEW_FORMAT: re.Pattern[str] = re.compile(
        r'\b([0-9A-CEHJKL-NP-SU-Z]{1,2}[A-Z][0-9A-CEHJKL-NP-SU-Z]{0,1})\s+([0-9A-Z]{4,5})\b'
    )
    
    # Old format: 3 letters + space + 3-4 digits  
    OLD_FORMAT: re.Pattern[str] = re.compile(
        r'\b([A-Z]{3})\s+(\d{3,4})\b'
    )
    registry: PatternRegistry
    
    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="vehicle_plate",
            region="cz",
            description="Czech vehicle registration plate detector"
        )
        self.registry = registry or get_shared_registry()
    
    @override
    def detect(self, text: str) -> list[Finding]:
        """Detect Czech vehicle registration plates."""
        findings: list[Finding] = []
        
        seen_spans: set[tuple[int, int]] = set()
        
        # Try new format first
        for match in self.NEW_FORMAT.finditer(text):
            plate = f"{match.group(1)} {match.group(2)}"
            
            if self._is_valid_plate(plate, "new"):
                confidence = self._calculate_confidence(plate, text, match.start())
                region = self._get_region(plate)
                
                findings.append(Finding(
                    type="vehicle_plate",
                    value=plate,
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence,
                    region=region,
                    metadata={
                        "plate": plate,
                        "format": "new",
                        "region": region,
                    }
                ))
                seen_spans.add((match.start(), match.end()))
        
        # Try old format
        for match in self.OLD_FORMAT.finditer(text):
            # Skip if overlaps with new format match
            if any(match.start() >= s and match.start() < e for s, e in seen_spans):
                continue
            
            plate = f"{match.group(1)} {match.group(2)}"
            
            if self._is_valid_plate(plate, "old"):
                confidence = self._calculate_confidence(plate, text, match.start())
                
                findings.append(Finding(
                    type="vehicle_plate",
                    value=plate,
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence,
                    region="cz",
                    metadata={
                        "plate": plate,
                        "format": "old",
                    }
                ))
        
        return findings
    
    @override
    def validate(self, value: str) -> bool:
        """Validate if string looks like a Czech vehicle plate."""
        plate = value.strip().upper()
        
        # Check new format
        if self.NEW_FORMAT.match(plate):
            return self._is_valid_plate(plate, "new")
        
        # Check old format
        if self.OLD_FORMAT.match(plate):
            return self._is_valid_plate(plate, "old")
        
        return False
    
    def _is_valid_plate(self, plate: str, format_type: str) -> bool:
        """Validate Czech vehicle plate format."""
        plate_upper = plate.upper()
        
        # Must not contain Q (not used in CZ plates)
        if 'Q' in plate_upper:
            return False
        
        # Length checks
        plate_no_space = plate_upper.replace(' ', '')
        
        if format_type == "new":
            # New format: 6-8 characters
            if len(plate_no_space) < 6 or len(plate_no_space) > 8:
                return False
        else:
            # Old format: 6-7 characters
            if len(plate_no_space) < 6 or len(plate_no_space) > 7:
                return False
        
        return True
    
    def _calculate_confidence(self, plate: str, text: str, _position: int) -> float:
        """Calculate confidence based on context."""
        text_lower = text.lower()
        
        # Context words
        context_words = ["spz", "spz,", "vozidlo", "auto", "parkování", "parkovací", "řidič"]
        for word in context_words:
            if word in text_lower:
                return 0.95
        
        # Regional prefix gives higher confidence
        plate_upper = plate.upper().replace(' ', '')
        if plate_upper[0] in self.REGIONAL_CODES:
            return 0.85
        
        return 0.70
    
    def _get_region(self, plate: str) -> str:
        """Get Czech region from plate prefix."""
        plate_upper = plate.upper().strip()
        first_char = plate_upper[0]
        
        return self.REGIONAL_CODES.get(first_char, "unknown")
