import re
from typing import Any

from cpg.detectors.base import Detector
from cpg.models import Finding


class PostalCodeDetector(Detector):
    CZECH_POSTAL_CODE_PATTERN = r'\b(\d{3})\s?(\d{2})\b'
    
    PRAGUE_CODES = {"110", "111", "112", "113", "114", "115", "116", "117", "118", "119", "120", "121", "122", "123", "124", "125", "126", "127", "128", "129", "130", "131", "132", "133", "134", "135", "136", "137", "138", "139", "140", "141", "142", "143", "144", "145", "146", "147", "148", "149", "150", "151", "152", "153", "154", "155", "156", "157", "158", "159", "160", "161", "162", "163", "164", "165", "166", "167", "168", "169", "170", "171", "172", "173", "174", "175", "176", "177", "178", "179", "180", "181", "182", "183", "184", "185", "186", "187", "188", "189", "190", "191", "192", "193", "194", "195", "196", "197", "198", "199"}

    def __init__(self) -> None:
        super().__init__(
            name="postal_code",
            region="cz",
            description="Czech postal code (PSČ) detector"
        )

    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []

        for match in re.finditer(self.CZECH_POSTAL_CODE_PATTERN, text):
            prefix = match.group(1)
            suffix = match.group(2)
            value = f"{prefix} {suffix}" if ' ' in match.group(0) else f"{prefix}{suffix}"
            
            if self._is_valid_postal_code(prefix, suffix):
                metadata = self._extract_metadata(prefix, suffix)
                
                findings.append(Finding(
                    type="postal_code",
                    value=value,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95,
                    region="cz",
                    metadata=metadata
                ))

        return findings

    def validate(self, value: str) -> bool:
        cleaned = value.replace(' ', '')
        
        if len(cleaned) != 5:
            return False
        
        if not cleaned.isdigit():
            return False
        
        if cleaned[0] == '0':
            return False
        
        return True

    def _is_valid_postal_code(self, prefix: str, suffix: str) -> bool:
        if not prefix.isdigit() or not suffix.isdigit():
            return False
        
        if len(prefix) != 3 or len(suffix) != 2:
            return False
        
        if prefix[0] == '0':
            return False
        
        return True

    def _extract_metadata(self, prefix: str, suffix: str) -> dict[str, Any]:
        metadata: dict[str, Any] = {}
        
        if prefix in self.PRAGUE_CODES:
            metadata["region"] = "Praha"
        elif prefix.startswith("1"):
            metadata["region"] = "Středočeský"
        elif prefix.startswith("2"):
            metadata["region"] = "Jihočeský"
        elif prefix.startswith("3"):
            metadata["region"] = "Plzeňský"
        elif prefix.startswith("4"):
            metadata["region"] = "Karlovarský"
        elif prefix.startswith("5"):
            metadata["region"] = "Ústecký"
        elif prefix.startswith("6"):
            metadata["region"] = "Liberecký"
        elif prefix.startswith("7"):
            metadata["region"] = "Královéhradecký"
        elif prefix.startswith("8"):
            metadata["region"] = "Pardubický"
        elif prefix.startswith("9"):
            metadata["region"] = "Moravskoslezský"
        else:
            metadata["region"] = "other"
        
        return metadata