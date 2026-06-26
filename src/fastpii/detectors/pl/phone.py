import re

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class PolishPhoneDetector(Detector):
    CONTEXT_REGEX_PATTERN: str = r"(?i)\b(?:tel|telefon|kom[óo]rka|phone|mobile|contact|numer)\b\s*:?"
    CONTEXT_WINDOW: int = 50

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="phone",
            region="pl",
            description="Polish phone number detector (mobile and landline)"
        )
        self.registry = registry or get_shared_registry()
        self._context_regex = re.compile(self.CONTEXT_REGEX_PATTERN)

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("phone", "pl")
        if not patterns:
            return []

        findings: list[Finding] = []

        for pattern_def in patterns:
            for match in pattern_def.compiled.finditer(text):
                raw_phone = match.group(0)
                phone_start = match.start()
                phone_end = match.end()

                if phone_start > 0 and text[phone_start - 1].isdigit():
                    continue
                if phone_end < len(text) and text[phone_end].isdigit():
                    continue

                if raw_phone.lstrip().startswith("+48") or raw_phone.lstrip().startswith("48"):
                    has_context = True
                else:
                    has_context = bool(
                        self._context_regex.search(text[max(0, phone_start - self.CONTEXT_WINDOW):phone_start])
                    )

                if not has_context:
                    continue

                normalized = self._normalize_phone(raw_phone)
                phone_type = "mobile" if pattern_def.name == "mobile" else "landline"

                findings.append(Finding(
                    type="phone",
                    value=normalized,
                    start=phone_start,
                    end=phone_end,
                    confidence=pattern_def.score,
                    region="pl",
                    metadata={"phone_type": phone_type}
                ))

        findings = self._deduplicate(findings)
        return findings

    @override
    def validate(self, value: str) -> bool:
        cleaned = self._normalize_phone(value)
        if cleaned.startswith("48"):
            cleaned = cleaned[2:]
        return len(cleaned) == 9 and cleaned.isdigit()

    def _normalize_phone(self, phone: str) -> str:
        cleaned = phone.replace(" ", "").replace("-", "")
        if cleaned.startswith("+"):
            return cleaned[1:]
        if not cleaned.startswith("48") and len(cleaned) == 9:
            return f"48{cleaned}"
        return cleaned

    def _deduplicate(self, findings: list[Finding]) -> list[Finding]:
        if not findings:
            return findings
        sorted_f = sorted(findings, key=lambda f: f.start)
        result: list[Finding] = []
        for finding in sorted_f:
            overlaps = False
            for existing in result:
                if finding.start < existing.end and finding.end > existing.start:
                    overlaps = True
                    if (finding.end - finding.start) > (existing.end - existing.start):
                        result.remove(existing)
                        result.append(finding)
                    break
            if not overlaps:
                result.append(finding)
        return result

    def _extract_metadata(self, value: str) -> dict[str, object]:
        return {"normalized": self._normalize_phone(value)}