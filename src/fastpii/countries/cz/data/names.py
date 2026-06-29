from datetime import datetime

from fastpii.core._compat import override
from fastpii.data.base import CountryData, DataSource


class CzechNamesData(CountryData[dict[str, set[str]]]):
    """Czech names data module.

    Provides access to Czech male and female first names from the
    Ministry of Interior registry of approved names.
    """

    _source_url: str = "https://mv.gov.cz/clanek/seznam-rodove-neutralnich-jmen.aspx"
    _source_license: str = "Public domain"

    def __init__(self) -> None:
        self._data: dict[str, set[str]] | None = None

    @override
    def get_data(self) -> dict[str, set[str]]:
        if self._data is None:
            from fastpii.countries.cz.data._data.names_male import MALE_NAMES
            from fastpii.countries.cz.data._data.names_female import FEMALE_NAMES
            self._data = {"male": set(MALE_NAMES), "female": set(FEMALE_NAMES)}
        return self._data

    @override
    def get_source(self) -> DataSource:
        data = self.get_data()
        total = len(data["male"]) + len(data["female"])
        return DataSource(
            name="CZ Names",
            url=self._source_url,
            license=self._source_license,
            last_updated=datetime.now(),
            entry_count=total,
        )

    @override
    def validate(self) -> bool:
        data = self.get_data()
        return "male" in data and "female" in data and len(data["male"]) > 0 and len(data["female"]) > 0
