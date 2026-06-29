from datetime import datetime

from fastpii.data.base import CountryData, DataSource


class CzechPostalCodesData(CountryData[set[str]]):
    """Czech postal codes (PSČ) data module.

    Provides access to Czech postal codes from ČÚZK RÚIAN (Registrační územní identifikační síť).
    Validates that all codes are 5-digit strings.
    """

    _source_url = "https://vdp.cuzk.gov.cz/vymenny_format/csv/"
    _source_license = "CC-BY 4.0"

    def __init__(self) -> None:
        self._data: set[str] | None = None

    def get_data(self) -> set[str]:
        if self._data is None:
            from fastpii.countries.cz.data._data.postal_codes import POSTAL_CODES
            self._data = set(POSTAL_CODES)
        return self._data

    def get_source(self) -> DataSource:
        return DataSource(
            name="CZ Postal Codes",
            url=self._source_url,
            license=self._source_license,
            last_updated=datetime.now(),
            entry_count=len(self.get_data()),
        )

    def validate(self) -> bool:
        data = self.get_data()
        return len(data) > 0 and all(len(code) == 5 and code.isdigit() for code in data)
