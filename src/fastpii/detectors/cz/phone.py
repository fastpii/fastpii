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
    # Backward compatibility: expose pattern constants
    MOBILE_PATTERN: str = r'(?:\+420[\s-]?)?(?:60[0-8]|7[0-9]\d)\d{6}'
    LANDLINE_PATTERN: str = r'(?:\+420[\s-]?)?[2-5](?:\s?\d{3}){2}\s?\d{2}'
    registry: PatternRegistry

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
                normalized_value = self._normalize_phone(match.group(0))
                
                metadata: dict[str, object] = {"phone_type": phone_type}
                
                if phone_type == "mobile":
                    # Extract prefix for operator detection
                    prefix = match.group(1) if len(match.groups()) > 0 else ""
                    metadata["operator"] = self._get_mobile_operator(prefix)
                else:
                    # Extract area code for area detection
                    area_code = match.group(1) if len(match.groups()) > 0 else ""
                    metadata["area"] = self._get_landline_area(area_code)
                
                findings.append(Finding(
                    type="phone",
                    value=normalized_value,
                    start=match.start(),
                    end=match.end(),
                    confidence=pattern_def.score,
                    region="cz",
                    metadata=metadata
                ))

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
