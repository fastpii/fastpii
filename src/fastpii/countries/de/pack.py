from fastpii.countries import CountryPack, register_country
from fastpii.countries.base import CountryMetadata, EntityDefinition
from fastpii.detectors.base import Detector
from fastpii.detectors.de import (
    SteuerIdDetector,
    UStIdNrDetector,
    HandelsregisterDetector,
    GermanPostalCodeDetector,
    GermanPhoneDetector,
    GermanAddressDetector,
)


__all__ = ["GERMAN_METADATA", "GERMAN_ENTITIES", "GermanPack"]


GERMAN_METADATA = CountryMetadata(
    code="de",
    name="Germany",
    official_name="Bundesrepublik Deutschland",
    language_codes=("de", "de-DE"),
    iso_3166_alpha2="DE",
    iso_3166_alpha3="DEU",
    currency_code="EUR",
)

GERMAN_ENTITIES: list[EntityDefinition] = [
    EntityDefinition(
        entity_type="steuer_id",
        display_name="Steuer-ID",
        description="German tax identification number",
        region="de",
        has_checksum=True,
        context_words=("Steuer-ID", "IdNr", "tax ID"),
        examples=("86095742719",),
        invalid_examples=("86095742710",),
    ),
    EntityDefinition(
        entity_type="ust_id",
        display_name="USt-IdNr",
        description="German VAT identification number",
        region="de",
        has_checksum=True,
        context_words=("USt-IdNr", "VAT"),
        examples=("DE136695976",),
        invalid_examples=("DE123456789",),
    ),
    EntityDefinition(
        entity_type="handelsregister",
        display_name="Handelsregister",
        description="German commercial register number",
        region="de",
        has_checksum=False,
        context_words=("Handelsregister", "HRB"),
        examples=("München HRB 12345",),
        invalid_examples=("XYZ",),
    ),
    EntityDefinition(
        entity_type="postal_code",
        display_name="PLZ",
        description="German postal code",
        region="de",
        has_checksum=False,
        context_words=("PLZ", "Postleitzahl"),
        examples=("10115",),
        invalid_examples=("00000",),
    ),
    EntityDefinition(
        entity_type="phone",
        display_name="Telefon",
        description="German phone number",
        region="de",
        has_checksum=False,
        context_words=("Tel", "Telefon"),
        examples=("+49 30 1234567",),
        invalid_examples=("123",),
    ),
    EntityDefinition(
        entity_type="address",
        display_name="Adresse",
        description="German street address",
        region="de",
        has_checksum=False,
        context_words=(),
        examples=("Hauptstraße 12, 10115 Berlin",),
        invalid_examples=("123",),
    ),
]


@register_country
class GermanPack(CountryPack):
    code = "de"

    @property
    def name(self) -> str:
        return "Germany"

    @property
    def metadata(self) -> CountryMetadata:
        return GERMAN_METADATA

    @property
    def detectors(self) -> list[Detector]:
        return [
            SteuerIdDetector(),
            UStIdNrDetector(),
            HandelsregisterDetector(),
            GermanPostalCodeDetector(),
            GermanPhoneDetector(),
            GermanAddressDetector(),
        ]

    @property
    def entities(self) -> list[EntityDefinition]:
        return GERMAN_ENTITIES
