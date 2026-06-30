from fastpii.core._compat import override
from fastpii.countries.fr.data.bank_codes import FrenchBankCodesData
from fastpii.countries.fr.data.cities import FrenchCitiesData
from fastpii.countries.fr.data.insurance_codes import FrenchInsuranceCodesData
from fastpii.countries.fr.data.names import FrenchNamesData
from fastpii.countries.fr.data.postal_codes import FrenchPostalCodesData
from fastpii.countries.fr.data.streets import FrenchStreetsData
from fastpii.countries.fr.data.surnames import FrenchSurnamesData
from fastpii.data.base import CountryData, CountryMetadata, CountryModule
from fastpii.data.registry import CountryRegistry

__all__ = [
    "FrenchBankCodesData",
    "FrenchCitiesData",
    "FrenchInsuranceCodesData",
    "FrenchModule",
    "FRENCH_METADATA",
    "FrenchNamesData",
    "FrenchPostalCodesData",
    "FrenchStreetsData",
    "FrenchSurnamesData",
]

FRENCH_METADATA = CountryMetadata(
    code="FR",
    name="France",
    language_codes=("fr", "fr-FR"),
    currency_code="EUR",
)


class FrenchModule(CountryModule):

    @override
    def get_metadata(self) -> CountryMetadata:
        return FRENCH_METADATA

    @override
    def get_bank_codes(self) -> CountryData[dict[str, str]]:
        return FrenchBankCodesData()

    @override
    def get_cities(self) -> CountryData[set[str]]:
        return FrenchCitiesData()

    @override
    def get_postal_codes(self) -> CountryData[set[str]]:
        return FrenchPostalCodesData()

    @override
    def get_names(self) -> CountryData[dict[str, set[str]]]:
        return FrenchNamesData()

    @override
    def get_insurance_codes(self) -> CountryData[dict[str, str]]:
        return FrenchInsuranceCodesData()

    @override
    def get_streets(self) -> CountryData[set[str]]:
        return FrenchStreetsData()

    @override
    def get_surnames(self) -> CountryData[dict[str, set[str]]]:
        return FrenchSurnamesData()


CountryRegistry.register("fr", FrenchModule)
