from fastpii.patterns.base import PatternDefinition

PESEL_SCORE = 0.95
NIP_SCORE = 0.90
REGON_SCORE = 0.85
POSTAL_CODE_SCORE = 0.90
PHONE_MOBILE_SCORE = 0.95
PHONE_LANDLINE_SCORE = 0.85
EMAIL_SCORE = 0.95


class PolishPatternLoader:
    REGION_CODE: str = "pl"
    REGION_NAME: str = "Poland"
    LANGUAGE_CODES: list[str] = ["pl", "pl-PL"]

    @staticmethod
    def load() -> list[PatternDefinition]:
        patterns: list[PatternDefinition] = []

        patterns.append(PatternDefinition(
            entity_type="pesel",
            name="standard",
            regex=r"\b(\d{11})\b",
            region="pl",
            score=PESEL_SCORE,
            context_words=["PESEL", "pesel", "numer PESEL", "identyfikacji"],
            validation_regex=r"^\d{11}$",
        ))

        patterns.append(PatternDefinition(
            entity_type="nip",
            name="standard",
            regex=r"\b(\d{10})\b",
            region="pl",
            score=NIP_SCORE,
            context_words=["NIP", "nip", "numer identyfikacji podatkowej", "VAT"],
            validation_regex=r"^\d{10}$",
        ))

        patterns.append(PatternDefinition(
            entity_type="regon",
            name="standard",
            regex=r"\b(\d{9}|\d{14})\b",
            region="pl",
            score=REGON_SCORE,
            context_words=["REGON", "regon", "rejestr gospodarki"],
            validation_regex=r"^\d{9}(\d{5})?$",
        ))

        patterns.append(PatternDefinition(
            entity_type="postal_code",
            name="standard",
            regex=r"\b(\d{2})[-\s]?(\d{3})\b",
            region="pl",
            score=POSTAL_CODE_SCORE,
            context_words=["kod pocztowy", "postal code", "zip"],
            validation_regex=r"^\d{2}[-\s]?\d{3}$",
            extraction_regex=r"^(\d{2})[-\s]?(\d{3})$",
        ))

        patterns.append(PatternDefinition(
            entity_type="phone",
            name="mobile",
            regex=r"(?<!\d)(?:\+48[\s-]?)?(?:45|50|51|52|53|54|55|56|57|58|60|66|69|72|73|78|79|88)\d[\s-]?\d{3}[\s-]?\d{3}(?!\d)",
            region="pl",
            score=PHONE_MOBILE_SCORE,
            context_words=["tel", "telefon", "komórka", "phone", "mobile", "contact", "numer"],
        ))

        patterns.append(PatternDefinition(
            entity_type="phone",
            name="landline",
            regex=r"(?<!\d)(?:\+48[\s-]?)?(?:1[2-9]|2[2-9]|3[2-9]|4[2-9]|5[2-9]|6[2-9]|7[2-9]|8[2-9]|9[2-9])[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}(?!\d)",
            region="pl",
            score=PHONE_LANDLINE_SCORE,
            context_words=["tel", "telefon", "stacjonarny", "landline", "contact", "numer"],
        ))

        patterns.append(PatternDefinition(
            entity_type="email",
            name="standard",
            regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            region="pl",
            score=EMAIL_SCORE,
            context_words=["email", "e-mail", "@"],
            validation_regex=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        ))

        return patterns

    @staticmethod
    def get_metadata() -> dict[str, object]:
        return {
            "region_code": "pl",
            "region_name": "Poland",
            "language_codes": ["pl", "pl-PL"],
            "iso_3166_code": "PL",
            "entity_types": ["pesel", "nip", "regon", "postal_code", "phone", "email"],
            "has_checksum_validation": True,
            "checksum_algorithms": ["validate_pesel", "validate_nip", "validate_regon"],
        }