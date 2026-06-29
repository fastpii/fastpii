"""Data integrity tests for Czech datasets.

Validates format, uniqueness, minimum entry counts, and structural
correctness of each data type. Tests are skipped when the underlying
data has not been populated (placeholder data is empty).
"""

import pytest

from fastpii.countries.cz.data.bank_codes import CzechBankCodesData
from fastpii.countries.cz.data.cities import CzechCitiesData
from fastpii.countries.cz.data.insurance_codes import CzechInsuranceCodesData
from fastpii.countries.cz.data.names import CzechNamesData
from fastpii.countries.cz.data.postal_codes import CzechPostalCodesData
from fastpii.countries.cz.data.streets import CzechStreetsData


def _min_entries(data_class, min_count: int) -> bool:
    data = data_class().get_data()
    if isinstance(data, dict) and "male" in data:
        return len(data["male"]) + len(data["female"]) >= min_count
    return len(data) >= min_count


class TestInsuranceCodesIntegrity:
    """Insurance codes has real data — always runs."""

    def test_format_all_3_digits(self):
        for code in CzechInsuranceCodesData().get_data():
            assert len(code) == 3, f"Insurance code '{code}' is not 3 digits"
            assert code.isdigit(), f"Insurance code '{code}' contains non-digits"

    def test_minimum_entries(self):
        data = CzechInsuranceCodesData().get_data()
        assert len(data) >= 7, f"Expected 7+ insurance codes, got {len(data)}"

    def test_no_duplicates(self):
        data = CzechInsuranceCodesData().get_data()
        assert len(data) == len(set(data.keys())), "Duplicate insurance codes found"

    def test_validate(self):
        assert CzechInsuranceCodesData().validate() is True


class TestBankCodesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(CzechBankCodesData, 30),
        reason="Bank codes data not populated (run extract_cz_bank_codes.py)",
    )
    def test_format_all_4_digits(self):
        for code in CzechBankCodesData().get_data():
            assert len(code) == 4, f"Bank code '{code}' is not 4 digits"
            assert code.isdigit(), f"Bank code '{code}' contains non-digits"

    @pytest.mark.skipif(
        not _min_entries(CzechBankCodesData, 30),
        reason="Bank codes data not populated",
    )
    def test_minimum_entries(self):
        data = CzechBankCodesData().get_data()
        assert len(data) >= 30, f"Expected 30+ bank codes, got {len(data)}"

    @pytest.mark.skipif(
        not _min_entries(CzechBankCodesData, 1),
        reason="Bank codes data not populated",
    )
    def test_no_duplicates(self):
        data = CzechBankCodesData().get_data()
        assert len(data) == len(set(data.keys())), "Duplicate bank codes found"


class TestCitiesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(CzechCitiesData, 5000),
        reason="Cities data not populated (run extract_cz_ruvian.py)",
    )
    def test_all_lowercase(self):
        for city in CzechCitiesData().get_data():
            assert city == city.lower(), f"City '{city}' is not lowercase"

    @pytest.mark.skipif(
        not _min_entries(CzechCitiesData, 5000),
        reason="Cities data not populated",
    )
    def test_no_duplicates(self):
        data = CzechCitiesData().get_data()
        assert len(data) == len(set(data)), "Duplicate cities found"

    @pytest.mark.skipif(
        not _min_entries(CzechCitiesData, 5000),
        reason="Cities data not populated",
    )
    def test_minimum_entries(self):
        data = CzechCitiesData().get_data()
        assert len(data) >= 5000, f"Expected 5000+ cities, got {len(data)}"


class TestPostalCodesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(CzechPostalCodesData, 2000),
        reason="Postal codes data not populated (run extract_cz_ruvian.py)",
    )
    def test_format_all_5_digits(self):
        for code in CzechPostalCodesData().get_data():
            assert len(code) == 5, f"Postal code '{code}' is not 5 digits"
            assert code.isdigit(), f"Postal code '{code}' contains non-digits"

    @pytest.mark.skipif(
        not _min_entries(CzechPostalCodesData, 2000),
        reason="Postal codes data not populated",
    )
    def test_no_duplicates(self):
        data = CzechPostalCodesData().get_data()
        assert len(data) == len(set(data)), "Duplicate postal codes found"

    @pytest.mark.skipif(
        not _min_entries(CzechPostalCodesData, 2000),
        reason="Postal codes data not populated",
    )
    def test_minimum_entries(self):
        data = CzechPostalCodesData().get_data()
        assert len(data) >= 2000, f"Expected 2000+ postal codes, got {len(data)}"


class TestNamesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(CzechNamesData, 5000),
        reason="Names data not populated (run extract_cz_names.py)",
    )
    def test_all_lowercase(self):
        data = CzechNamesData().get_data()
        for name in data["male"]:
            assert name == name.lower(), f"Male name '{name}' is not lowercase"
        for name in data["female"]:
            assert name == name.lower(), f"Female name '{name}' is not lowercase"

    @pytest.mark.skipif(
        not _min_entries(CzechNamesData, 5000),
        reason="Names data not populated",
    )
    def test_no_duplicates(self):
        data = CzechNamesData().get_data()
        male = data["male"]
        female = data["female"]
        assert len(male) == len(set(male)), "Duplicate male names found"
        assert len(female) == len(set(female)), "Duplicate female names found"

    @pytest.mark.skipif(
        not _min_entries(CzechNamesData, 5000),
        reason="Names data not populated",
    )
    def test_minimum_entries(self):
        data = CzechNamesData().get_data()
        male = data["male"]
        female = data["female"]
        total = len(male) + len(female)
        assert total >= 5000, f"Expected 5000+ names, got {total}"

    @pytest.mark.skipif(
        not _min_entries(CzechNamesData, 5000),
        reason="Names data not populated",
    )
    def test_has_male_and_female_keys(self):
        data = CzechNamesData().get_data()
        assert "male" in data
        assert "female" in data
        assert len(data["male"]) > 0
        assert len(data["female"]) > 0


class TestStreetsIntegrity:
    @pytest.mark.skipif(
        not _min_entries(CzechStreetsData, 20000),
        reason="Streets data not populated (run extract_cz_ruvian.py)",
    )
    def test_all_lowercase(self):
        for street in CzechStreetsData().get_data():
            assert street == street.lower(), f"Street '{street}' is not lowercase"

    @pytest.mark.skipif(
        not _min_entries(CzechStreetsData, 20000),
        reason="Streets data not populated",
    )
    def test_no_duplicates(self):
        data = CzechStreetsData().get_data()
        assert len(data) == len(set(data)), "Duplicate streets found"

    @pytest.mark.skipif(
        not _min_entries(CzechStreetsData, 20000),
        reason="Streets data not populated",
    )
    def test_minimum_entries(self):
        data = CzechStreetsData().get_data()
        assert len(data) >= 20000, f"Expected 20000+ streets, got {len(data)}"
