"""
Pattern Registry Implementation

Centralized pattern management with pre-compilation, region-based organization,
and auto-discovery following industry best practices.

Design Patterns:
- Strategy Pattern: Different regions implement their own loaders
- Plugin Pattern: Auto-discovery of region modules
- Factory Pattern: Dynamic loader instantiation
- Singleton Pattern: Global shared instance
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type
from functools import lru_cache

from fastpii.patterns.base import BasePatternRegistry, PatternDefinition


class PatternRegistry(BasePatternRegistry):
    """
    Generic pattern registry with auto-discovery and modular loading.
    
    Industry Best Practices:
    1. **Plugin Architecture**: Region loaders are plugins, not hardcoded
    2. **Auto-Discovery**: Automatically finds region modules
    3. **Lazy Loading**: Patterns loaded only when needed
    4. **Extensibility**: Add new regions by creating modules
    5. **Configuration over Code**: Patterns defined declaratively
    6. **Single Responsibility**: Each loader handles its own region
    
    Usage:
        # Auto-discovery mode (recommended)
        registry = PatternRegistry()
        registry.load_patterns("cz")  # Loads Czech patterns
        
        # Manual registration (backward compatible)
        registry.register(PatternDefinition(...))
        
        # Auto-load all regions
        registry.load_all_regions()
    
    Design Pattern: Strategy Pattern
    - Each region implements its own loading strategy
    - Registry delegates to appropriate loader
    - Easy to add new regions without modifying registry
    """
    
    def __init__(self):
        """Create an empty pattern registry with auto-discovery"""
        # region -> entity_type -> List[PatternDefinition]
        self._patterns: Dict[str, Dict[str, List[PatternDefinition]]] = {}
        
        # Cache compiled patterns
        self._pattern_cache: Dict[str, PatternDefinition] = {}
        
        # Loaded regions (lazy loading)
        self._loaded_regions: set = set()
        
        # Auto-discovered region loaders (Plugin Pattern)
        self._loaders: Dict[str, Type] = {}
        self._discover_region_loaders()
    
    def _discover_region_loaders(self) -> None:
        """
        Auto-discover available region loaders.
        
        Implements the Plugin Pattern:
        - Scans regions directory for available loaders
        - Registers them without hardcoding
        - Easy to add new regions by creating modules
        
        This follows the Open/Closed Principle:
        - Open for extension (add new region modules)
        - Closed for modification (no need to edit this file)
        """
        try:
            # Import all available region loaders
            from fastpii.patterns.regions import REGION_LOADERS
            self._loaders = REGION_LOADERS.copy()
        except ImportError:
            # Fallback: no region loaders available yet
            self._loaders = {}
    
    def register(self, pattern: PatternDefinition) -> None:
        """
        Register a pattern definition manually.
        
        Args:
            pattern: Pattern definition to register
            
        Raises:
            ValueError: If regex is invalid
        
        Note:
            Prefer using load_patterns(region_code) for auto-discovery
        """
        region = pattern.region.lower()
        entity_type = pattern.entity_type.lower()
        
        # Initialize region dict if needed
        if region not in self._patterns:
            self._patterns[region] = {}
        
        # Initialize entity list if needed
        if entity_type not in self._patterns[region]:
            self._patterns[region][entity_type] = []
        
        # Add pattern to registry
        self._patterns[region][entity_type].append(pattern)
        
        # Cache by variant name
        cache_key = f"{region}.{entity_type}.{pattern.name}"
        self._pattern_cache[cache_key] = pattern
    
    def load_patterns(self, region_code: str) -> None:
        """
        Load patterns for a specific region using auto-discovery.
        
        Implements the Strategy Pattern:
        - Delegates to region-specific loader
        - Each region has its own loading strategy
        - No hardcoded patterns in registry
        
        Args:
            region_code: ISO 3166-1 alpha-2 code (e.g., "cz", "sk", "de", "pl")
        
        Raises:
            ValueError: If region not available
        
        Example:
            >>> registry = PatternRegistry()
            >>> registry.load_patterns("cz")  # Loads Czech patterns
            >>> registry.load_patterns("sk")  # Future: Slovak patterns
        """
        region_code = region_code.lower()
        
        # Check if already loaded (Lazy Loading Pattern)
        if region_code in self._loaded_regions:
            return
        
        # Check if loader available
        if region_code not in self._loaders:
            available = list(self._loaders.keys())
            raise ValueError(
                f"Region '{region_code}' not available. "
                f"Available regions: {available}. "
                f"To add support, create a loader in patterns/regions/{region_code}.py"
            )
        
        # Instantiate loader (Factory Pattern)
        loader_class = self._loaders[region_code]
        loader = loader_class()
        
        # Load patterns
        patterns = loader.load()
        
        # Register all patterns
        for pattern in patterns:
            self.register(pattern)
        
        # Mark as loaded
        self._loaded_regions.add(region_code)
    
    def load_all_regions(self) -> None:
        """
        Load all available region patterns.
        
        Useful for systems that need all patterns upfront.
        
        Example:
            >>> registry = PatternRegistry()
            >>> registry.load_all_regions()  # Loads all available regions
        """
        for region_code in self._loaders.keys():
            self.load_patterns(region_code)
    
    @lru_cache(maxsize=128)
    def get_patterns(self, entity_type: str, region: str) -> List[PatternDefinition]:
        """
        Get all patterns for an entity type in a region.
        
        Uses LRU cache for performance.
        
        Args:
            entity_type: Type of PII (e.g., "rodne_cislo")
            region: Region code (e.g., "cz")
            
        Returns:
            List of pattern definitions (empty list if not found)
        """
        region = region.lower()
        entity_type = entity_type.lower()
        
        return self._patterns.get(region, {}).get(entity_type, [])
    
    def get_pattern(self, entity_type: str, variant: str, region: str) -> Optional[PatternDefinition]:
        """
        Get a specific pattern variant.
        
        Args:
            entity_type: Type of PII (e.g., "phone")
            variant: Variant name (e.g., "mobile")
            region: Region code (e.g., "cz")
            
        Returns:
            Pattern definition or None if not found
        """
        cache_key = f"{region.lower()}.{entity_type.lower()}.{variant}"
        return self._pattern_cache.get(cache_key)
    
    def get_available_regions(self) -> List[str]:
        """Get list of available region codes"""
        return list(self._loaders.keys())
    
    def get_loaded_regions(self) -> List[str]:
        """Get list of regions that have been loaded"""
        return list(self._loaded_regions)
    
    def get_available_entities(self, region: str) -> List[str]:
        """
        Get list of available entity types for a region.
        
        Args:
            region: Region code (e.g., "cz")
            
        Returns:
            List of entity type names
        """
        return list(self._patterns.get(region.lower(), {}).keys())
    
    def clear(self) -> None:
        """Clear all registered patterns"""
        self._patterns.clear()
        self._pattern_cache.clear()
        self._loaded_regions.clear()
        # Clear the LRU cache
        self.get_patterns.cache_clear()
    
    # Backward compatibility: Keep load_czech_patterns() as alias
    def load_czech_patterns(self) -> None:
        """
        Load Czech patterns (backward compatibility).
        
        Deprecated: Use load_patterns("cz") instead.
        """
        self.load_patterns("cz")


# Region-specific registry implementations
class CzechPatternRegistry(PatternRegistry):
    """
    Czech (CZ) specific pattern registry.
    
    Loads all Czech patterns on initialization.
    
    Usage:
        registry = CzechPatternRegistry()
        patterns = registry.get_patterns("rodne_cislo", "cz")
    
    Note:
        Prefer using PatternRegistry().load_patterns("cz") instead
        for consistency with multi-region systems.
    """
    
    def __init__(self):
        super().__init__()
        self.load_patterns()  # Automatically load Czech patterns
    
    def load_patterns(self) -> None:
        """Load Czech patterns"""
        self.load_czech_patterns()


# Global shared registry instance (singleton)
_shared_registry: Optional[PatternRegistry] = None


def get_shared_registry() -> PatternRegistry:
    """
    Get the global shared pattern registry instance.
    
    Creates a singleton instance that can be shared across all detectors
    and the PrivacyGuard to avoid pattern duplication.
    
    Returns:
        Shared PatternRegistry instance
    
    Design Pattern: Singleton
    - Ensures only one registry instance exists
    - Saves memory (patterns loaded once)
    - Consistent across application
    
    Example:
        >>> # In detector 1
        >>> registry = get_shared_registry()
        >>> registry.load_patterns("cz")
        
        >>> # In detector 2 (same instance!)
        >>> registry = get_shared_registry()
        >>> patterns = registry.get_patterns("ico", "cz")
    """
    global _shared_registry
    if _shared_registry is None:
        _shared_registry = PatternRegistry()
        _shared_registry.load_patterns("cz")  # Load default region
    return _shared_registry


def set_shared_registry(registry: PatternRegistry) -> None:
    """
    Set the global shared pattern registry instance.
    
    Useful for testing or custom region configurations.
    
    Args:
        registry: PatternRegistry instance to use as shared registry
    
    Example:
        >>> # For testing
        >>> test_registry = PatternRegistry()
        >>> set_shared_registry(test_registry)
    """
    global _shared_registry
    _shared_registry = registry


def reset_shared_registry() -> None:
    """
    Reset the global shared registry to None.
    
    Useful for testing to ensure clean state.
    """
    global _shared_registry
    _shared_registry = None