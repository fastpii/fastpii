from fastpii.patterns.base import PatternDefinition

SIREN_SCORE = 0.90
SIRET_SCORE = 0.95
INSEE_SCORE = 0.95
POSTAL_CODE_SCORE = 0.85
PHONE_MOBILE_SCORE = 0.95
PHONE_LANDLINE_SCORE = 0.85
EMAIL_SCORE = 0.95


class FrenchPatternLoader:
    REGION_CODE: str = "fr"
    REGION_NAME: str = "France"
    LANGUAGE_CODES: list[str] = ["fr", "fr-FR"]

    @staticmethod
    def load() -> list[PatternDefinition]:
        patterns: list[PatternDefinition] = []

        patterns.append(PatternDefinition(
            entity_type="siren",
            name="standard",
            regex=r"\b(\d{9})\b",
            region="fr",
            score=SIREN_SCORE,
            context_words=["SIREN", "siren", "numéro SIREN", "company ID"],
            validation_regex=r"^\d{9}$",
        ))

        patterns.append(PatternDefinition(
            entity_type="siret",
            name="standard",
            regex=r"\b(\d{14})\b",
            region="fr",
            score=SIRET_SCORE,
            context_words=["SIRET", "siret", "numéro SIRET", "establishment"],
            validation_regex=r"^\d{14}$",
        ))

        patterns.append(PatternDefinition(
            entity_type="insee",
            name="standard",
            regex=r"\b([12]\d{2}(?:0[1-9]|1[0-2])(?:\d{2}|2[ABab])\d{8})\b",
            region="fr",
            score=INSEE_SCORE,
            context_words=["INSEE", "NIR", "numéro de sécurité sociale", "numéro social", "SS"],
            validation_regex=r"^[12]\d{2}(?:0[1-9]|1[0-2])(?:\d{2}|2[ABab])\d{8}$",
        ))

        patterns.append(PatternDefinition(
            entity_type="postal_code",
            name="standard",
            regex=r"\b(\d{5})\b",
            region="fr",
            score=POSTAL_CODE_SCORE,
            context_words=["code postal", "postal code", "CP"],
            validation_regex=r"^\d{5}$",
        ))

        patterns.append(PatternDefinition(
            entity_type="phone",
            name="mobile",
            regex=r"(?<!\d)(?:\+33[\s-]?|0)(?:6|7)[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}(?!\d)",
            region="fr",
            score=PHONE_MOBILE_SCORE,
            context_words=["tel", "téléphone", "mobile", "portable", "phone", "contact", "numéro"],
        ))

        patterns.append(PatternDefinition(
            entity_type="phone",
            name="landline",
            regex=r"(?<!\d)(?:\+33[\s-]?|0)[1-5][\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}(?!\d)",
            region="fr",
            score=PHONE_LANDLINE_SCORE,
            context_words=["tel", "téléphone", "fixe", "landline", "contact", "numéro"],
        ))

        patterns.append(PatternDefinition(
            entity_type="email",
            name="standard",
            regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            region="fr",
            score=EMAIL_SCORE,
            context_words=["email", "e-mail", "courriel", "@"],
            validation_regex=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        ))

        return patterns

    @staticmethod
    def get_metadata() -> dict[str, object]:
        return {
            "region_code": "fr",
            "region_name": "France",
            "language_codes": ["fr", "fr-FR"],
            "iso_3166_code": "FR",
            "entity_types": ["siren", "siret", "insee", "postal_code", "phone", "email"],
            "has_checksum_validation": True,
            "checksum_algorithms": ["validate_siren", "validate_siret", "validate_insee"],
        }
