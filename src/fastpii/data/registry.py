"""Central registry for country modules.

Allows dynamic registration and retrieval of country modules.

Example:
    from fastpii.data.registry import CountryRegistry

    registry.register('cz', CzechModule)
    cz_module = registry.get('cz')
    all_countries = registry.get_all()
"""

from typing import ClassVar

from fastpii.data.base import CountryMetadata, CountryModule


class CountryRegistry:
    """Central registry for country modules.

    Uses class-level storage so country modules are available globally
    after registration. Thread-safe for read operations (registration
    should happen at module import time, not at runtime).
    """

    _countries: ClassVar[dict[str, type[CountryModule]]] = {}

    @classmethod
    def register(cls, code: str, module_class: type[CountryModule]) -> None:
        """Register a country module.

        Args:
            code: ISO 3166-1 alpha-2 code (e.g., 'cz', 'sk', 'pl').
            module_class: CountryModule subclass.
        """
        cls._countries[code.lower()] = module_class

    @classmethod
    def get(cls, code: str) -> CountryModule:
        """Get a country module by code.

        Args:
            code: ISO 3166-1 alpha-2 code

        Returns:
            CountryModule instance

        Raises:
            KeyError: If country not registered
        """
        code = code.lower()
        if code not in cls._countries:
            raise KeyError(
                f"Country '{code}' not registered. Available: {list(cls._countries.keys())}"
            )
        return cls._countries[code]()

    @classmethod
    def get_all(cls) -> dict[str, CountryModule]:
        """Get all registered country modules.

        Returns:
            Dict mapping country code to CountryModule instance
        """
        return {code: module() for code, module in cls._countries.items()}

    @classmethod
    def list_countries(cls) -> list[str]:
        """List all registered country codes."""
        return list(cls._countries.keys())

    @classmethod
    def get_metadata(cls, code: str) -> CountryMetadata:
        """Get metadata for a country."""
        return cls.get(code).get_metadata()

    @classmethod
    def clear(cls) -> None:
        """Clear all registered countries (for testing)."""
        cls._countries.clear()