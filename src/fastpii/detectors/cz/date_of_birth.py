import re
from datetime import datetime

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


class DateOfBirthDetector(Detector):
    CONTEXT_WINDOW: int = 150
    MAX_NEWLINES: int = 5
    CONTEXT_CONFIDENCE: float = 0.95
    NO_CONTEXT_CONFIDENCE: float = 0.70

    MONTH_NAMES: dict[str, int] = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }

    DATE_PATTERN_FULL: re.Pattern[str] = re.compile(
        r'\b(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})\b'
    )
    DATE_PATTERN_TEXTUAL: re.Pattern[str] = re.compile(
        r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',
        re.IGNORECASE,
    )

    BIRTH_CONTEXT_WORDS: set[str] = {
        "narozen", "narozena", "narození", "datum narození",
        "nar.", "dat. nar.", "r.", "rodiven",
        "birth", "born", "date of birth", "dob",
    }
    registry: PatternRegistry

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="date_of_birth",
            region="cz",
            description="Czech date of birth detector"
        )
        self.registry = registry or get_shared_registry()

    @override
    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []

        for match in self.DATE_PATTERN_FULL.finditer(text):
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
            finding = self._build_finding(text, match, day, month, year)
            if finding is not None:
                findings.append(finding)

        for match in self.DATE_PATTERN_TEXTUAL.finditer(text):
            day = int(match.group(1))
            month = self.MONTH_NAMES[match.group(2).lower()]
            year = int(match.group(3))
            finding = self._build_finding(text, match, day, month, year)
            if finding is not None:
                findings.append(finding)

        findings.sort(key=lambda finding: finding.start)

        return findings

    @override
    def validate(self, value: str) -> bool:
        match = self.DATE_PATTERN_FULL.match(value.strip())
        if not match:
            return False

        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))

        return self._is_valid_date(day, month, year)

    def _is_valid_date(self, day: int, month: int, year: int) -> bool:
        if month < 1 or month > 12:
            return False
        if day < 1 or day > 31:
            return False
        if year < 1900 or year > datetime.now().year + 2:
            return False

        days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        if month == 2:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                days_in_month[2] = 29

        if day > days_in_month[month]:
            return False

        return True

    def _calculate_confidence(self, text: str, _position: int, _match_value: str) -> float:
        if self._has_birth_context_nearby(text, _position):
            return self.CONTEXT_CONFIDENCE

        return self.NO_CONTEXT_CONFIDENCE

    def _has_birth_context_nearby(self, text: str, position: int) -> bool:
        window_start = max(0, position - self.CONTEXT_WINDOW)

        newline_count = 0
        line_start = -1
        for i in range(position - 1, max(0, window_start - 1), -1):
            if text[i] == '\n':
                newline_count += 1
                if newline_count == self.MAX_NEWLINES:
                    line_start = i + 1
                    break

        if line_start != -1:
            window_start = min(window_start, line_start)

        context_window = text[window_start:position].lower()

        for word in self.BIRTH_CONTEXT_WORDS:
            if word in context_window:
                context_pos = context_window.rfind(word)
                after_context = context_window[context_pos + len(word):]
                if re.search(r'\d{1,2}\.\s*\d{1,2}\.\s*\d{4}', after_context):
                    return False
                return True

        return False

    def _build_finding(
        self,
        text: str,
        match: re.Match[str],
        day: int,
        month: int,
        year: int,
    ) -> Finding | None:
        if not self._is_valid_date(day, month, year):
            return None

        has_birth_context = self._has_birth_context_nearby(text, match.start())
        confidence = self._calculate_confidence(text, match.start(), match.group(0))
        metadata = self._extract_metadata(day, month, year)

        return Finding(
            type="date_of_birth" if has_birth_context else "date",
            value=match.group(0),
            start=match.start(),
            end=match.end(),
            confidence=confidence,
            region="cz",
            metadata=metadata,
        )

    def _extract_metadata(self, day: int, month: int, year: int) -> dict[str, object]:
        today = datetime.now()
        age = today.year - year
        if (today.month, today.day) < (month, day):
            age -= 1

        iso_date = f"{year:04d}-{month:02d}-{day:02d}"

        metadata: dict[str, object] = {
            "day": day,
            "month": month,
            "year": year,
            "iso_date": iso_date,
            "age": age if age >= 0 else None,
        }

        metadata["zodiac_sign"] = self._get_zodiac_sign(day, month)

        return metadata

    @staticmethod
    def _get_zodiac_sign(day: int, month: int) -> str:
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "aries"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "taurus"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return "gemini"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return "cancer"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "leo"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "virgo"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "libra"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "scorpio"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "sagittarius"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "capricorn"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "aquarius"
        else:
            return "pisces"