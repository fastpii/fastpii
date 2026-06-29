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


class IdentityCardDetector(Detector):
    CONTEXT_WINDOW: int = 80
    CONTEXT_CONFIDENCE: float = 0.95
    NO_CONTEXT_CONFIDENCE: float = 0.70

    _context_regex: ClassVar[re.Pattern[str]] = re.compile(
        r"(?i)(?:občanský\s+průkaz|obč\.\s*průkaz|OP|č\.\s*průkazu|číslo\s+průkazu|"
        r"průkaz\s+totožnosti|identity\s+card|id\s+card)",
    )

    _negative_context_regex: ClassVar[re.Pattern[str]] = re.compile(
        r"(?i)(?:celkem|total|suma|částka|amount|balance|zůstatek|počet|count|"
        r"number|quantity|množství|hodnota|value|výsledek|result|součet|invoice|"
        r"faktura|order|objednávka|reference|ref|account|účet)\s*[:\-=]?\s*$",
    )

    NEW_FORMAT_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r'\b(\d{9})\b'
    )

    OLD_FORMAT_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r'\b(\d{6}[A-Z]{2})\b'
    )

    registry: PatternRegistry

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="identity_card",
            region="cz",
            description="Czech identity card (občanský průkaz) detector"
        )
        self.registry = registry or get_shared_registry()

    @override
    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []

        for match in self.OLD_FORMAT_PATTERN.finditer(text):
            value = match.group(1)
            has_context = self._has_context(text, match.start())
            confidence = self._calculate_confidence(has_context, format_type="old")

            metadata: dict[str, object] = {
                "format": "old",
                "number": value,
                "series": value[6:8],
            }

            findings.append(Finding(
                type="identity_card",
                value=value,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                region="cz",
                metadata=metadata,
            ))

        for match in self.NEW_FORMAT_PATTERN.finditer(text):
            value = match.group(1)

            if value[0] == '0':
                continue

            if any(f.start <= match.start() and f.end >= match.end() for f in findings):
                continue

            if self._has_negative_context(text, match.start()):
                continue

            has_context = self._has_context(text, match.start())
            confidence = self._calculate_confidence(has_context, format_type="new")

            metadata: dict[str, object] = {
                "format": "new",
                "number": value,
            }

            findings.append(Finding(
                type="identity_card",
                value=value,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                region="cz",
                metadata=metadata,
            ))

        findings.sort(key=lambda f: f.start)
        return findings

    @override
    def validate(self, value: str) -> bool:
        value = value.strip().upper()

        if self._is_old_format(value):
            return True

        if value.isdigit() and len(value) == 9:
            return value[0] != '0'

        return False

    def _is_old_format(self, value: str) -> bool:
        return len(value) == 8 and value[:6].isdigit() and value[6:8].isalpha()

    def _has_context(self, text: str, position: int) -> bool:
        return self._matches_context(self._context_regex, text, position)

    def _has_negative_context(self, text: str, position: int) -> bool:
        return self._matches_context(self._negative_context_regex, text, position)

    def _matches_context(self, pattern: re.Pattern[str], text: str, position: int) -> bool:
        start = max(0, position - self.CONTEXT_WINDOW)
        window = text[start:position]
        return bool(pattern.search(window))

    def _calculate_confidence(self, has_context: bool, format_type: str = "new") -> float:
        if has_context:
            return self.CONTEXT_CONFIDENCE
        if format_type == "old":
            return 0.85
        return self.NO_CONTEXT_CONFIDENCE