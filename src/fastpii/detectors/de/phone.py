import re

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class GermanPhoneDetector(Detector):
    registry: PatternRegistry
    CONTEXT_PATTERN: str = r"(?i)\b(?:Tel|Telefon|Handy|phone|mobile|Rufnummer)\b\s*:?"
    CONTEXT_WINDOW: int = 50
    COUNTRY_PREFIX: str = "+49"
    MOBILE_PREFIXES: tuple[str, ...] = ("4915", "4916", "4917")
    MIN_SUBSCRIBER_LEN: int = 3
    MAX_SUBSCRIBER_LEN: int = 13

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="phone",
            region="de",
            description="German phone number detector"
        )
        self.registry = registry or get_shared_registry()
        self._context_regex = re.compile(self.CONTEXT_PATTERN)

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("phone", "de")
        if not patterns:
            return []

        pattern_def = patterns[0]
        findings: list[Finding] = []

        for match in pattern_def.compiled.finditer(text):
            raw_phone = match.group(0)
            phone_start = match.start()
            phone_end = match.end()

            if phone_start > 0 and text[phone_start - 1].isdigit():
                continue
            if phone_end < len(text) and text[phone_end].isdigit():
                continue

            if raw_phone.lstrip().startswith(self.COUNTRY_PREFIX):
                has_context = True
            else:
                has_context = bool(
                    self._context_regex.search(text[max(0, phone_start - self.CONTEXT_WINDOW):phone_start])
                )

            if not has_context:
                continue

            normalized = self._normalize_phone(raw_phone)

            findings.append(Finding(
                type="phone",
                value=normalized,
                start=phone_start,
                end=phone_end,
                confidence=pattern_def.score,
                region="de",
                metadata={"phone_type": "mobile" if normalized.startswith(self.MOBILE_PREFIXES) else "landline"}
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        cleaned = self._normalize_phone(value)
        if cleaned.startswith("49"):
            cleaned = cleaned[2:]
        return self.MIN_SUBSCRIBER_LEN <= len(cleaned) <= self.MAX_SUBSCRIBER_LEN and cleaned.isdigit()

    def _normalize_phone(self, phone: str) -> str:
        cleaned = phone.replace(" ", "").replace("-", "")
        if cleaned.startswith("+"):
            return cleaned[1:]
        if cleaned.startswith("0"):
            return f"49{cleaned[1:]}"
        return cleaned

    def _extract_metadata(self, value: str) -> dict[str, object]:
        return {"normalized": self._normalize_phone(value)}