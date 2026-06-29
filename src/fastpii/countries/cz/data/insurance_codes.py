from datetime import datetime

from fastpii.core._compat import override
from fastpii.data.base import CountryData, DataSource


class CzechInsuranceCodesData(CountryData[dict[str, str]]):
    """Czech health insurance codes data module.

    Provides access to Czech health insurance company codes.
    Only 7 insurance companies exist in Czech Republic.
    """

    _source_url: str = "https://www.mfcr.cz/"
    _source_license: str = "Public domain"

    def __init__(self) -> None:
        self._data: dict[str, str] | None = None

    @override
    def get_data(self) -> dict[str, str]:
        if self._data is None:
            from fastpii.countries.cz.data._data.insurance_codes import INSURANCE_NAMES
            self._data = dict(INSURANCE_NAMES)
        return self._data

    @override
    def get_source(self) -> DataSource:
        return DataSource(
            name="CZ Insurance Codes",
            url=self._source_url,
            license=self._source_license,
            last_updated=datetime.now(),
            entry_count=len(self.get_data()),
        )

    @override
    def validate(self) -> bool:
        return len(self.get_data()) > 0
