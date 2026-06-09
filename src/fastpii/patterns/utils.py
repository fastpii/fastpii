"""
Pattern utilities for validators.

Provides registry access for validation and extraction patterns.
Uses singleton pattern for efficiency.
"""

from fastpii.patterns.base import PatternDefinition
from fastpii.patterns.registry import get_shared_registry


def validate_format(entity_type: str, value: str, region: str = "cz") -> bool:
    """
    Validate value format using registry patterns.
    
    Args:
        entity_type: Type of PII (e.g., "rodne_cislo")
        value: Value to validate
        region: Region code (default: "cz")
    
    Returns:
        True if format matches, False otherwise
    """
    registry = get_shared_registry()
    patterns = registry.get_patterns(entity_type, region)
    
    if not patterns:
        return False
    
    pattern_def = patterns[0]
    
    if not pattern_def.validation_compiled:
        # Fallback to detection pattern if no validation pattern
        return bool(pattern_def.compiled.search(value))
    
    return bool(pattern_def.validation_compiled.match(value))


def extract_groups(entity_type: str, value: str, region: str = "cz") -> tuple[str, ...] | None:
    """
    Extract regex groups using registry patterns.
    
    Args:
        entity_type: Type of PII (e.g., "rodne_cislo")
        value: Value to extract from
        region: Region code (default: "cz")
    
    Returns:
        Tuple of groups or None if no match
    """
    registry = get_shared_registry()
    patterns = registry.get_patterns(entity_type, region)
    
    if not patterns:
        return None
    
    pattern_def = patterns[0]
    
    # Use extraction pattern if available, otherwise use validation pattern
    pattern = pattern_def.extraction_compiled or pattern_def.validation_compiled or pattern_def.compiled
    
    if not pattern:
        return None
    
    match = pattern.match(value)
    if match:
        return match.groups()
    
    return None


def get_pattern(
    entity_type: str,
    variant: str = "standard",
    region: str = "cz",
) -> PatternDefinition | None:
    """
    Get a specific pattern from the registry.
    
    Args:
        entity_type: Type of PII (e.g., "phone")
        variant: Variant name (e.g., "mobile")
        region: Region code (default: "cz")
    
    Returns:
        PatternDefinition or None
    """
    registry = get_shared_registry()
    return registry.get_pattern(entity_type, variant, region)
