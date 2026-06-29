from fastpii.data.base import CountryData, CountryMetadata, CountryModule
from fastpii.data.countries.cz.bank_codes import CzechBankCodesData
from fastpii.data.countries.cz.cities import CzechCitiesData
from fastpii.data.countries.cz.insurance_codes import CzechInsuranceCodesData
from fastpii.data.countries.cz.names import CzechNamesData
from fastpii.data.countries.cz.postal_codes import CzechPostalCodesData
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

    def get_bank_codes(self) -> CountryData:
        return CzechBankCodesData()

    def get_cities(self) -> CountryData:
        return CzechCitiesData()

    def get_postal_codes(self) -> CountryData:
        return CzechPostalCodesData()

    def get_names(self) -> CountryData:
        return CzechNamesData()

    def get_insurance_codes(self) -> CountryData:
        return CzechInsuranceCodesData()


CountryRegistry.register("cz", CzechModule)