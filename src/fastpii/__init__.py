__version__ = "0.4.0"

from fastpii.models import Finding, DetectionResult, ValidationResult
from fastpii.guard import (
    FastPII,
    PrivacyGuard,
    DEFAULT_PRIORITY,
    DEFAULT_CONFIDENCE_SCORES,
    DEFAULT_CONTEXT_BOOST,
)
from fastpii.core.confidence import ConfidenceScorer

__all__ = [
    "FastPII",
    "PrivacyGuard",
    "ConfidenceScorer",
    "Finding",
    "DetectionResult",
    "ValidationResult",
    "DEFAULT_PRIORITY",
    "DEFAULT_CONFIDENCE_SCORES",
    "DEFAULT_CONTEXT_BOOST",
]
