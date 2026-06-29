from datetime import datetime

from fastpii.data.base import CountryData, DataSource


class CzechCitiesData(CountryData[set[str]]):
    """Czech cities data module.

    Provides access to Czech city names from OpenStreetMap.
    """

    _source_url = "https://download.geofabrik.de/europe/czech-republic.html"
    _source_license = "ODbL"

    def __init__(self) -> None:
        self._data: set[str] | None = None

    def get_data(self) -> set[str]:
        if self._data is None:
            from fastpii.data.countries.cz._cities import CITIES
            self._data = set(CITIES)
        return self._data

    def get_source(self) -> DataSource:
        return DataSource(
            name="CZ Cities",
            url=self._source_url,
            license=self._source_license,
            last_updated=datetime.now(),
            entry_count=len(self.get_data()),
        )

    def validate(self) -> bool:
        return len(self.get_data()) > 0