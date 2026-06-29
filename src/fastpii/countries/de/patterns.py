from fastpii.patterns.base import PatternDefinition

STEUER_ID_SCORE = 0.95
UST_ID_SCORE = 0.95
HANDELSREGISTER_SCORE = 0.90
POSTAL_CODE_SCORE = 0.90
PHONE_SCORE = 0.85
EMAIL_SCORE = 0.95


class GermanPatternLoader:
    REGION_CODE: str = "de"
    REGION_NAME: str = "Germany"
    LANGUAGE_CODES: list[str] = ["de", "de-DE"]

    @staticmethod
    def load() -> list[PatternDefinition]:
        patterns: list[PatternDefinition] = []

        patterns.append(PatternDefinition(
            entity_type="steuer_id",
            name="standard",
            regex=r"\b(\d{11})\b",
            region="de",
            score=STEUER_ID_SCORE,
            context_words=["Steuer-ID", "Steueridentifikationsnummer", "IdNr", "tax ID", "Steuernummer"],
            validation_regex=r"^\d{11}$",
        ))

        patterns.append(PatternDefinition(
            entity_type="ust_id",
            name="standard",
            regex=r"\bDE(\d{9})\b",
            region="de",
            score=UST_ID_SCORE,
            context_words=["USt-IdNr", "Umsatzsteuer-Identifikationsnummer", "VAT", "MwSt"],
            validation_regex=r"^\d{9}$",
            extraction_regex=r"^(\d{9})$",
        ))

        patterns.append(PatternDefinition(
            entity_type="handelsregister",
            name="standard",
            regex=r"\b((?:[A-ZÄÖÜa-zäöü./]+\s+)?(?:HRA|HRB|PR|GnR|VR)\s+\d{1,6}(?:\s+[A-ZÄÖÜa-zäöü.&]+)?)\b",
            region="de",
            score=HANDELSREGISTER_SCORE,
            context_words=["Handelsregister", "HRB", "HRA", "Register", "Registernummer"],
        ))

        patterns.append(PatternDefinition(
            entity_type="postal_code",
            name="standard",
            regex=r"\b(\d{5})\b",
            region="de",
            score=POSTAL_CODE_SCORE,
            context_words=["PLZ", "Postleitzahl", "postal code", "zip"],
            validation_regex=r"^\d{5}$",
        ))

        patterns.append(PatternDefinition(
            entity_type="phone",
            name="standard",
            regex=r"(?<!\d)(?:\+49[\s-]?|0)(?:15[1279]|16[023]|17[0-9]|2\d{1,4}|3\d{1,4}|4\d{1,4}|5\d{1,4}|6\d{1,4}|7\d{1,4}|8\d{1,4}|9\d{1,4})[\s-]?\d{3,12}(?!\d)",
            region="de",
            score=PHONE_SCORE,
            context_words=["Tel", "Telefon", "Handy", "phone", "mobile", "Anruf", "Rufnummer"],
        ))

        patterns.append(PatternDefinition(
            entity_type="email",
            name="standard",
            regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            region="de",
            score=EMAIL_SCORE,
            context_words=["E-Mail", "email", "@"],
            validation_regex=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        ))

        return patterns

    @staticmethod
    def get_metadata() -> dict[str, object]:
        return {
            "region_code": "de",
            "region_name": "Germany",
            "language_codes": ["de", "de-DE"],
            "iso_3166_code": "DE",
            "entity_types": ["steuer_id", "ust_id", "handelsregister", "postal_code", "phone", "email"],
            "has_checksum_validation": True,
            "checksum_algorithms": ["validate_steuer_id", "validate_ust_id"],
        }
