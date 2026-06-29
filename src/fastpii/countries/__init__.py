from abc import ABC, abstractmethod

from fastpii.countries.base import CountryMetadata, EntityDefinition
from fastpii.detectors.base import Detector
from fastpii.detectors.registry import DetectorRegistry
from fastpii.patterns.registry import PatternRegistry


__all__ = [
    "CountryPack",
    "register_country",
    "get_country_packs",
    "get_country_pack",
]


class CountryPack(ABC):
    """Abstract base class for country packs.

    Every country (CZ, PL, DE, FR, etc.) implements this interface
    to provide detectors, patterns, validators, entities, and metadata.

    Subclasses MUST set ``code`` as a class attribute (not a property):

        class GermanPack(CountryPack):
            code = "de"
    """

    code: str

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def metadata(self) -> CountryMetadata:
        ...

    @property
    @abstractmethod
    def detectors(self) -> list[Detector]:
        ...

    @property
    @abstractmethod
    def entities(self) -> list[EntityDefinition]:
        ...

    def register_detectors(self, registry: DetectorRegistry) -> None:
        for detector in self.detectors:
            registry.register(detector)

    def register_patterns(self, registry: PatternRegistry) -> None:
        registry.load_patterns(self.code)


_COUNTRY_PACKS: dict[str, type[CountryPack]] = {}

_PACK_MODULES: dict[str, str] = {
    "cz": "fastpii.countries.cz",
    "pl": "fastpii.countries.pl",
    "de": "fastpii.countries.de",
    "fr": "fastpii.countries.fr",
}


def _ensure_loaded(code: str) -> None:
    if code not in _COUNTRY_PACKS and code in _PACK_MODULES:
        import importlib
        _ = importlib.import_module(_PACK_MODULES[code])


def register_country(pack_cls: type[CountryPack]) -> type[CountryPack]:
    _COUNTRY_PACKS[pack_cls.code] = pack_cls
    return pack_cls


def get_country_packs() -> dict[str, type[CountryPack]]:
    for code in _PACK_MODULES:
        _ensure_loaded(code)
    return _COUNTRY_PACKS.copy()


def get_country_pack(code: str) -> type[CountryPack] | None:
    _ensure_loaded(code)
    return _COUNTRY_PACKS.get(code)
