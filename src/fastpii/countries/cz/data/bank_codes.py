from datetime import datetime

from fastpii.core._compat import override
from fastpii.data.base import CountryData, DataSource


class CzechBankCodesData(CountryData[dict[str, str]]):
    """Czech bank codes data module.

    Provides access to Czech bank codes and names from the
    Czech National Bank registry.
    """

    _source_url: str = "https://www.czso.cz/csu/cz/bankovni-kody"
    _source_license: str = "Public domain"

    def __init__(self) -> None:
        self._data: dict[str, str] | None = None

    @override
    def get_data(self) -> dict[str, str]:
        if self._data is None:
            from fastpii.countries.cz.data._data.bank_codes import BANK_NAMES
            self._data = dict(BANK_NAMES)
        return self._data

    @override
    def get_source(self) -> DataSource:
        return DataSource(
            name="CZ Bank Codes",
            url=self._source_url,
            license=self._source_license,
            last_updated=datetime.now(),
            entry_count=len(self.get_data()),
        )

    @override
    def validate(self) -> bool:
        return len(self.get_data()) > 0
