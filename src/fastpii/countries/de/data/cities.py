from datetime import datetime

from fastpii.core._compat import override
from fastpii.data.base import CountryData, DataSource


class GermanCitiesData(CountryData[set[str]]):
    _source_url: str = "https://www.govdata.de/"
    _source_license: str = "CC-BY 4.0"

    def __init__(self) -> None:
        self._data: set[str] | None = None

    @override
    def get_data(self) -> set[str]:
        if self._data is None:
            from fastpii.countries.de.data._data.cities import CITIES
            self._data = CITIES
        return self._data

    @override
    def get_source(self) -> DataSource:
        return DataSource(
            name="DE Cities",
            url=self._source_url,
            license=self._source_license,
            last_updated=datetime.now(),
            entry_count=len(self.get_data()),
        )

    @override
    def validate(self) -> bool:
        return len(self.get_data()) > 0