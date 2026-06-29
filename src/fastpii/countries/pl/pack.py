from fastpii.core._compat import override
from fastpii.countries import CountryPack, register_country
from fastpii.countries.base import CountryMetadata, EntityDefinition
from fastpii.detectors.base import Detector
from fastpii.detectors.pl import (
    PeseleDetector,
    NIPDetector,
    REGONDetector,
    PolishPostalCodeDetector,
    PolishPhoneDetector,
    PolishAddressDetector,
)


__all__ = ["POLISH_METADATA", "POLISH_ENTITIES", "PolishPack"]


POLISH_METADATA = CountryMetadata(
    code="pl",
    name="Poland",
    official_name="Rzeczpospolita Polska",
    language_codes=("pl", "pl-PL"),
    iso_3166_alpha2="PL",
    iso_3166_alpha3="POL",
    currency_code="PLN",
)

POLISH_ENTITIES: list[EntityDefinition] = [
    EntityDefinition(
        entity_type="pesel",
        display_name="PESEL",
        description="Polish national identification number",
        region="pl",
        has_checksum=True,
        context_words=("PESEL", "numer PESEL"),
        examples=("44051401458",),
        invalid_examples=("44051401459",),
    ),
    EntityDefinition(
        entity_type="nip",
        display_name="NIP",
        description="Polish tax identification number",
        region="pl",
        has_checksum=True,
        context_words=("NIP", "VAT"),
        examples=("5260250274",),
        invalid_examples=("1234567890",),
    ),
    EntityDefinition(
        entity_type="regon",
        display_name="REGON",
        description="Polish business registry number",
        region="pl",
        has_checksum=True,
        context_words=("REGON",),
        examples=("123456785",),
        invalid_examples=("123456789",),
    ),
    EntityDefinition(
        entity_type="postal_code",
        display_name="Kod pocztowy",
        description="Polish postal code",
        region="pl",
        has_checksum=False,
        context_words=("kod pocztowy",),
        examples=("00-001",),
        invalid_examples=("00000",),
    ),
    EntityDefinition(
        entity_type="phone",
        display_name="Telefon",
        description="Polish phone number",
        region="pl",
        has_checksum=False,
        context_words=("tel", "telefon"),
        examples=("+48 512 345 678",),
        invalid_examples=("123",),
    ),
    EntityDefinition(
        entity_type="address",
        display_name="Adres",
        description="Polish street address",
        region="pl",
        has_checksum=False,
        context_words=(),
        examples=("ul. Długa 15, 00-001 Warszawa",),
        invalid_examples=("123",),
    ),
]


@register_country
class PolishPack(CountryPack):
    code: str = "pl"

    @property
    @override
    def name(self) -> str:
        return "Poland"

    @property
    @override
    def metadata(self) -> CountryMetadata:
        return POLISH_METADATA

    @property
    @override
    def detectors(self) -> list[Detector]:
        return [
            PeseleDetector(),
            NIPDetector(),
            REGONDetector(),
            PolishPostalCodeDetector(),
            PolishPhoneDetector(),
            PolishAddressDetector(),
        ]

    @property
    @override
    def entities(self) -> list[EntityDefinition]:
        return POLISH_ENTITIES
