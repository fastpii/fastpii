"""Tests for fastpii.data.countries.cz module (CzechModule and data classes)."""

import pytest

from fastpii.data.base import CountryData, CountryMetadata, CountryModule
from fastpii.data.countries.cz import CZECH_METADATA, CzechModule
from fastpii.data.countries.cz.bank_codes import CzechBankCodesData
from fastpii.data.countries.cz.cities import CzechCitiesData
from fastpii.data.countries.cz.insurance_codes import CzechInsuranceCodesData
from fastpii.data.countries.cz.names import CzechNamesData
from fastpii.data.countries.cz.postal_codes import CzechPostalCodesData
from fastpii.data.registry import CountryRegistry


class TestCzechMetadata:
    def test_metadata_values(self):
        assert CZECH_METADATA.code == "CZ"
        assert CZECH_METADATA.name == "Czech Republic"
        assert CZECH_METADATA.language_codes == ("cs",)
        assert CZECH_METADATA.currency_code == "CZK"

    def test_metadata_frozen(self):
        with pytest.raises(AttributeError):
            CZECH_METADATA.code = "SK"


class TestCzechInsuranceCodesData:
    def test_get_data(self):
        data = CzechInsuranceCodesData().get_data()
        assert isinstance(data, dict)
        assert "111" in data
        assert len(data) == 7

    def test_get_data_caches(self):
        codes = CzechInsuranceCodesData()
        data1 = codes.get_data()
        data2 = codes.get_data()
        assert data1 is data2

    def test_get_source(self):
        source = CzechInsuranceCodesData().get_source()
        assert source.name == "CZ Insurance Codes"
        assert source.url == "https://www.mfcr.cz/"
        assert source.license == "Public domain"
        assert source.entry_count == 7

    def test_validate(self):
        assert CzechInsuranceCodesData().validate() is True


class TestCzechBankCodesData:
    def test_get_data_returns_dict(self):
        data = CzechBankCodesData().get_data()
        assert isinstance(data, dict)

    def test_get_data_caches(self):
        codes = CzechBankCodesData()
        data1 = codes.get_data()
        data2 = codes.get_data()
        assert data1 is data2

    def test_get_source(self):
        source = CzechBankCodesData().get_source()
        assert source.name == "CZ Bank Codes"
        assert source.license == "Public domain"

    def test_validate_empty_data(self):
        codes = CzechBankCodesData()
        assert codes.validate() is False


class TestCzechCitiesData:
    def test_get_data_returns_set(self):
        data = CzechCitiesData().get_data()
        assert isinstance(data, set)

    def test_get_data_caches(self):
        cities = CzechCitiesData()
        data1 = cities.get_data()
        data2 = cities.get_data()
        assert data1 is data2

    def test_validate_empty_data(self):
        assert CzechCitiesData().validate() is False


class TestCzechPostalCodesData:
    def test_get_data_returns_set(self):
        data = CzechPostalCodesData().get_data()
        assert isinstance(data, set)

    def test_get_data_caches(self):
        codes = CzechPostalCodesData()
        data1 = codes.get_data()
        data2 = codes.get_data()
        assert data1 is data2

    def test_validate_empty_data(self):
        assert CzechPostalCodesData().validate() is False


class TestCzechNamesData:
    def test_get_data_structure(self):
        data = CzechNamesData().get_data()
        assert isinstance(data, dict)
        assert "male" in data
        assert "female" in data

    def test_get_data_caches(self):
        names = CzechNamesData()
        data1 = names.get_data()
        data2 = names.get_data()
        assert data1 is data2

    def test_validate_empty_data(self):
        assert CzechNamesData().validate() is False


class TestCzechModule:
    def setup_method(self):
        CountryRegistry.clear()

    def test_is_country_module(self):
        module = CzechModule()
        assert isinstance(module, CountryModule)

    def test_get_metadata(self):
        module = CzechModule()
        metadata = module.get_metadata()
        assert isinstance(metadata, CountryMetadata)
        assert metadata.code == "CZ"
        assert metadata.name == "Czech Republic"

    def test_get_bank_codes(self):
        module = CzechModule()
        data = module.get_bank_codes()
        assert isinstance(data, CzechBankCodesData)
        assert isinstance(data, CountryData)

    def test_get_cities(self):
        module = CzechModule()
        data = module.get_cities()
        assert isinstance(data, CzechCitiesData)

    def test_get_postal_codes(self):
        module = CzechModule()
        data = module.get_postal_codes()
        assert isinstance(data, CzechPostalCodesData)

    def test_get_names(self):
        module = CzechModule()
        data = module.get_names()
        assert isinstance(data, CzechNamesData)

    def test_get_insurance_codes(self):
        module = CzechModule()
        data = module.get_insurance_codes()
        assert isinstance(data, CzechInsuranceCodesData)

    def test_get_all_data(self):
        module = CzechModule()
        all_data = module.get_all_data()
        assert "bank_codes" in all_data
        assert "cities" in all_data
        assert "postal_codes" in all_data
        assert "names" in all_data
        assert "insurance_codes" in all_data

    def test_validate_all(self):
        module = CzechModule()
        results = module.validate_all()
        assert isinstance(results, dict)
        assert "insurance_codes" in results
        assert results["insurance_codes"] is True

    def test_get_all_data_caches(self):
        module = CzechModule()
        data1 = module.get_all_data()
        data2 = module.get_all_data()
        assert data1 is data2

    def test_registry_auto_registration(self):
        CountryRegistry.clear()
        CountryRegistry.register("cz", CzechModule)
        assert "cz" in CountryRegistry.list_countries()

    def test_registry_get(self):
        CountryRegistry.clear()
        CountryRegistry.register("cz", CzechModule)
        module = CountryRegistry.get("cz")
        assert isinstance(module, CzechModule)

    def test_registry_case_insensitive(self):
        CountryRegistry.clear()
        CountryRegistry.register("cz", CzechModule)
        module = CountryRegistry.get("CZ")
        assert isinstance(module, CzechModule)