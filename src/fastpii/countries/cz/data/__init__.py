from fastpii.core._compat import override
from fastpii.data.base import CountryData, CountryMetadata, CountryModule
from fastpii.countries.cz.data.bank_codes import CzechBankCodesData
from fastpii.countries.cz.data.cities import CzechCitiesData
from fastpii.countries.cz.data.corporate_names import CzechCorporateNamesData
from fastpii.countries.cz.data.insurance_codes import CzechInsuranceCodesData
from fastpii.countries.cz.data.names import CzechNamesData
from fastpii.countries.cz.data.postal_codes import CzechPostalCodesData
from fastpii.countries.cz.data.streets import CzechStreetsData
from fastpii.countries.cz.data.surnames import CzechSurnamesData
from fastpii.data.registry import CountryRegistry

__all__ = [
    "CzechBankCodesData",
    "CzechCitiesData",
    "CzechCorporateNamesData",
    "CzechInsuranceCodesData",
    "CzechModule",
    "CZECH_METADATA",
    "CzechNamesData",
    "CzechPostalCodesData",
    "CzechStreetsData",
    "CzechSurnamesData",
]

CZECH_METADATA = CountryMetadata(
    code="CZ",
    name="Czech Republic",
    language_codes=("cs",),
    currency_code="CZK",
)


class CzechModule(CountryModule):

    @override
    def get_metadata(self) -> CountryMetadata:
        return CZECH_METADATA

    @override
    def get_bank_codes(self) -> CountryData[dict[str, str]]:
        return CzechBankCodesData()

    @override
    def get_cities(self) -> CountryData[set[str]]:
        return CzechCitiesData()

    @override
    def get_postal_codes(self) -> CountryData[set[str]]:
        return CzechPostalCodesData()

    @override
    def get_names(self) -> CountryData[dict[str, set[str]]]:
        return CzechNamesData()

    def get_corporate_names(self) -> CountryData[set[str]]:
        return CzechCorporateNamesData()

    @override
    def get_insurance_codes(self) -> CountryData[dict[str, str]]:
        return CzechInsuranceCodesData()

    @override
    def get_streets(self) -> CountryData[set[str]]:
        return CzechStreetsData()

    @override
    def get_surnames(self) -> CountryData[dict[str, set[str]]]:
        return CzechSurnamesData()


CountryRegistry.register("cz", CzechModule)
