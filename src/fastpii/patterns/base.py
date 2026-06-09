"""
Abstract base class for Pattern Registries.

Defines the interface that all region-specific pattern registries must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import re


@dataclass
class PatternDefinition:
    """
    Definition of a single PII detection pattern.
    
    Patterns are pre-compiled for performance and include metadata for context
    and validation.
    
    Attributes:
        entity_type: Type of PII (e.g., "rodne_cislo", "ico")
        name: Variant name (e.g., "standard", "mobile", "landline")
        regex: The regex pattern string for detection
        region: Region code (e.g., "cz", "sk", "de")
        score: Confidence score for matches (0.0-1.0)
        context_words: Words that boost confidence when found nearby
        checksum_algo: Name of validation algorithm (e.g., "validate_ico")
        compiled: Pre-compiled regex pattern (auto-generated)
        validation_regex: Optional pattern for validating detected values
        extraction_regex: Optional pattern for extracting metadata components
        validation_compiled: Pre-compiled validation pattern (auto-generated)
        extraction_compiled: Pre-compiled extraction pattern (auto-generated)
    """
    entity_type: str
    name: str
    regex: str
    region: str
    score: float = 1.0
    context_words: list[str] = field(default_factory=list)
    checksum_algo: str | None = None
    compiled: re.Pattern[str] = field(init=False, repr=False)
    validation_regex: str | None = None
    extraction_regex: str | None = None
    validation_compiled: re.Pattern[str] | None = field(init=False, repr=False, default=None)
    extraction_compiled: re.Pattern[str] | None = field(init=False, repr=False, default=None)
    
    def __post_init__(self) -> None:
        """Pre-compile the regex patterns"""
        try:
            self.compiled = re.compile(self.regex)
        except re.error as e:
            raise ValueError(f"Invalid regex for {self.entity_type}.{self.name}: {e}")
        
        if self.validation_regex:
            try:
                self.validation_compiled = re.compile(self.validation_regex)
            except re.error as e:
                raise ValueError(f"Invalid validation_regex for {self.entity_type}.{self.name}: {e}")
        
        if self.extraction_regex:
            try:
                self.extraction_compiled = re.compile(self.extraction_regex)
            except re.error as e:
                raise ValueError(f"Invalid extraction_regex for {self.entity_type}.{self.name}: {e}")


class BasePatternRegistry(ABC):
    """
    Abstract base class for pattern registries.
    
    Each region (CZ, SK, DE, PL) should implement their own pattern registry
    by subclassing this interface.
    
    This follows the Strategy pattern - different regions can have different
    pattern loading strategies while conforming to the same interface.
    
    Usage:
        class CzechPatternRegistry(BasePatternRegistry):
            def load_patterns(self) -> None:
                self.register(PatternDefinition(
                    entity_type="rodne_cislo",
                    name="standard",
                    regex=r"\\b(\\d{6}[/\\s]?\\d{3,4})\\b",
                    region="cz",
                    ...
                ))
    """
    
    @abstractmethod
    def load_patterns(self) -> None:
        """
        Load all patterns for this region.
        
        Implementations should:
        1. Create PatternDefinition instances for all PII types
        2. Register them using self.register()
        
        Example:
            def load_patterns(self) -> None:
                self.register(PatternDefinition(
                    entity_type="rodne_cislo",
                    name="standard",
                    regex=r"\\b(\\d{6}[/\\s]?\\d{3,4})\\b",
                    region="cz",
                    score=0.95
                ))
        """
        pass
    
    @abstractmethod
    def register(self, pattern: PatternDefinition) -> None:
        """
        Register a pattern definition.
        
        Args:
            pattern: Pattern definition to register
        """
        pass
    
    @abstractmethod
    def get_patterns(self, entity_type: str, region: str) -> list[PatternDefinition]:
        """
        Get all patterns for an entity type in a region.
        
        Args:
            entity_type: Type of PII (e.g., "rodne_cislo")
            region: Region code (e.g., "cz")
            
        Returns:
            List of pattern definitions (empty list if not found)
        """
        pass
    
    @abstractmethod
    def get_pattern(self, entity_type: str, variant: str, region: str) -> PatternDefinition | None:
        """
        Get a specific pattern variant.
        
        Args:
            entity_type: Type of PII (e.g., "phone")
            variant: Variant name (e.g., "mobile")
            region: Region code (e.g., "cz")
            
        Returns:
            Pattern definition or None if not found
        """
        pass
    
    @abstractmethod
    def get_available_regions(self) -> list[str]:
        """Get list of available region codes"""
        pass
    
    @abstractmethod
    def get_available_entities(self, region: str) -> list[str]:
        """
        Get list of available entity types for a region.
        
        Args:
            region: Region code (e.g., "cz")
            
        Returns:
            List of entity type names
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all registered patterns"""
        pass
