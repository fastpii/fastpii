from datetime import datetime

from fastpii.core._compat import override
from fastpii.data.base import CountryData, DataSource


class FrenchSurnamesData(CountryData[dict[str, set[str]]]):
    _source_url: str = "https://www.data.gouv.fr/"
    _source_license: str = "Licence Ouverte 2.0"

    def __init__(self) -> None:
        self._data: dict[str, set[str]] | None = None

    @override
    def get_data(self) -> dict[str, set[str]]:
        if self._data is None:
            self._data = {"male": set(), "female": set()}
        return self._data

    @override
    def get_source(self) -> DataSource:
        data = self.get_data()
        total = len(data["male"]) + len(data["female"])
        return DataSource(
            name="FR Surnames",
            url=self._source_url,
            license=self._source_license,
            last_updated=datetime.now(),
            entry_count=total,
        )

    @override
    def validate(self) -> bool:
        data = self.get_data()
        return "male" in data and "female" in data
