from dataclasses import dataclass, field
from enum import Enum

from fastpii.detectors.base import Detector


class EntityType(str, Enum):
    NATIONAL_ID = "national_id"
    TAX_ID = "tax_id"
    COMPANY_ID = "company_id"
    VAT_ID = "vat_id"
    BANK_ACCOUNT = "bank_account"
    POSTAL_CODE = "postal_code"
    PHONE = "phone"
    EMAIL = "email"
    ADDRESS = "address"
    NAME = "name"
    DATE_OF_BIRTH = "date_of_birth"
    VEHICLE_PLATE = "vehicle_plate"


@dataclass(frozen=True)
class EntityDefinition:
    entity_type: str
    display_name: str
    description: str
    region: str
    has_checksum: bool = False
    context_words: tuple[str, ...] = ()
    examples: tuple[str, ...] = ()
    invalid_examples: tuple[str, ...] = ()


@dataclass
class CountryMetadata:
    code: str
    name: str
    official_name: str
    language_codes: tuple[str, ...] = ()
    iso_3166_alpha2: str = ""
    iso_3166_alpha3: str = ""
    currency_code: str = ""