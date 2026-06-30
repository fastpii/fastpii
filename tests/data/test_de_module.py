import pytest

from fastpii.countries.de.data.bank_codes import GermanBankCodesData
from fastpii.countries.de.data.cities import GermanCitiesData
from fastpii.countries.de.data.insurance_codes import GermanInsuranceCodesData
from fastpii.countries.de.data.names import GermanNamesData
from fastpii.countries.de.data.postal_codes import GermanPostalCodesData
from fastpii.countries.de.data.streets import GermanStreetsData
from fastpii.countries.de.data.surnames import GermanSurnamesData


def _min_entries(data_class, min_count: int) -> bool:
    data = data_class().get_data()
    if isinstance(data, dict) and "male" in data:
        return len(data["male"]) + len(data["female"]) >= min_count
    return len(data) >= min_count


class TestBankCodesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(GermanBankCodesData, 1),
        reason="Bank codes data not populated",
    )
    def test_format_all_8_digit_bank_codes(self):
        for code in GermanBankCodesData().get_data():
            assert len(code) == 8, f"Bank code '{code}' is not 8 digits"
            assert code.isdigit(), f"Bank code '{code}' contains non-digits"

    @pytest.mark.skipif(
        not _min_entries(GermanBankCodesData, 1),
        reason="Bank codes data not populated",
    )
    def test_no_duplicates(self):
        data = GermanBankCodesData().get_data()
        assert len(data) == len(set(data.keys())), "Duplicate bank codes found"


class TestInsuranceCodesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(GermanInsuranceCodesData, 1),
        reason="Insurance codes data not populated",
    )
    def test_no_duplicates(self):
        data = GermanInsuranceCodesData().get_data()
        assert len(data) == len(set(data.keys())), "Duplicate insurance codes found"


class TestCitiesIntegrity:
    def test_all_lowercase(self):
        for city in GermanCitiesData().get_data():
            assert city == city.lower(), f"City '{city}' is not lowercase"

    def test_no_duplicates(self):
        data = GermanCitiesData().get_data()
        assert len(data) == len(set(data)), "Duplicate cities found"

    def test_minimum_entries(self):
        data = GermanCitiesData().get_data()
        assert len(data) >= 50, f"Expected 50+ cities, got {len(data)}"


class TestPostalCodesIntegrity:
    def test_format_all_5_digits(self):
        for code in GermanPostalCodesData().get_data():
            assert len(code) == 5, f"Postal code '{code}' is not 5 digits"
            assert code.isdigit(), f"Postal code '{code}' contains non-digits"

    def test_no_duplicates(self):
        data = GermanPostalCodesData().get_data()
        assert len(data) == len(set(data)), "Duplicate postal codes found"

    def test_minimum_entries(self):
        data = GermanPostalCodesData().get_data()
        assert len(data) >= 100, f"Expected 100+ postal codes, got {len(data)}"


class TestNamesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(GermanNamesData, 1),
        reason="Names data not populated",
    )
    def test_all_lowercase(self):
        data = GermanNamesData().get_data()
        for name in data["male"]:
            assert name == name.lower(), f"Male name '{name}' is not lowercase"
        for name in data["female"]:
            assert name == name.lower(), f"Female name '{name}' is not lowercase"

    @pytest.mark.skipif(
        not _min_entries(GermanNamesData, 1),
        reason="Names data not populated",
    )
    def test_no_duplicates(self):
        data = GermanNamesData().get_data()
        male = data["male"]
        female = data["female"]
        assert len(male) == len(set(male)), "Duplicate male names found"
        assert len(female) == len(set(female)), "Duplicate female names found"

    @pytest.mark.skipif(
        not _min_entries(GermanNamesData, 1),
        reason="Names data not populated",
    )
    def test_has_male_and_female_keys(self):
        data = GermanNamesData().get_data()
        assert "male" in data
        assert "female" in data


class TestStreetsIntegrity:
    def test_all_lowercase(self):
        for street in GermanStreetsData().get_data():
            assert street == street.lower(), f"Street '{street}' is not lowercase"

    def test_no_duplicates(self):
        data = GermanStreetsData().get_data()
        assert len(data) == len(set(data)), "Duplicate streets found"

    def test_minimum_entries(self):
        data = GermanStreetsData().get_data()
        assert len(data) >= 50, f"Expected 50+ streets, got {len(data)}"


class TestSurnamesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(GermanSurnamesData, 1),
        reason="Surnames data not populated",
    )
    def test_all_lowercase(self):
        data = GermanSurnamesData().get_data()
        for name in data["male"]:
            assert name == name.lower(), f"Male surname '{name}' is not lowercase"
        for name in data["female"]:
            assert name == name.lower(), f"Female surname '{name}' is not lowercase"

    @pytest.mark.skipif(
        not _min_entries(GermanSurnamesData, 1),
        reason="Surnames data not populated",
    )
    def test_no_duplicates(self):
        data = GermanSurnamesData().get_data()
        male = data["male"]
        female = data["female"]
        assert len(male) == len(set(male)), "Duplicate male surnames found"
        assert len(female) == len(set(female)), "Duplicate female surnames found"

    @pytest.mark.skipif(
        not _min_entries(GermanSurnamesData, 1),
        reason="Surnames data not populated",
    )
    def test_has_male_and_female_keys(self):
        data = GermanSurnamesData().get_data()
        assert "male" in data
        assert "female" in data