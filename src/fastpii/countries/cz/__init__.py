import importlib
from typing import cast

from fastpii.patterns.regions import PatternLoader
from fastpii.countries.cz.data import CzechModule, CZECH_METADATA
from fastpii.countries.cz.pack import CzechPack, CZECH_METADATA as CZECH_PACK_METADATA, CZECH_ENTITIES
from fastpii.countries.cz.validators import (
    is_valid_birth_number,
    is_valid_bank_code,
    is_valid_insurance_code,
    calculate_ico_checksum,
    format_dic,
    is_valid_ico,
    is_valid_bank_account,
    is_valid_dic,
    parse_bank_account,
    validate_bank_account,
    validate_bank_code,
    validate_birth_number_format,
    validate_dic,
    validate_ico,
    validate_insurance_code,
)

__all__ = [
    "CzechPack",
    "CZECH_METADATA",
    "CZECH_PACK_METADATA",
    "CZECH_ENTITIES",
    "CzechPatternLoader",
    "CzechModule",
    "is_valid_ico",
    "validate_ico",
    "calculate_ico_checksum",
    "is_valid_birth_number",
    "validate_birth_number_format",
    "is_valid_bank_code",
    "is_valid_bank_account",
    "validate_bank_account",
    "validate_bank_code",
    "parse_bank_account",
    "is_valid_dic",
    "validate_dic",
    "format_dic",
    "is_valid_insurance_code",
    "validate_insurance_code",
]

CzechPatternLoader: type[PatternLoader] = cast(type[PatternLoader], getattr(
    importlib.import_module("fastpii.countries.cz.patterns"),
    "CzechPatternLoader",
))
