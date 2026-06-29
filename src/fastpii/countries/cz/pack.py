from fastpii.core._compat import override
from fastpii.countries import CountryPack, register_country
from fastpii.countries.base import CountryMetadata, EntityDefinition
from fastpii.detectors.base import Detector
from fastpii.detectors.cz import (
    RodneCisloDetector,
    ICODetector,
    DICDetector,
    BankAccountDetector,
    PostalCodeDetector,
    PhoneNumberDetector,
    EmailDetector,
    NameDetector,
    AddressDetector,
    DateOfBirthDetector,
    VehiclePlateDetector,
    HealthInsuranceDetector,
    IBANDetector,
    CreditCardDetector,
    IdentityCardDetector,
)


__all__ = ["CZECH_METADATA", "CZECH_ENTITIES", "CzechPack"]


CZECH_METADATA = CountryMetadata(
    code="cz",
    name="Czech Republic",
    official_name="Ceská republika",
    language_codes=("cs", "cs-CZ"),
    iso_3166_alpha2="CZ",
    iso_3166_alpha3="CZE",
    currency_code="CZK",
)

CZECH_ENTITIES: list[EntityDefinition] = [
    EntityDefinition(
        entity_type="rodne_cislo",
        display_name="Rodné číslo",
        description="Czech birth number / national ID",
        region="cz",
        has_checksum=True,
        context_words=("rodné číslo", "RČ", "rod. č.", "birth number"),
        examples=("8001011238", "900101/1234"),
        invalid_examples=("8001011239", "000000000"),
    ),
    EntityDefinition(
        entity_type="ico",
        display_name="IČO",
        description="Czech company identification number",
        region="cz",
        has_checksum=True,
        context_words=("IČO", "IČ", "identifikační číslo", "company ID"),
        examples=("25596641", "69663963"),
        invalid_examples=("12345678", "00000000"),
    ),
    EntityDefinition(
        entity_type="dic",
        display_name="DIČ",
        description="Czech VAT identification number",
        region="cz",
        has_checksum=True,
        context_words=("DIČ", "daňové číslo", "VAT", "tax ID"),
        examples=("CZ25596641", "CZ7801233540"),
        invalid_examples=("CZ12345678", "CZ00000000"),
    ),
    EntityDefinition(
        entity_type="bank_account",
        display_name="Bankovní účet",
        description="Czech bank account number",
        region="cz",
        has_checksum=True,
        context_words=("účet", "číslo účtu", "bankovní účet", "bank account"),
        examples=("19-2000145399/0800", "1234567890/0100"),
        invalid_examples=("19-12/0800", "abc/0100"),
    ),
    EntityDefinition(
        entity_type="postal_code",
        display_name="PSČ",
        description="Czech postal code",
        region="cz",
        has_checksum=False,
        context_words=("PSČ", "poštovní směrovací číslo", "postal code", "zip"),
        examples=("120 00", "110 00"),
        invalid_examples=("00000", "123456"),
    ),
    EntityDefinition(
        entity_type="phone",
        display_name="Telefon",
        description="Czech phone number (mobile and landline)",
        region="cz",
        has_checksum=False,
        context_words=("tel", "telefon", "mobil", "phone", "contact"),
        examples=("+420 777 123 456", "+420 221 234 567"),
        invalid_examples=("123", "9999999999"),
    ),
    EntityDefinition(
        entity_type="email",
        display_name="E-mail",
        description="Email address",
        region="cz",
        has_checksum=False,
        context_words=("email", "e-mail", "@"),
        examples=("jan@seznam.cz", "info@firma.cz"),
        invalid_examples=("@domain.cz", "user@"),
    ),
    EntityDefinition(
        entity_type="name",
        display_name="Jméno",
        description="Czech personal name with gender classification",
        region="cz",
        has_checksum=False,
        context_words=(),
        examples=("Jan Novák", "Marie Nováková"),
        invalid_examples=("Praha", "123"),
    ),
    EntityDefinition(
        entity_type="address",
        display_name="Adresa",
        description="Czech street address",
        region="cz",
        has_checksum=False,
        context_words=("adresa", "ulice", "address"),
        examples=("Vinohradská 1523/45, Praha",),
        invalid_examples=("123", "abc"),
    ),
    EntityDefinition(
        entity_type="date_of_birth",
        display_name="Datum narození",
        description="Date of birth with context awareness",
        region="cz",
        has_checksum=False,
        context_words=("narozen", "narozena", "narození", "born", "dob"),
        examples=("15. 3. 1990", "1.1.2000"),
        invalid_examples=("99.99.9999", "32.13.2000"),
    ),
    EntityDefinition(
        entity_type="vehicle_plate",
        display_name="SPZ",
        description="Czech vehicle registration plate",
        region="cz",
        has_checksum=False,
        context_words=("SPZ", "vozidlo", "auto"),
        examples=("1A2 3456", "3B5 7890"),
        invalid_examples=("Q12 3456", "12345"),
    ),
    EntityDefinition(
        entity_type="health_insurance",
        display_name="Zdravotní pojištění",
        description="Czech health insurance number",
        region="cz",
        has_checksum=False,
        context_words=("pojištění", "zdravotní pojišťovna", "pojišťovna", "health insurance", "insurance"),
        examples=("111123456", "201456789"),
        invalid_examples=("999123456", "000000000"),
    ),
    EntityDefinition(
        entity_type="iban",
        display_name="IBAN",
        description="Czech International Bank Account Number",
        region="cz",
        has_checksum=True,
        context_words=("IBAN", "mezinárodní číslo účtu", "international bank account"),
        examples=("CZ0710000000000123456789",),
        invalid_examples=("CZ0010000000000123456789",),
    ),
    EntityDefinition(
        entity_type="credit_card",
        display_name="Kreditní karta",
        description="Credit card number with Luhn checksum",
        region="cz",
        has_checksum=True,
        context_words=("credit card", "card number", "visa", "mastercard", "amex", "kreditní karta"),
        examples=("4111111111111111", "5500000000000004"),
        invalid_examples=("4111111111111112", "0000000000000000"),
    ),
    EntityDefinition(
        entity_type="identity_card",
        display_name="Občanský průkaz",
        description="Czech identity card number",
        region="cz",
        has_checksum=False,
        context_words=("občanský průkaz", "OP", "č. průkazu", "identity card", "ID card"),
        examples=("123456789", "123456AB"),
        invalid_examples=("023456789", "12345"),
    ),
]


@register_country
class CzechPack(CountryPack):
    code: str = "cz"

    @property
    @override
    def name(self) -> str:
        return "Czech Republic"

    @property
    @override
    def metadata(self) -> CountryMetadata:
        return CZECH_METADATA

    @property
    @override
    def detectors(self) -> list[Detector]:
        return [
            RodneCisloDetector(),
            ICODetector(),
            DICDetector(),
            BankAccountDetector(),
            PostalCodeDetector(),
            PhoneNumberDetector(),
            EmailDetector(),
            NameDetector(),
            AddressDetector(),
            DateOfBirthDetector(),
            VehiclePlateDetector(),
            HealthInsuranceDetector(),
            IBANDetector(),
            CreditCardDetector(),
            IdentityCardDetector(),
        ]

    @property
    @override
    def entities(self) -> list[EntityDefinition]:
        return CZECH_ENTITIES
