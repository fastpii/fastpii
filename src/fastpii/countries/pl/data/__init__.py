from fastpii.core._compat import override
from fastpii.countries.pl.data.bank_codes import PolishBankCodesData
from fastpii.countries.pl.data.cities import PolishCitiesData
from fastpii.countries.pl.data.insurance_codes import PolishInsuranceCodesData
from fastpii.countries.pl.data.names import PolishNamesData
from fastpii.countries.pl.data.postal_codes import PolishPostalCodesData
from fastpii.countries.pl.data.streets import PolishStreetsData
from fastpii.countries.pl.data.surnames import PolishSurnamesData
from fastpii.data.base import CountryData, CountryMetadata, CountryModule
from fastpii.data.registry import CountryRegistry

__all__ = [
    "POLISH_METADATA",
    "PolishBankCodesData",
    "PolishCitiesData",
    "PolishInsuranceCodesData",
    "PolishModule",
    "PolishNamesData",
    "PolishPostalCodesData",
    "PolishStreetsData",
    "PolishSurnamesData",
]

POLISH_METADATA = CountryMetadata(
    code="PL",
    name="Poland",
    language_codes=("pl", "pl-PL"),
    currency_code="PLN",
)


class PolishModule(CountryModule):

    @override
    def get_metadata(self) -> CountryMetadata:
        return POLISH_METADATA

    @override
    def get_bank_codes(self) -> CountryData[dict[str, str]]:
        return PolishBankCodesData()

    @override
    def get_cities(self) -> CountryData[set[str]]:
        return PolishCitiesData()

    @override
    def get_postal_codes(self) -> CountryData[set[str]]:
        return PolishPostalCodesData()

    @override
    def get_names(self) -> CountryData[dict[str, set[str]]]:
        return PolishNamesData()

    @override
    def get_insurance_codes(self) -> CountryData[dict[str, str]]:
        return PolishInsuranceCodesData()

    @override
    def get_streets(self) -> CountryData[set[str]]:
        return PolishStreetsData()

    @override
    def get_surnames(self) -> CountryData[dict[str, set[str]]]:
        return PolishSurnamesData()


CountryRegistry.register("pl", PolishModule)