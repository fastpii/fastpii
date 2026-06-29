"""Credit card detector with Luhn checksum validation.

Detects Visa, MasterCard, and American Express card numbers with context-gated
detection. Uses Luhn algorithm for checksum validation and BIN prefix matching
for card type identification.
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


class CreditCardDetector(Detector):
    """Credit card detector with Luhn validation and BIN prefix matching.

    Detects Visa (13/16 digits), MasterCard (16 digits), and Amex (15 digits).
    Context-gated: requires context words for detection.
    """

    CONTEXT_WINDOW: int = 80
    CONTEXT_CONFIDENCE: float = 0.95
    NO_CONTEXT_CONFIDENCE: float = 0.60

    CARD_CONTEXT_WORDS: ClassVar[tuple[str, ...]] = (
        "credit card", "card number", "card no", "card#", "card:",
        "kreditní karta", "platební karta", "karta", "číslo karty",
        "visa", "mastercard", "amex", "american express",
        "cvv", "cvc", "expiry", "expiration",
    )

    _context_regex: ClassVar[re.Pattern[str]] = re.compile(
        r"(?i)(?:credit\s+card|card\s+number|card\s+no|card\s*#|card:|"
        r"kreditní\s+karta|platební\s+karta|číslo\s+karty|"
        r"visa|mastercard|amex|american\s+express|cvv|cvc|expiry|expiration)",
    )

    CARD_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r'\b(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{1,4})\b|'
        r'\b(\d{4}[\s-]?\d{6}[\s-]?\d{5})\b|'
        r'\b(\d{13,16})\b'
    )

    CARD_PREFIXES: ClassVar[dict[str, list[tuple[int, int]]]] = {
        "visa": [(4, 1)],
        "mastercard": [
            (51, 2), (52, 2), (53, 2), (54, 2), (55, 2),
            (2221, 4), (2222, 4), (2223, 4), (2224, 4), (2225, 4),
            (2226, 4), (2227, 4), (2228, 4), (2229, 4), (2230, 4),
            (2231, 4), (2232, 4), (2233, 4), (2234, 4), (2235, 4),
            (2236, 4), (2237, 4), (2238, 4), (2239, 4), (2240, 4),
            (2250, 4), (2260, 4), (2270, 4), (2280, 4), (2290, 4),
            (2300, 4), (2310, 4), (2320, 4), (2330, 4), (2340, 4),
            (2350, 4), (2360, 4), (2370, 4), (2380, 4), (2390, 4),
            (2400, 4), (2410, 4), (2420, 4), (2430, 4), (2440, 4),
            (2450, 4), (2460, 4), (2470, 4), (2480, 4), (2490, 4),
            (2500, 4), (2510, 4), (2520, 4), (2530, 4), (2540, 4),
            (2550, 4), (2560, 4), (2570, 4), (2580, 4), (2590, 4),
            (2600, 4), (2610, 4), (2620, 4), (2630, 4), (2640, 4),
            (2650, 4), (2660, 4), (2670, 4), (2680, 4), (2690, 4),
            (2700, 4), (2710, 4), (2720, 4),
        ],
        "amex": [(34, 2), (37, 2)],
    }

    VALID_LENGTHS: ClassVar[dict[str, list[int]]] = {
        "visa": [13, 16],
        "mastercard": [16],
        "amex": [15],
    }

    registry: PatternRegistry

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="credit_card",
            region="cz",
            description="Credit card number detector with Luhn checksum validation"
        )
        self.registry = registry or get_shared_registry()

    @override
    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []

        for match in self.CARD_PATTERN.finditer(text):
            raw_value = match.group(0)
            digits = re.sub(r'[\s-]', '', raw_value)

            if len(digits) < 13 or len(digits) > 19:
                continue

            if not self._luhn_check(digits):
                continue

            card_type = self._identify_card_type(digits)
            if card_type is None:
                continue

            has_context = self._has_card_context(text, match.start())
            confidence = self.CONTEXT_CONFIDENCE if has_context else self.NO_CONTEXT_CONFIDENCE

            metadata = self._extract_metadata(digits, card_type)

            findings.append(Finding(
                type="credit_card",
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
        digits = re.sub(r'[\s-]', '', value)

        if not digits.isdigit():
            return False

        if len(digits) < 13 or len(digits) > 19:
            return False

        if not self._luhn_check(digits):
            return False

        return self._identify_card_type(digits) is not None

    @staticmethod
    def _luhn_check(number: str) -> bool:
        total = 0
        reverse_digits = number[::-1]

        for i, char in enumerate(reverse_digits):
            digit = int(char)
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit

        return total % 10 == 0

    def _identify_card_type(self, digits: str) -> str | None:
        for card_type, prefixes in self.CARD_PREFIXES.items():
            valid_lengths = self.VALID_LENGTHS[card_type]
            if len(digits) not in valid_lengths:
                continue

            for prefix, prefix_len in prefixes:
                if digits[:prefix_len] == str(prefix):
                    return card_type

        return None

    def _has_card_context(self, text: str, position: int) -> bool:
        start = max(0, position - self.CONTEXT_WINDOW)
        window = text[start:position]
        return bool(self._context_regex.search(window))

    def _extract_metadata(self, digits: str, card_type: str) -> dict[str, object]:
        metadata: dict[str, object] = {
            "card_type": card_type,
            "length": len(digits),
        }

        if card_type == "amex":
            metadata["issuer_identifier"] = digits[:2]
        elif card_type == "visa":
            metadata["issuer_identifier"] = digits[:1]
        elif card_type == "mastercard":
            metadata["issuer_identifier"] = digits[:4] if digits.startswith("2") else digits[:2]

        return metadata