"""Czech health insurance number detector.

Detects Czech health insurance numbers (číslo pojištěnce) with context-gated
detection and validation against the 7 official insurance company codes.

The number format is: 3-digit insurance code + 6-9 digit personal number
(9-12 digits total). The first 3 digits must be one of the 7 valid codes:
111, 201, 205, 207, 209, 211, 213.
"""

import re
from collections.abc import Callable
from typing import TYPE_CHECKING, ClassVar, TypeVar

F = TypeVar("F", bound=Callable[..., object])

try:
    from typing_extensions import override
except ImportError:
    def override(method: F, /) -> F:
        return method

from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry

if TYPE_CHECKING:
    from fastpii.countries.cz.data.insurance_codes import CzechInsuranceCodesData


class HealthInsuranceDetector(Detector):
    """Czech health insurance number detector.

    Detects health insurance numbers with 3-digit company code prefix.
    Validates against the 7 official Czech insurance company codes.
    Context-gated: requires context words or slash format for detection.
    """

    CONTEXT_WINDOW: int = 50
    CONTEXT_CONFIDENCE: float = 0.95
    NO_CONTEXT_CONFIDENCE: float = 0.70

    INSURANCE_CONTEXT_WORDS: ClassVar[tuple[str, ...]] = (
        "pojištění", "zdravotní pojišťovna", "pojišťovna", "pojištěnec",
        "číslo pojištěnce", "č. pojištěnce", "health insurance", "insurance",
    )

    _context_regex: ClassVar[re.Pattern[str]] = re.compile(
        r"(?i)(?:pojištění|zdravotní\s+pojišťovna|pojišťovna|pojištěnec|"
        r"číslo\s+pojištěnce|č\.\s*pojištěnce|health\s+insurance|insurance)",
    )

    INSURANCE_NUMBER_PATTERN: re.Pattern[str] = re.compile(
        r'\b(\d{3})(\d{6,9})\b'
    )

    SLASH_FORMAT_PATTERN: re.Pattern[str] = re.compile(
        r'\b(\d{3})/(\d{6,9})\b'
    )

    registry: PatternRegistry
    insurance_data: "CzechInsuranceCodesData"
    valid_codes: set[str]
    insurance_names: dict[str, str]

    def __init__(
        self,
        registry: PatternRegistry | None = None,
        insurance_data: "CzechInsuranceCodesData | None" = None,
    ) -> None:
        super().__init__(
            name="health_insurance",
            region="cz",
            description="Czech health insurance number detector"
        )
        self.registry = registry or get_shared_registry()
        if insurance_data is not None:
            self.insurance_data = insurance_data
        else:
            from fastpii.countries.cz.data.insurance_codes import CzechInsuranceCodesData
            self.insurance_data = CzechInsuranceCodesData()
        data = self.insurance_data.get_data()
        self.valid_codes = set(data.keys())
        self.insurance_names = data

    @override
    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []

        # Slash format: XXX/YYYYYYY
        for match in self.SLASH_FORMAT_PATTERN.finditer(text):
            insurance_code = match.group(1)
            personal_number = match.group(2)

            if insurance_code not in self.valid_codes:
                continue

            full_value = match.group(0)
            metadata = self._extract_metadata(insurance_code, personal_number)

            findings.append(Finding(
                type="health_insurance",
                value=full_value,
                start=match.start(),
                end=match.end(),
                confidence=self.CONTEXT_CONFIDENCE,
                region="cz",
                metadata=metadata,
            ))

        # Plain format: XXXXXXXXX (9-12 digits with valid 3-digit prefix)
        for match in self.INSURANCE_NUMBER_PATTERN.finditer(text):
            insurance_code = match.group(1)
            personal_number = match.group(2)
            full_value = match.group(0)

            # Skip if this overlaps with an already-found slash format match
            if any(f.start <= match.start() and f.end >= match.end() for f in findings):
                continue

            if insurance_code not in self.valid_codes:
                continue

            has_context = self._has_insurance_context(text, match.start())
            metadata = self._extract_metadata(insurance_code, personal_number)

            findings.append(Finding(
                type="health_insurance",
                value=full_value,
                start=match.start(),
                end=match.end(),
                confidence=self.CONTEXT_CONFIDENCE if has_context else self.NO_CONTEXT_CONFIDENCE,
                region="cz",
                metadata=metadata,
            ))

        findings.sort(key=lambda f: f.start)
        return findings

    @override
    def validate(self, value: str) -> bool:
        cleaned = value.replace("/", "").replace(" ", "")
        if not cleaned.isdigit():
            return False

        if len(cleaned) < 9 or len(cleaned) > 12:
            return False

        insurance_code = cleaned[:3]
        if insurance_code not in self.valid_codes:
            return False

        return True

    def _has_insurance_context(self, text: str, position: int) -> bool:
        start = max(0, position - self.CONTEXT_WINDOW)
        window = text[start:position]
        return bool(self._context_regex.search(window))

    def _extract_metadata(self, insurance_code: str, personal_number: str) -> dict[str, object]:
        metadata: dict[str, object] = {
            "insurance_code": insurance_code,
            "personal_number": personal_number,
        }

        company_name = self.insurance_names.get(insurance_code)
        if company_name:
            metadata["company_name"] = company_name

        return metadata