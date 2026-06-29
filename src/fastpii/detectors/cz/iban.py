"""Czech IBAN (International Bank Account Number) detector.

Detects Czech IBANs with MOD97 checksum validation. Czech IBANs are 24 characters:
CZ + 2 check digits + 4 bank code + 6 prefix + 10 account number.
Format: CZXX BBBB XXXXXX YYYYYYYYYY or CZXXXXXXXXXXXXXXXXXXXXXX (without spaces).
"""

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


class IBANDetector(Detector):
    """Czech IBAN detector with MOD97 checksum validation.

    Czech IBAN format: CZ + 2 check digits + 22 BBAN characters (24 total).
    Supports both spaced (CZXX BBBB XXXXXX YYYYYYYYYY) and compact formats.
    """

    CONTEXT_WINDOW: int = 80
    CONTEXT_CONFIDENCE: float = 0.95
    CHECKSUM_CONFIDENCE: float = 1.0

    IBAN_CONTEXT_WORDS: ClassVar[tuple[str, ...]] = (
        "iban", "iban:", "international bank account",
        "mezinárodní číslo účtu", "mezinárodní účet", "swift", "bic",
    )

    _context_regex: ClassVar[re.Pattern[str]] = re.compile(
        r"(?i)(?:iban|mezinárodní\s+číslo\s+účtu|mezinárodní\s+účet|international\s+bank\s+account|swift|bic)",
    )

    IBAN_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r'\bCZ\d{2}\s?(?:\d{4}\s?){4}\d{4}\b',
        re.IGNORECASE,
    )

    CZECH_IBAN_LENGTH: int = 24

    registry: PatternRegistry

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="iban",
            region="cz",
            description="Czech IBAN (International Bank Account Number) detector"
        )
        self.registry = registry or get_shared_registry()

    @override
    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []

        for match in self.IBAN_PATTERN.finditer(text):
            raw_value = match.group(0)
            cleaned = raw_value.replace(" ", "").upper()

            if len(cleaned) != self.CZECH_IBAN_LENGTH:
                continue

            if not self._validate_check_digits(cleaned):
                continue

            has_context = self._has_iban_context(text, match.start())
            confidence = self.CHECKSUM_CONFIDENCE if not has_context else self.CONTEXT_CONFIDENCE

            metadata = self._extract_metadata(cleaned)

            findings.append(Finding(
                type="iban",
                value=raw_value,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                region="cz",
                metadata=metadata,
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        cleaned = value.replace(" ", "").upper()

        if len(cleaned) != self.CZECH_IBAN_LENGTH:
            return False

        if not cleaned.startswith("CZ"):
            return False

        if not cleaned[2:].isdigit():
            return False

        return self._validate_check_digits(cleaned)

    def _validate_check_digits(self, iban: str) -> bool:
        rearranged = iban[4:] + iban[:4]
        numeric = ""
        for char in rearranged:
            if char.isdigit():
                numeric += char
            else:
                numeric += str(ord(char) - ord('A') + 10)

        return int(numeric) % 97 == 1

    def _has_iban_context(self, text: str, position: int) -> bool:
        start = max(0, position - self.CONTEXT_WINDOW)
        window = text[start:position]
        return bool(self._context_regex.search(window))

    def _extract_metadata(self, iban: str) -> dict[str, object]:
        bban = iban[4:]
        bank_code = bban[:4]
        prefix_end = 4 + 6
        prefix = bban[4:prefix_end]
        account = bban[prefix_end:]

        metadata: dict[str, object] = {
            "bank_code": bank_code,
            "country_code": "CZ",
            "check_digits": iban[2:4],
        }

        if prefix:
            metadata["prefix"] = prefix
        if account:
            metadata["account_number"] = account

        return metadata