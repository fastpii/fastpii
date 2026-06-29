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
from fastpii.countries.cz.data.names import CzechNamesData
from fastpii.countries.cz.data.surnames import CzechSurnamesData


class NameDetector(Detector):

    HEADING_WORDS: ClassVar[set[str]] = {
        "information",
        "details",
        "vehicle",
        "customer",
        "company",
        "business",
        "account",
        "alternative",
        "additional",
        "employees",
        "registered",
        "office",
        "notes",
        "tests",
        "false",
        "positive",
        "number",
        "report",
        "summary",
        "overview",
    }

    CONFIDENCE_SURNAME_DICT: float = 0.95
    CONFIDENCE_SURNAME_OVOVA: float = 0.90
    CONFIDENCE_UNKNOWN_SURNAME: float = 0.70
    MIN_CONFIDENCE: float = 0.5

    NAME_PATTERN: re.Pattern[str] = re.compile(
        r'\b([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+)[^\S\n]+([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]{2,}(?:ová|ova|ý|á|ý|ec|ek)?)\b'
    )
    registry: PatternRegistry
    names_data: CzechNamesData
    surnames_data: CzechSurnamesData
    male_first_names: set[str]
    female_first_names: set[str]
    male_surnames: set[str]
    female_surnames: set[str]

    def __init__(self, registry: PatternRegistry | None = None, names_data: CzechNamesData | None = None, surnames_data: CzechSurnamesData | None = None) -> None:
        super().__init__(
            name="name",
            region="cz",
            description="Czech personal name detector with gender classification"
        )
        self.registry = registry or get_shared_registry()
        self.names_data = names_data or CzechNamesData()
        self.surnames_data = surnames_data or CzechSurnamesData()
        loaded_names = self.names_data.get_data()
        self.male_first_names = loaded_names["male"]
        self.female_first_names = loaded_names["female"]
        loaded_surnames = self.surnames_data.get_data()
        self.male_surnames = loaded_surnames["male"]
        self.female_surnames = loaded_surnames["female"]

    @override
    def detect(self, text: str) -> list[Finding]:
        findings: list[Finding] = []

        for match in self.NAME_PATTERN.finditer(text):
            firstname = match.group(1)
            surname = match.group(2)
            full_name = match.group(0)
            matched_words = {firstname.lower(), surname.lower()}

            if matched_words & self.HEADING_WORDS:
                continue

            gender = self._classify_gender(firstname, surname)
            confidence = self._calculate_confidence(firstname, surname)

            if confidence < self.MIN_CONFIDENCE:
                continue

            metadata: dict[str, object] = {
                "firstname": firstname,
                "surname": surname,
                "gender": gender,
                "full_name": full_name,
            }

            if gender == 'f' and surname.lower().endswith(('ová', 'ova')):
                metadata["marital_status"] = "married"

            findings.append(Finding(
                type="name",
                value=full_name,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
                region="cz",
                metadata=metadata
            ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        if not value:
            return False

        parts = value.strip().split()
        if len(parts) < 2:
            return False

        firstname, surname = parts[0], parts[-1]

        if not firstname[0].isupper() or not surname[0].isupper():
            return False

        czech_alpha_pattern = re.compile(r'^[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+$')

        if not czech_alpha_pattern.match(firstname):
            return False

        if not czech_alpha_pattern.match(surname):
            return False

        return True

    def _classify_gender(self, firstname: str, surname: str) -> str:
        firstname_lower = firstname.lower()
        surname_lower = surname.lower()

        if surname_lower.endswith(('ová', 'ova')):
            return 'f'

        if surname_lower in self.female_surnames:
            return 'f'
        elif surname_lower in self.male_surnames:
            return 'm'

        gender = self.classify_gender_by_firstname(firstname)
        if gender:
            return gender

        if firstname_lower.endswith(('a', 'e', 'ě')):
            return 'f'

        return 'm'

    def _calculate_confidence(self, firstname: str, surname: str) -> float:
        firstname_lower = firstname.lower()
        surname_lower = surname.lower()
        firstname_in_dictionary = firstname_lower in self.male_first_names or firstname_lower in self.female_first_names or firstname_lower in self.male_surnames or firstname_lower in self.female_surnames
        surname_in_dictionary = surname_lower in self.male_first_names or surname_lower in self.female_first_names or surname_lower in self.male_surnames or surname_lower in self.female_surnames

        if not firstname_in_dictionary and not surname_in_dictionary and not surname_lower.endswith(('ová', 'ova')):
            return 0.0

        firstname_confidence = self.get_name_confidence(firstname)

        if surname_lower in self.male_surnames or surname_lower in self.female_surnames:
            surname_confidence = self.CONFIDENCE_SURNAME_DICT
        elif surname_lower.endswith(('ová', 'ova')):
            surname_confidence = self.CONFIDENCE_SURNAME_OVOVA
        else:
            surname_confidence = self.CONFIDENCE_UNKNOWN_SURNAME

        return (firstname_confidence + surname_confidence) / 2

    def classify_gender_by_firstname(self, firstname: str) -> str | None:
        name_lower = firstname.lower().strip()

        if name_lower in self.male_first_names:
            return 'm'
        elif name_lower in self.female_first_names:
            return 'f'
        else:
            if name_lower.endswith('a') or name_lower.endswith('e') or name_lower.endswith('ě'):
                return 'f'
            else:
                return 'm'

    def get_name_confidence(self, name: str) -> float:
        name_lower = name.lower().strip()

        if name_lower in self.male_first_names or name_lower in self.female_first_names:
            return 0.95
        elif name_lower.endswith('a') or name_lower.endswith('e'):
            return 0.75
        elif name_lower[-1] not in 'aeěyi':
            return 0.70
        else:
            return 0.50