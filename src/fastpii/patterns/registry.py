from fastpii.core._compat import override
from fastpii.patterns.base import BasePatternRegistry, PatternDefinition
from fastpii.patterns.regions import PatternLoader


__all__ = [
    "PatternRegistry",
    "CzechPatternRegistry",
    "get_shared_registry",
    "set_shared_registry",
    "reset_shared_registry",
]


class PatternRegistry(BasePatternRegistry):
    def __init__(self) -> None:
        self._patterns: dict[str, dict[str, list[PatternDefinition]]] = {}
        self._pattern_cache: dict[str, PatternDefinition] = {}
        self._loaded_regions: set[str] = set()
        self._loaders: dict[str, type[PatternLoader]] = {}
        self._discover_region_loaders()
    
    def _discover_region_loaders(self) -> None:
        try:
            from fastpii.patterns.regions import get_region_loaders
            self._loaders = get_region_loaders()
        except ImportError:
            self._loaders = {}
    
    @override
    def register(self, pattern: PatternDefinition) -> None:
        region = pattern.region.lower()
        entity_type = pattern.entity_type.lower()
        
        if region not in self._patterns:
            self._patterns[region] = {}
        
        if entity_type not in self._patterns[region]:
            self._patterns[region][entity_type] = []
        
        self._patterns[region][entity_type].append(pattern)
        
        cache_key = f"{region}.{entity_type}.{pattern.name}"
        self._pattern_cache[cache_key] = pattern
    
    @override
    def load_patterns(self, region_code: str | None = None) -> None:
        if region_code is None:
            raise ValueError("region_code is required")

        region_code = region_code.lower()
        
        if region_code in self._loaded_regions:
            return
        
        if region_code not in self._loaders:
            available = list(self._loaders.keys())
            message = (
                f"Region '{region_code}' not available. Available regions: {available}. "
                f"To add support, create a loader in patterns/regions/{region_code}.py"
            )
            raise ValueError(message)
        
        loader_class = self._loaders[region_code]
        loader = loader_class()
        
        patterns = loader.load()
        
        for pattern in patterns:
            self.register(pattern)
        
        self._loaded_regions.add(region_code)
    
    def load_all_regions(self) -> None:
        for region_code in self._loaders.keys():
            self.load_patterns(region_code)
    
    @override
    def get_patterns(self, entity_type: str, region: str) -> list[PatternDefinition]:
        region = region.lower()
        entity_type = entity_type.lower()
        return self._patterns.get(region, {}).get(entity_type, [])
    
    @override
    def get_pattern(self, entity_type: str, variant: str, region: str) -> PatternDefinition | None:
        cache_key = f"{region.lower()}.{entity_type.lower()}.{variant}"
        return self._pattern_cache.get(cache_key)
    
    @override
    def get_available_regions(self) -> list[str]:
        return list(self._loaders.keys())
    
    def get_loaded_regions(self) -> list[str]:
        return list(self._loaded_regions)
    
    @override
    def get_available_entities(self, region: str) -> list[str]:
        return list(self._patterns.get(region.lower(), {}).keys())
    
    @override
    def clear(self) -> None:
        self._patterns.clear()
        self._pattern_cache.clear()
        self._loaded_regions.clear()
    
    def load_czech_patterns(self) -> None:
        self.load_patterns("cz")


class CzechPatternRegistry(PatternRegistry):
    def __init__(self) -> None:
        super().__init__()
        super().load_patterns("cz")
    
    @override
    def load_patterns(self, region_code: str | None = None) -> None:
        super().load_patterns(region_code or "cz")


_shared_registry: PatternRegistry | None = None


def get_shared_registry() -> PatternRegistry:
    global _shared_registry
    if _shared_registry is None:
        _shared_registry = PatternRegistry()
    return _shared_registry


def set_shared_registry(registry: PatternRegistry) -> None:
    global _shared_registry
    _shared_registry = registry


def reset_shared_registry() -> None:
    global _shared_registry
    _shared_registry = None
