"""FastPII Data Infrastructure.

Provides modular, extensible data infrastructure for PII detection.

Example:
    from fastpii.data.registry import CountryRegistry

    cz_module = CountryRegistry.get('cz')
    cities = cz_module.get_cities().get_data()
"""

from fastpii.data.base import CountryData, CountryMetadata, CountryModule, DataSource
from fastpii.data.registry import CountryRegistry

__all__ = [
    "DataSource",
    "CountryMetadata",
    "CountryData",
    "CountryModule",
    "CountryRegistry",
]