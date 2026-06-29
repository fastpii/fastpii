from datetime import datetime

from fastpii.data.base import CountryData, DataSource


class CzechStreetsData(CountryData[set[str]]):
    """Czech streets data module.

    Provides access to Czech street names from ČÚZK RÚIAN (Registrační územní identifikační síť).
    """

    _source_url = "https://vdp.cuzk.gov.cz/vymenny_format/csv/"
    _source_license = "CC-BY 4.0"

    def __init__(self) -> None:
        self._data: set[str] | None = None

    def get_data(self) -> set[str]:
        if self._data is None:
            from fastpii.countries.cz.data._data.streets import STREETS
            self._data = set(STREETS)
        return self._data

    def get_source(self) -> DataSource:
        return DataSource(
            name="CZ Streets",
            url=self._source_url,
            license=self._source_license,
            last_updated=datetime.now(),
            entry_count=len(self.get_data()),
        )

    def validate(self) -> bool:
        return len(self.get_data()) > 0