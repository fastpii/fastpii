import pytest

from fastpii.countries.pl.data.bank_codes import PolishBankCodesData
from fastpii.countries.pl.data.cities import PolishCitiesData
from fastpii.countries.pl.data.insurance_codes import PolishInsuranceCodesData
from fastpii.countries.pl.data.names import PolishNamesData
from fastpii.countries.pl.data.postal_codes import PolishPostalCodesData
from fastpii.countries.pl.data.streets import PolishStreetsData
from fastpii.countries.pl.data.surnames import PolishSurnamesData


def _min_entries(data_class, min_count: int) -> bool:
    data = data_class().get_data()
    if isinstance(data, dict) and "male" in data:
        return len(data["male"]) + len(data["female"]) >= min_count
    return len(data) >= min_count


class TestBankCodesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(PolishBankCodesData, 1),
        reason="Bank codes data not populated",
    )
    def test_no_duplicates(self):
        data = PolishBankCodesData().get_data()
        assert len(data) == len(set(data.keys())), "Duplicate bank codes found"


class TestInsuranceCodesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(PolishInsuranceCodesData, 1),
        reason="Insurance codes data not populated",
    )
    def test_no_duplicates(self):
        data = PolishInsuranceCodesData().get_data()
        assert len(data) == len(set(data.keys())), "Duplicate insurance codes found"


class TestCitiesIntegrity:
    def test_all_lowercase(self):
        for city in PolishCitiesData().get_data():
            assert city == city.lower(), f"City '{city}' is not lowercase"

    def test_no_duplicates(self):
        data = PolishCitiesData().get_data()
        assert len(data) == len(set(data)), "Duplicate cities found"

    def test_minimum_entries(self):
        data = PolishCitiesData().get_data()
        assert len(data) >= 20, f"Expected 20+ cities, got {len(data)}"


class TestPostalCodesIntegrity:
    def test_format_dd_ddddd(self):
        for code in PolishPostalCodesData().get_data():
            assert len(code) == 6, f"Postal code '{code}' is not 6 chars (DD-DDD)"
            assert code[2] == "-", f"Postal code '{code}' missing dash separator"
            assert code[:2].isdigit(), f"Postal code '{code}' prefix not digits"
            assert code[3:].isdigit(), f"Postal code '{code}' suffix not digits"

    def test_no_duplicates(self):
        data = PolishPostalCodesData().get_data()
        assert len(data) == len(set(data)), "Duplicate postal codes found"

    def test_minimum_entries(self):
        data = PolishPostalCodesData().get_data()
        assert len(data) >= 100, f"Expected 100+ postal codes, got {len(data)}"


class TestNamesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(PolishNamesData, 1),
        reason="Names data not populated",
    )
    def test_all_lowercase(self):
        data = PolishNamesData().get_data()
        for name in data["male"]:
            assert name == name.lower(), f"Male name '{name}' is not lowercase"
        for name in data["female"]:
            assert name == name.lower(), f"Female name '{name}' is not lowercase"

    @pytest.mark.skipif(
        not _min_entries(PolishNamesData, 1),
        reason="Names data not populated",
    )
    def test_no_duplicates(self):
        data = PolishNamesData().get_data()
        male = data["male"]
        female = data["female"]
        assert len(male) == len(set(male)), "Duplicate male names found"
        assert len(female) == len(set(female)), "Duplicate female names found"

    @pytest.mark.skipif(
        not _min_entries(PolishNamesData, 1),
        reason="Names data not populated",
    )
    def test_has_male_and_female_keys(self):
        data = PolishNamesData().get_data()
        assert "male" in data
        assert "female" in data


class TestStreetsIntegrity:
    def test_all_lowercase(self):
        for street in PolishStreetsData().get_data():
            assert street == street.lower(), f"Street '{street}' is not lowercase"

    def test_no_duplicates(self):
        data = PolishStreetsData().get_data()
        assert len(data) == len(set(data)), "Duplicate streets found"

    def test_minimum_entries(self):
        data = PolishStreetsData().get_data()
        assert len(data) >= 50, f"Expected 50+ streets, got {len(data)}"


class TestSurnamesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(PolishSurnamesData, 1),
        reason="Surnames data not populated",
    )
    def test_all_lowercase(self):
        data = PolishSurnamesData().get_data()
        for name in data["male"]:
            assert name == name.lower(), f"Male surname '{name}' is not lowercase"
        for name in data["female"]:
            assert name == name.lower(), f"Female surname '{name}' is not lowercase"

    @pytest.mark.skipif(
        not _min_entries(PolishSurnamesData, 1),
        reason="Surnames data not populated",
    )
    def test_no_duplicates(self):
        data = PolishSurnamesData().get_data()
        male = data["male"]
        female = data["female"]
        assert len(male) == len(set(male)), "Duplicate male surnames found"
        assert len(female) == len(set(female)), "Duplicate female surnames found"

    @pytest.mark.skipif(
        not _min_entries(PolishSurnamesData, 1),
        reason="Surnames data not populated",
    )
    def test_has_male_and_female_keys(self):
        data = PolishSurnamesData().get_data()
        assert "male" in data
        assert "female" in data