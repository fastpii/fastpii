"""
Pattern package exports.

Primary exports:
- PatternDefinition: Pattern definition dataclass
- BasePatternRegistry: Abstract interface for region-specific registries
- PatternRegistry: Generic registry implementation
- CzechPatternRegistry: Czech-specific registry
- get_shared_registry: Get global shared registry instance
- validate_format: Validate value format using registry patterns
- extract_groups: Extract regex groups using registry patterns
"""

from fastpii.patterns.base import BasePatternRegistry, PatternDefinition
from fastpii.patterns.registry import (
    PatternRegistry,
    CzechPatternRegistry,
    get_shared_registry,
    set_shared_registry,
)
from fastpii.patterns.utils import validate_format, extract_groups, get_pattern

__all__ = [
    "PatternDefinition",
    "BasePatternRegistry",
    "PatternRegistry",
    "CzechPatternRegistry",
    "get_shared_registry",
    "set_shared_registry",
    "validate_format",
    "extract_groups",
    "get_pattern",
]