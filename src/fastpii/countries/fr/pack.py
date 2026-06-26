from fastpii.countries import CountryPack, register_country
from fastpii.countries.base import CountryMetadata, EntityDefinition
from fastpii.detectors.base import Detector
from fastpii.detectors.fr import (
    SIRENDetector,
    SIRETDetector,
    INSEEDetector,
    FrenchPostalCodeDetector,
    FrenchPhoneDetector,
    FrenchAddressDetector,
)


FRENCH_METADATA = CountryMetadata(
    code="fr",
    name="France",
    official_name="République française",
    language_codes=("fr", "fr-FR"),
    iso_3166_alpha2="FR",
    iso_3166_alpha3="FRA",
    currency_code="EUR",
)

FRENCH_ENTITIES: list[EntityDefinition] = [
    EntityDefinition(
        entity_type="siren",
        display_name="SIREN",
        description="French business identification number",
        region="fr",
        has_checksum=True,
        context_words=("SIREN",),
        examples=("552120222",),
        invalid_examples=("552120223",),
    ),
    EntityDefinition(
        entity_type="siret",
        display_name="SIRET",
        description="French establishment identification number",
        region="fr",
        has_checksum=True,
        context_words=("SIRET",),
        examples=("73282932000074",),
        invalid_examples=("73282932000075",),
    ),
    EntityDefinition(
        entity_type="insee",
        display_name="INSEE/NIR",
        description="French national identification number",
        region="fr",
        has_checksum=True,
        context_words=("INSEE", "NIR", "sécurité sociale"),
        examples=(),
        invalid_examples=(),
    ),
    EntityDefinition(
        entity_type="postal_code",
        display_name="Code postal",
        description="French postal code",
        region="fr",
        has_checksum=False,
        context_words=("code postal",),
        examples=("75001",),
        invalid_examples=("00000",),
    ),
    EntityDefinition(
        entity_type="phone",
        display_name="Téléphone",
        description="French phone number",
        region="fr",
        has_checksum=False,
        context_words=("tel", "téléphone", "portable"),
        examples=("+33 6 12 34 56 78",),
        invalid_examples=("123",),
    ),
    EntityDefinition(
        entity_type="address",
        display_name="Adresse",
        description="French street address",
        region="fr",
        has_checksum=False,
        context_words=(),
        examples=("15 Rue de Rivoli, 75001 Paris",),
        invalid_examples=("123",),
    ),
]


@register_country
class FrenchPack(CountryPack):
    code = "fr"

    @property
    def name(self) -> str:
        return "France"

    @property
    def metadata(self) -> CountryMetadata:
        return FRENCH_METADATA

    @property
    def detectors(self) -> list[Detector]:
        return [
            SIRENDetector(),
            SIRETDetector(),
            INSEEDetector(),
            FrenchPostalCodeDetector(),
            FrenchPhoneDetector(),
            FrenchAddressDetector(),
        ]

    @property
    def entities(self) -> list[EntityDefinition]:
        return FRENCH_ENTITIES