"""FastPII Data Extractors.

Generic data extractors for all countries.
Each extractor is an abstract base class that country-specific
implementations subclass with their extraction logic.
"""

from fastpii.data.extractors.bank_codes import BankCodesExtractor
from fastpii.data.extractors.cities import CitiesExtractor
from fastpii.data.extractors.names import NamesExtractor
from fastpii.data.extractors.postal_codes import PostalCodesExtractor

__all__ = [
    "BankCodesExtractor",
    "CitiesExtractor",
    "PostalCodesExtractor",
    "NamesExtractor",
]