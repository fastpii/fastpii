from collections.abc import Callable
from datetime import datetime
from typing import ClassVar, TypeVar

from fastpii.data.base import CountryData, DataSource

F = TypeVar("F", bound=Callable[..., object])

try:
    from typing_extensions import override
except ImportError:
    def override(method: F, /) -> F:
        return method


class CzechCorporateNamesData(CountryData[set[str]]):
    """Czech corporate name parts data module.

    Provides access to common Czech corporate designators and
    company suffixes that cause false positives in name detection.
    """

    _source_url: ClassVar[str] = "https://www.czso.cz/"
    _source_license: ClassVar[str] = "Public domain"

    def __init__(self) -> None:
        self._data: set[str] | None = None

    @override
    def get_data(self) -> set[str]:
        if self._data is None:
            from fastpii.countries.cz.data._data.corporate_names import CORPORATE_NAMES
            self._data = CORPORATE_NAMES
        return self._data

    @override
    def get_source(self) -> DataSource:
        return DataSource(
            name="CZ Corporate Names",
            url=self._source_url,
            license=self._source_license,
            last_updated=datetime.now(),
            entry_count=len(self.get_data()),
        )

    @override
    def validate(self) -> bool:
        return len(self.get_data()) > 0
