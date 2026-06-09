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


class PhoneNumberDetector(Detector):
    # Context words that indicate a phone number follows
    CONTEXT_WORDS: tuple[str, ...] = (
        "phone",
        "tel",
        "telefon",
        "mobil",
        "mobile",
        "phone:",
        "tel:",
        "contact",
        "number",
        "numbers",
        "číslo",
    )

    # Backward compatibility: expose pattern constants
    MOBILE_PATTERN: str = r"(?<!\d)(?:\+420[\s-]?)?(?:60[1-8]|7\d{2})[\s-]?\d{3}[\s-]?\d{3}(?!\d)"
    LANDLINE_PATTERN: str = r"(?<!\d)(?:\+420[\s-]?)?[2-5][\s-]?\d{4}[\s-]?\d{4}(?!\d)"

    registry: PatternRegistry
    _context_regex = re.compile(
        r"(?i)\b(?:phone|tel|telefon|mobil|mobile|contact|numbers?|číslo)\b\s*:?"
    )
    _bank_account_regex = re.compile(r"\d{1,6}-\d{1,10}/\d{4}|\d{1,10}/\d{4}")

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="phone",
            region="cz",
            description="Czech phone number detector (mobile and landline)"
        )
        # Use shared registry if none provided (singleton pattern)
        self.registry = registry or get_shared_registry()

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("phone", "cz")
        if not patterns:
            return []
        
        findings: list[Finding] = []

        for pattern_def in patterns:  # Process all variants (mobile, landline)
            for match in pattern_def.compiled.finditer(text):
                phone_type = "mobile" if pattern_def.name == "mobile" else "landline"
                raw_phone = match.group(0)
                phone_start = match.start()
                phone_end = match.end()

                if not self._is_valid_phone_match(text, raw_phone, phone_start, phone_end):
                    continue

                normalized_value = self._normalize_phone(raw_phone)
                
                metadata: dict[str, object] = {"phone_type": phone_type}
                
                if phone_type == "mobile":
                    # Extract prefix for operator detection
                    prefix = self._extract_mobile_prefix(normalized_value)
                    metadata["operator"] = self._get_mobile_operator(prefix)
                else:
                    # Extract area code for area detection
                    area_code = self._extract_landline_area(normalized_value)
                    metadata["area"] = self._get_landline_area(area_code)
                
                findings.append(Finding(
                    type="phone",
                    value=normalized_value,
                    start=phone_start,
                    end=phone_end,
                    confidence=pattern_def.score,
                    region="cz",
                    metadata=metadata
                ))

        # Deduplicate overlapping matches (e.g., "+420 777 123 456" and "777 123 456")
        findings = self._deduplicate_findings(findings)

        return findings

    @override
    def validate(self, value: str) -> bool:
        cleaned = self._normalize_phone(value)
        
        if not cleaned.isdigit():
            return False
        
        if cleaned.startswith("420"):
            cleaned = cleaned[3:]
        
        if cleaned.startswith("60") or cleaned.startswith("7"):
            return len(cleaned) == 9 and cleaned[0] in ['6', '7']
        elif cleaned[0] in ['2', '3', '4', '5']:
            return len(cleaned) == 9
        
        return False

    def _extract_mobile_prefix(self, normalized: str) -> str:
        """Extract mobile prefix from normalized phone (420XXXXXXXXX or XXXXXXXXX)."""
        if normalized.startswith("420") and len(normalized) == 12:
            return normalized[3:6]
        elif len(normalized) == 9:
            return normalized[:3]
        return ""

    def _extract_landline_area(self, normalized: str) -> str:
        """Extract landline area code from normalized phone."""
        if normalized.startswith("420") and len(normalized) == 12:
            return normalized[3]
        elif len(normalized) == 9:
            return normalized[0]
        return ""

    def _is_valid_phone_match(self, text: str, raw_phone: str, start: int, end: int) -> bool:
        # 1. Boundary check: must not be inside a larger digit sequence
        if start > 0 and text[start - 1].isdigit():
            return False

        if end < len(text) and text[end].isdigit():
            return False

        # 2. Must not be inside a bank account pattern
        if self._is_inside_bank_account(text, start, end):
            return False

        # 3. If starts with +420, accept unconditionally
        if raw_phone.lstrip().startswith("+420"):
            return True

        # 4. No +420 prefix: require context word within 50 chars before
        context_start = max(0, start - 50)
        context_window = text[context_start:start]
        return bool(self._context_regex.search(context_window))

    def _is_inside_bank_account(self, text: str, start: int, end: int) -> bool:
        window_start = max(0, start - 20)
        window_end = min(len(text), end + 10)
        window = text[window_start:window_end]

        for bank_match in self._bank_account_regex.finditer(window):
            absolute_start = window_start + bank_match.start()
            absolute_end = window_start + bank_match.end()
            if absolute_start <= start and end <= absolute_end:
                return True

        return False

    def _deduplicate_findings(self, findings: list[Finding]) -> list[Finding]:
        """Remove overlapping phone matches, keeping the longer/more specific one."""
        if not findings:
            return findings

        # Sort by position
        sorted_findings = sorted(findings, key=lambda f: f.start)
        
        result: list[Finding] = []
        for finding in sorted_findings:
            # Check if this overlaps with any accepted finding
            overlaps = False
            for existing in result:
                if finding.start < existing.end and finding.end > existing.start:
                    overlaps = True
                    # Keep the longer match (more specific, e.g. "+420 777 123 456" > "777 123 456")
                    if (finding.end - finding.start) > (existing.end - existing.start):
                        result.remove(existing)
                        result.append(finding)
                    break
            if not overlaps:
                result.append(finding)

        return result

    def _normalize_phone(self, phone: str) -> str:
        cleaned = phone.replace(' ', '').replace('-', '')
        
        if cleaned.startswith('+'):
            return cleaned[1:]
        
        if not cleaned.startswith('420') and len(cleaned) == 9:
            return f"420{cleaned}"
        
        return cleaned

    def _get_mobile_operator(self, prefix: str) -> str:
        if prefix.startswith('601') or prefix.startswith('602') or prefix.startswith('603'):
            return "O2"
        elif prefix.startswith('604') or prefix.startswith('605') or prefix.startswith('607'):
            return "T-Mobile"
        elif prefix.startswith('606') or prefix.startswith('608') or prefix.startswith('77'):
            return "Vodafone"
        elif prefix.startswith('70') or prefix.startswith('79'):
            return "T-Mobile"
        elif prefix.startswith('72') or prefix.startswith('73'):
            return "Vodafone"
        else:
            return "other"

    def _get_landline_area(self, prefix: str) -> str:
        area_map = {
            '2': "Praha",
            '3': "Pardubice/Hradec Králové",
            '4': "Plzeň",
            '5': "Brno/Olomouc"
        }
        return area_map.get(prefix, "other")