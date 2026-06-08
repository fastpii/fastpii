"""
Region-specific pattern registries.

Each region (CZ, SK, DE, PL) implements its own module with patterns.
Modules are auto-discovered and loaded on demand.
"""

from fastpii.patterns.regions.czech import CzechPatternLoader

__all__ = ["CzechPatternLoader"]

# Region module mapping for auto-discovery
REGION_LOADERS = {
    "cz": CzechPatternLoader,
    # Future regions:
    # "sk": SlovakPatternLoader,
    # "de": GermanPatternLoader,
    # "pl": PolishPatternLoader,
}