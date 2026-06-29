import importlib
from typing import cast

from fastpii.patterns.regions import PatternLoader
from fastpii.countries.pl.pack import PolishPack, POLISH_METADATA, POLISH_ENTITIES
from fastpii.countries.pl.validators import (
    extract_pesel_metadata,
    is_valid_nip,
    is_valid_pesel,
    is_valid_regon,
    validate_nip,
    validate_pesel,
    validate_regon,
)

__all__ = [
    "PolishPack",
    "POLISH_METADATA",
    "POLISH_ENTITIES",
    "PolishPatternLoader",
    "extract_pesel_metadata",
    "is_valid_nip",
    "is_valid_pesel",
    "is_valid_regon",
    "validate_nip",
    "validate_pesel",
    "validate_regon",
]

PolishPatternLoader: type[PatternLoader] = cast(type[PatternLoader], getattr(
    importlib.import_module("fastpii.countries.pl.patterns"),
    "PolishPatternLoader",
))
