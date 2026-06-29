import importlib
from typing import cast

from fastpii.patterns.regions import PatternLoader
from fastpii.countries.fr.pack import FrenchPack, FRENCH_METADATA, FRENCH_ENTITIES
from fastpii.countries.fr.validators import (
    extract_insee_metadata,
    is_valid_insee,
    is_valid_siren,
    is_valid_siret,
    validate_insee,
    validate_siren,
    validate_siret,
)

__all__ = [
    "FrenchPack",
    "FRENCH_METADATA",
    "FRENCH_ENTITIES",
    "FrenchPatternLoader",
    "extract_insee_metadata",
    "is_valid_insee",
    "is_valid_siren",
    "is_valid_siret",
    "validate_insee",
    "validate_siren",
    "validate_siret",
]

FrenchPatternLoader: type[PatternLoader] = cast(type[PatternLoader], getattr(
    importlib.import_module("fastpii.countries.fr.patterns"),
    "FrenchPatternLoader",
))
