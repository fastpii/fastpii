from fastpii.core._compat import override
from fastpii.countries.de.data.bank_codes import GermanBankCodesData
from fastpii.countries.de.data.cities import GermanCitiesData
from fastpii.countries.de.data.insurance_codes import GermanInsuranceCodesData
from fastpii.countries.de.data.names import GermanNamesData
from fastpii.countries.de.data.postal_codes import GermanPostalCodesData
from fastpii.countries.de.data.streets import GermanStreetsData
from fastpii.countries.de.data.surnames import GermanSurnamesData
from fastpii.data.base import CountryData, CountryMetadata, CountryModule
from fastpii.data.registry import CountryRegistry

__all__ = [
    "GermanBankCodesData",
    "GermanCitiesData",
    "GermanInsuranceCodesData",
    "GERMAN_METADATA",
    "GermanModule",
    "GermanNamesData",
    "GermanPostalCodesData",
    "GermanStreetsData",
    "GermanSurnamesData",
]

GERMAN_METADATA = CountryMetadata(
    code="DE",
    name="Germany",
    language_codes=("de", "de-DE"),
    currency_code="EUR",
)


class GermanModule(CountryModule):

    @override
    def get_metadata(self) -> CountryMetadata:
        return GERMAN_METADATA

    @override
    def get_bank_codes(self) -> CountryData[dict[str, str]]:
        return GermanBankCodesData()

    @override
    def get_cities(self) -> CountryData[set[str]]:
        return GermanCitiesData()

    @override
    def get_postal_codes(self) -> CountryData[set[str]]:
        return GermanPostalCodesData()

    @override
    def get_names(self) -> CountryData[dict[str, set[str]]]:
        return GermanNamesData()

    @override
    def get_insurance_codes(self) -> CountryData[dict[str, str]]:
        return GermanInsuranceCodesData()

    @override
    def get_streets(self) -> CountryData[set[str]]:
        return GermanStreetsData()

    @override
    def get_surnames(self) -> CountryData[dict[str, set[str]]]:
        return GermanSurnamesData()


CountryRegistry.register("de", GermanModule)