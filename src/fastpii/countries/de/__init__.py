import importlib
from typing import cast

from fastpii.patterns.regions import PatternLoader
from fastpii.countries.de.pack import GermanPack, GERMAN_METADATA, GERMAN_ENTITIES
from fastpii.countries.de.validators import (
    extract_steuer_id_metadata,
    is_valid_handelsregister,
    is_valid_steuer_id,
    is_valid_ust_id,
    parse_handelsregister,
    validate_handelsregister,
    validate_steuer_id,
    validate_ust_id,
)

__all__ = [
    "GermanPack",
    "GERMAN_METADATA",
    "GERMAN_ENTITIES",
    "GermanPatternLoader",
    "extract_steuer_id_metadata",
    "is_valid_handelsregister",
    "is_valid_steuer_id",
    "is_valid_ust_id",
    "parse_handelsregister",
    "validate_handelsregister",
    "validate_steuer_id",
    "validate_ust_id",
]

GermanPatternLoader: type[PatternLoader] = cast(type[PatternLoader], getattr(
    importlib.import_module("fastpii.countries.de.patterns"),
    "GermanPatternLoader",
))
