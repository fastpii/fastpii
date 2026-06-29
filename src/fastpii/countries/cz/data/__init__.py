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

CZECH_METADATA = CountryMetadata(
    code="CZ",
    name="Czech Republic",
    language_codes=("cs",),
    currency_code="CZK",
)


class CzechModule(CountryModule):

    def get_metadata(self) -> CountryMetadata:
        return CZECH_METADATA

    def get_bank_codes(self) -> CountryData[dict[str, str]]:
        return CzechBankCodesData()

    def get_cities(self) -> CountryData[set[str]]:
        return CzechCitiesData()

    def get_postal_codes(self) -> CountryData[set[str]]:
        return CzechPostalCodesData()

    def get_names(self) -> CountryData[dict[str, set[str]]]:
        return CzechNamesData()

    def get_corporate_names(self) -> CountryData[set[str]]:
        return CzechCorporateNamesData()

    def get_insurance_codes(self) -> CountryData[dict[str, str]]:
        return CzechInsuranceCodesData()

    def get_streets(self) -> CountryData[set[str]]:
        return CzechStreetsData()

    def get_surnames(self) -> CountryData[dict[str, set[str]]]:
        return CzechSurnamesData()


CountryRegistry.register("cz", CzechModule)
