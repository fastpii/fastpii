import re
from typing import Any

from fastpii.detectors.base import Detector
from fastpii.models import Finding


class PhoneNumberDetector(Detector):
    MOBILE_PATTERN = r'(?:\+420\s?)?(?:60[0-8]|7[0-9]\d)\d{6}'
    LANDLINE_PATTERN = r'(?:\+420\s?)?[2-5](?:\s?\d{3}){2}\s?\d{2}'

    def __init__(self) -> None:
        super().__init__(
            name="phone",
            region="cz",
            description="Czech phone number detector (mobile and landline)"
        )

    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []

        mobile_matches = self._detect_mobile(text)
        landline_matches = self._detect_landline(text)
        
        findings.extend(mobile_matches)
        findings.extend(landline_matches)

        return findings

    def _detect_mobile(self, text: str) -> list[Finding]:
        findings: list[Finding] = []
        
        mobile_regex = r'(?:\+420[\s-]?)?(60[1-8]|7[0-9]\d)[\s-]?(\d{3})[\s-]?(\d{3})'
        
        for match in re.finditer(mobile_regex, text):
            prefix = match.group(1)
            normalized_value = self._normalize_phone(match.group(0))
            
            metadata = {
                "phone_type": "mobile",
                "operator": self._get_mobile_operator(prefix)
            }
            
            findings.append(Finding(
                type="phone",
                value=normalized_value,
                start=match.start(),
                end=match.end(),
                confidence=0.95,
                region="cz",
                metadata=metadata
            ))

        return findings

    def _detect_landline(self, text: str) -> list[Finding]:
        findings: list[Finding] = []
        
        landline_regex = r'(?:\+420[\s-]?)?([2-5])(\d{3})[\s-]?(\d{3})[\s-]?(\d{2})'
        
        for match in re.finditer(landline_regex, text):
            normalized_value = self._normalize_phone(match.group(0))
            
            metadata = {
                "phone_type": "landline",
                "area": self._get_landline_area(match.group(1))
            }
            
            findings.append(Finding(
                type="phone",
                value=normalized_value,
                start=match.start(),
                end=match.end(),
                confidence=0.90,
                region="cz",
                metadata=metadata
            ))

        return findings

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