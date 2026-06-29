"""Base classes for modular data infrastructure.

Provides abstract base classes for country-specific data modules,
ensuring consistent behavior across all countries.
"""

import time
from abc import ABC, abstractmethod
from collections.abc import Sized
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class DataSource:
    """Data source metadata.

    Attributes:
        name: Human-readable name of the data source.
        url: URL where the data originates.
        license: License under which the data is used.
        last_updated: Timestamp of last data update.
        entry_count: Number of entries in the dataset.
    """

    name: str
    url: str
    license: str
    last_updated: datetime
    entry_count: int


@dataclass(frozen=True)
class CountryMetadata:
    """Country metadata.

    Attributes:
        code: ISO 3166-1 alpha-2 country code (e.g., 'CZ', 'SK', 'PL').
        name: Full country name (e.g., 'Czech Republic').
        language_codes: ISO 639-1 language codes (e.g., ('cs',)).
        currency_code: ISO 4217 currency code (e.g., 'CZK').
    """

    code: str
    name: str
    language_codes: tuple[str, ...] = ()
    currency_code: str = ""


class CountryData(ABC, Generic[T]):
    """Abstract base class for country-specific data.

    All country data modules inherit from this class.
    Provides common interface for data loading, validation,
    import time benchmarking, and data integrity checks.
    """

    @abstractmethod
    def get_data(self) -> T:
        """Return the data for this country.

        Examples:
            BankCodesData: returns Dict[str, str]
            CitiesData: returns Set[str]
            NamesData: returns Dict[str, Set[str]] (male/female)
        """

    @abstractmethod
    def get_source(self) -> DataSource:
        """Return metadata about data source."""

    @abstractmethod
    def validate(self) -> bool:
        """Validate data integrity.

        Checks: data not empty, correct format, no duplicates, no invalid entries.
        """

    def get_import_time(self) -> float:
        """Measure import time in milliseconds."""
        start = time.time()
        _ = self.get_data()
        return (time.time() - start) * 1000

    def get_entry_count(self) -> int:
        """Return number of entries in data.

        Only works when the data type supports len().
        """
        data = self.get_data()
        if isinstance(data, Sized):
            return len(data)
        raise TypeError(f"Cannot count entries for {type(data).__name__}: not a Sized type")


class CountryModule(ABC):
    """Abstract base class for country module containing ALL data for one country.

    Example:
        class CzechModule(CountryModule):
            def get_bank_codes(self) -> CountryData[Dict[str, str]]:
                return CzechBankCodesData()
            def get_cities(self) -> CountryData[Set[str]]:
                return CzechCitiesData()
    """

    @abstractmethod
    def get_metadata(self) -> CountryMetadata:
        """Return country metadata."""

    @abstractmethod
    def get_bank_codes(self) -> "CountryData[dict[str, str]]":
        """Return bank codes data."""

    @abstractmethod
    def get_cities(self) -> "CountryData[set[str]]":
        """Return cities data."""

    @abstractmethod
    def get_postal_codes(self) -> "CountryData[set[str]]":
        """Return postal codes data."""

    @abstractmethod
    def get_names(self) -> "CountryData[dict[str, set[str]]]":
        """Return names data (male/female)."""

    @abstractmethod
    def get_insurance_codes(self) -> "CountryData[dict[str, str]]":
        """Return insurance codes data."""

    @abstractmethod
    def get_streets(self) -> "CountryData[set[str]]":
        """Return streets data."""

    @abstractmethod
    def get_surnames(self) -> "CountryData[dict[str, set[str]]]":
        """Return surnames data (male/female)."""

    def get_all_data(self) -> dict[str, "CountryData"]:
        """Return all data types for this country.

        Caches results so repeated calls return the same instances.
        """
        if not hasattr(self, "_all_data_cache"):
            self._all_data_cache: dict[str, "CountryData"] = {
                "bank_codes": self.get_bank_codes(),
                "cities": self.get_cities(),
                "postal_codes": self.get_postal_codes(),
                "names": self.get_names(),
                "insurance_codes": self.get_insurance_codes(),
                "streets": self.get_streets(),
                "surnames": self.get_surnames(),
            }
        return self._all_data_cache

    def validate_all(self) -> dict[str, bool]:
        """Validate all data types."""
        return {name: data.validate() for name, data in self.get_all_data().items()}

    def benchmark_import_times(self) -> dict[str, float]:
        """Benchmark import times for all data types."""
        return {name: data.get_import_time() for name, data in self.get_all_data().items()}