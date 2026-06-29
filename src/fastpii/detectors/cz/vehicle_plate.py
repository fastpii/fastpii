import re


from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class VehiclePlateDetector(Detector):

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

    CONTEXT_WORDS: tuple[str, ...] = (
        "spz", "spz,", "vozidlo", "auto", "parkování", "parkovací", "řidič",
    )

    CONTEXT_CONFIDENCE: float = 0.95
    REGIONAL_CONFIDENCE: float = 0.85
    DEFAULT_CONFIDENCE: float = 0.70

    NEW_FORMAT: re.Pattern[str] = re.compile(
        r'\b([0-9A-CEHJKL-NP-SU-Z]{1,2}[A-Z][0-9A-CEHJKL-NP-SU-Z]{0,1})\s+([0-9A-Z]{4,5})\b'
    )

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
        findings: list[Finding] = []

        seen_spans: set[tuple[int, int]] = set()

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

        for match in self.OLD_FORMAT.finditer(text):
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
        plate = value.strip().upper()

        if self.NEW_FORMAT.match(plate):
            return self._is_valid_plate(plate, "new")

        if self.OLD_FORMAT.match(plate):
            return self._is_valid_plate(plate, "old")

        return False

    def _is_valid_plate(self, plate: str, format_type: str) -> bool:
        plate_upper = plate.upper()

        if 'Q' in plate_upper:
            return False

        plate_no_space = plate_upper.replace(' ', '')

        if len(set(plate_no_space.replace(' ', ''))) <= 2:
            return False

        if format_type == "new":
            if len(plate_no_space) < 6 or len(plate_no_space) > 8:
                return False
        else:
            if len(plate_no_space) < 6 or len(plate_no_space) > 7:
                return False
            parts = plate_upper.split()
            if len(parts) == 2:
                letters, digits = parts
                if not letters.isalpha() or not digits.isdigit():
                    return False
                if len(set(letters)) == 1:
                    return False

        return True

    def _calculate_confidence(self, plate: str, text: str, _position: int) -> float:
        text_lower = text.lower()

        for word in self.CONTEXT_WORDS:
            if word in text_lower:
                return self.CONTEXT_CONFIDENCE

        plate_upper = plate.upper().replace(' ', '')
        if plate_upper[0] in self.REGIONAL_CODES:
            return self.REGIONAL_CONFIDENCE

        return self.DEFAULT_CONFIDENCE

    def _get_region(self, plate: str) -> str:
        plate_upper = plate.upper().strip()
        first_char = plate_upper[0]

        return self.REGIONAL_CODES.get(first_char, "unknown")