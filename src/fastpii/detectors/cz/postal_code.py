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


class PostalCodeDetector(Detector):
    CZECH_POSTAL_CODE_PATTERN: str = r'\b(\d{3})\s?(\d{2})\b'

    PRAGUE_CODES: set[str] = {
        "110", "111", "112", "113", "114", "115", "116", "117", "118", "119",
        "120", "121", "122", "123", "124", "125", "126", "127", "128", "129",
        "130", "131", "132", "133", "134", "135", "136", "137", "138", "139",
        "140", "141", "142", "143", "144", "145", "146", "147", "148", "149",
        "150", "151", "152", "153", "154", "155", "156", "157", "158", "159",
        "160", "161", "162", "163", "164", "165", "166", "167", "168", "169",
        "170", "171", "172", "173", "174", "175", "176", "177", "178", "179",
        "180", "181", "182", "183", "184", "185", "186", "187", "188", "189",
        "190", "191", "192", "193", "194", "195", "196", "197", "198", "199",
    }

    POSTAL_CONTEXT_WORDS: tuple[str, ...] = (
        "psč", "p.s.c", "poštovní", "postal", "zip", "postcode", "post code",
    )

    CONTEXT_CHARS: int = 30
    COMMA_CONTEXT_CHARS: int = 5
    CONTEXT_CONFIDENCE: float = 0.95
    NO_CONTEXT_CONFIDENCE: float = 0.80

    _context_regex = re.compile(
        r"(?i)\b(?:psč|p\.s\.c|poštovní|postal|zip|postcode|post\s*code)\b\s*:?"
    )

    _city_regex = re.compile(
        r"(?i)\b(?:Praha|Brno|Ostrava|Plzeň|Liberec|Olomouc|České\s+Budějovice|"
        r"Hradec\s+Králové|Pardubice|Ústí\s+nad\s+Labem|Zlín|Karlovy\s+Vary|"
        r"Jihlava|Tábor|Český\s+Krumlov|Kladno|Mladá\s+Boleslav|Děčín|"
        r"Kroměříž|Hodonín|Znojmo|Břeclav|Beroun|Kolín|Příbram|Šumperk|"
        r"Trutnov|Cheb|Opava|Havířov|Třinec|Třebíč|Vsetín|Blansko)\b"
    )

    registry: PatternRegistry

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="postal_code",
            region="cz",
            description="Czech postal code (PSČ) detector"
        )
        self.registry = registry or get_shared_registry()

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("postal_code", "cz")
        if not patterns:
            return []

        pattern_def = patterns[0]
        findings: list[Finding] = []

        for match in pattern_def.compiled.finditer(text):
            prefix = match.group(1)
            suffix = match.group(2)
            value = f"{prefix} {suffix}" if ' ' in match.group(0) else f"{prefix}{suffix}"

            if not self._is_valid_postal_code(prefix, suffix):
                continue

            if not self._has_valid_context(text, match.start(), match.end(), value):
                continue

            metadata = self._extract_metadata(value)

            confidence = self._calculate_confidence(text, match.start())

            findings.append(Finding(
                type="postal_code",
                value=value,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                region="cz",
                metadata=metadata
            ))

        return findings

    @override
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

    def _has_valid_context(self, text: str, start: int, end: int, value: str) -> bool:
        context_start = max(0, start - self.CONTEXT_CHARS)
        before_window = text[context_start:start]
        if self._context_regex.search(before_window):
            return True

        after_end = min(len(text), end + self.CONTEXT_CHARS)
        after_window = text[end:after_end]
        if self._city_regex.search(after_window):
            return True

        before_5 = text[max(0, start - self.COMMA_CONTEXT_CHARS):start]
        if before_5.rstrip().endswith(','):
            return True

        if ' ' in value:
            return True

        return False

    def _calculate_confidence(self, text: str, position: int) -> float:
        context_start = max(0, position - self.CONTEXT_CHARS)
        before_window = text[context_start:position]

        if self._context_regex.search(before_window):
            return self.CONTEXT_CONFIDENCE

        return self.NO_CONTEXT_CONFIDENCE

    def _extract_metadata(self, value: str) -> dict[str, object]:
        cleaned = value.replace(' ', '')
        prefix = cleaned[:3]

        metadata: dict[str, object] = {}

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