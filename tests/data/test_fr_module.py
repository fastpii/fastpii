import pytest

from fastpii.countries.fr.data.bank_codes import FrenchBankCodesData
from fastpii.countries.fr.data.cities import FrenchCitiesData
from fastpii.countries.fr.data.insurance_codes import FrenchInsuranceCodesData
from fastpii.countries.fr.data.names import FrenchNamesData
from fastpii.countries.fr.data.postal_codes import FrenchPostalCodesData
from fastpii.countries.fr.data.streets import FrenchStreetsData
from fastpii.countries.fr.data.surnames import FrenchSurnamesData


def _min_entries(data_class, min_count: int) -> bool:
    data = data_class().get_data()
    if isinstance(data, dict) and "male" in data:
        return len(data["male"]) + len(data["female"]) >= min_count
    return len(data) >= min_count


class TestBankCodesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(FrenchBankCodesData, 1),
        reason="Bank codes data not populated",
    )
    def test_no_duplicates(self):
        data = FrenchBankCodesData().get_data()
        assert len(data) == len(set(data.keys())), "Duplicate bank codes found"


class TestInsuranceCodesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(FrenchInsuranceCodesData, 1),
        reason="Insurance codes data not populated",
    )
    def test_no_duplicates(self):
        data = FrenchInsuranceCodesData().get_data()
        assert len(data) == len(set(data.keys())), "Duplicate insurance codes found"


class TestCitiesIntegrity:
    def test_all_lowercase(self):
        for city in FrenchCitiesData().get_data():
            assert city == city.lower(), f"City '{city}' is not lowercase"

    def test_no_duplicates(self):
        data = FrenchCitiesData().get_data()
        assert len(data) == len(set(data)), "Duplicate cities found"

    def test_minimum_entries(self):
        data = FrenchCitiesData().get_data()
        assert len(data) >= 50, f"Expected 50+ cities, got {len(data)}"


class TestPostalCodesIntegrity:
    def test_format_all_5_digits(self):
        for code in FrenchPostalCodesData().get_data():
            assert len(code) == 5, f"Postal code '{code}' is not 5 digits"
            assert code.isdigit(), f"Postal code '{code}' contains non-digits"

    def test_no_duplicates(self):
        data = FrenchPostalCodesData().get_data()
        assert len(data) == len(set(data)), "Duplicate postal codes found"

    def test_minimum_entries(self):
        data = FrenchPostalCodesData().get_data()
        assert len(data) >= 50, f"Expected 50+ postal codes, got {len(data)}"


class TestNamesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(FrenchNamesData, 1),
        reason="Names data not populated",
    )
    def test_all_lowercase(self):
        data = FrenchNamesData().get_data()
        for name in data["male"]:
            assert name == name.lower(), f"Male name '{name}' is not lowercase"
        for name in data["female"]:
            assert name == name.lower(), f"Female name '{name}' is not lowercase"

    @pytest.mark.skipif(
        not _min_entries(FrenchNamesData, 1),
        reason="Names data not populated",
    )
    def test_no_duplicates(self):
        data = FrenchNamesData().get_data()
        male = data["male"]
        female = data["female"]
        assert len(male) == len(set(male)), "Duplicate male names found"
        assert len(female) == len(set(female)), "Duplicate female names found"

    @pytest.mark.skipif(
        not _min_entries(FrenchNamesData, 1),
        reason="Names data not populated",
    )
    def test_has_male_and_female_keys(self):
        data = FrenchNamesData().get_data()
        assert "male" in data
        assert "female" in data


class TestStreetsIntegrity:
    def test_all_lowercase(self):
        for street in FrenchStreetsData().get_data():
            assert street == street.lower(), f"Street '{street}' is not lowercase"

    def test_no_duplicates(self):
        data = FrenchStreetsData().get_data()
        assert len(data) == len(set(data)), "Duplicate streets found"

    def test_minimum_entries(self):
        data = FrenchStreetsData().get_data()
        assert len(data) >= 50, f"Expected 50+ streets, got {len(data)}"


class TestSurnamesIntegrity:
    @pytest.mark.skipif(
        not _min_entries(FrenchSurnamesData, 1),
        reason="Surnames data not populated",
    )
    def test_all_lowercase(self):
        data = FrenchSurnamesData().get_data()
        for name in data["male"]:
            assert name == name.lower(), f"Male surname '{name}' is not lowercase"
        for name in data["female"]:
            assert name == name.lower(), f"Female surname '{name}' is not lowercase"

    @pytest.mark.skipif(
        not _min_entries(FrenchSurnamesData, 1),
        reason="Surnames data not populated",
    )
    def test_no_duplicates(self):
        data = FrenchSurnamesData().get_data()
        male = data["male"]
        female = data["female"]
        assert len(male) == len(set(male)), "Duplicate male surnames found"
        assert len(female) == len(set(female)), "Duplicate female surnames found"

    @pytest.mark.skipif(
        not _min_entries(FrenchSurnamesData, 1),
        reason="Surnames data not populated",
    )
    def test_has_male_and_female_keys(self):
        data = FrenchSurnamesData().get_data()
        assert "male" in data
        assert "female" in data