from datetime import datetime

from fastpii.data.base import CountryData, DataSource


class CzechSurnamesData(CountryData[dict[str, set[str]]]):
    """Czech surnames data module.

    Provides access to Czech male and female surnames from the
    Czech Statistical Office via prijmeni.eu.
    """

    _source_url = "https://prijmeni.eu/ceska-republika"
    _source_license = "CC-BY 4.0"

    def __init__(self) -> None:
        self._data: dict[str, set[str]] | None = None

    def get_data(self) -> dict[str, set[str]]:
        if self._data is None:
            from fastpii.countries.cz.data._data.surnames_male import MALE_SURNAMES
            from fastpii.countries.cz.data._data.surnames_female import FEMALE_SURNAMES
            self._data = {"male": set(MALE_SURNAMES), "female": set(FEMALE_SURNAMES)}
        return self._data

    def get_source(self) -> DataSource:
        data = self.get_data()
        total = len(data["male"]) + len(data["female"])
        return DataSource(
            name="CZ Surnames",
            url=self._source_url,
            license=self._source_license,
            last_updated=datetime.now(),
            entry_count=total,
        )

    def validate(self) -> bool:
        data = self.get_data()
        return "male" in data and "female" in data and len(data["male"]) > 0 and len(data["female"]) > 0