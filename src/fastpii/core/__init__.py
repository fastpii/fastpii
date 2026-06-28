"""
FastPII Core utilities.

Shared infrastructure used across all country packs:
- Context matching
- Confidence scoring
- Checksum algorithms
- Normalization utilities
- Regex helpers
- Transformation engine and strategies
"""

from fastpii.core._compat import override
from fastpii.core.context import ContextWindowMatcher
from fastpii.core.confidence import ConfidenceScorer
from fastpii.core.checksum import weighted_mod11, luhn_checksum, validate_luhn
from fastpii.core.normalization import normalize_whitespace, normalize_phone

__all__ = [
    "override",
    "ContextWindowMatcher",
    "ConfidenceScorer",
    "weighted_mod11",
    "luhn_checksum",
    "validate_luhn",
    "normalize_whitespace",
    "normalize_phone",
]