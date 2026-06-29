"""Performance tests for data import and lookup times."""

import time

import pytest

from fastpii.countries.cz.data.bank_codes import CzechBankCodesData
from fastpii.countries.cz.data.cities import CzechCitiesData
from fastpii.countries.cz.data.insurance_codes import CzechInsuranceCodesData
from fastpii.countries.cz.data.names import CzechNamesData
from fastpii.countries.cz.data.postal_codes import CzechPostalCodesData


def _has_data(data_class, min_entries: int) -> bool:
    data = data_class().get_data()
    if isinstance(data, dict) and "male" in data:
        return len(data["male"]) + len(data["female"]) >= min_entries
    return len(data) >= min_entries


class TestImportTimes:
    """Test that data imports meet performance requirements."""

    def test_insurance_codes_import_time(self):
        codes = CzechInsuranceCodesData()
        elapsed = codes.get_import_time()
        assert elapsed < 10, f"Insurance codes import took {elapsed:.1f}ms, expected <10ms"

    @pytest.mark.skipif(
        not _has_data(CzechBankCodesData, 30),
        reason="Bank codes data not populated (run extract_cz_bank_codes.py)",
    )
    def test_bank_codes_import_time(self):
        codes = CzechBankCodesData()
        elapsed = codes.get_import_time()
        assert elapsed < 10, f"Bank codes import took {elapsed:.1f}ms, expected <10ms"

    @pytest.mark.skipif(
        not _has_data(CzechCitiesData, 6000),
        reason="Cities data not populated (run extract_cz_cities.py)",
    )
    def test_cities_import_time(self):
        cities = CzechCitiesData()
        elapsed = cities.get_import_time()
        assert elapsed < 100, f"Cities import took {elapsed:.1f}ms, expected <100ms"

    @pytest.mark.skipif(
        not _has_data(CzechPostalCodesData, 15000),
        reason="Postal codes data not populated (run extract_cz_postal_codes.py)",
    )
    def test_postal_codes_import_time(self):
        codes = CzechPostalCodesData()
        elapsed = codes.get_import_time()
        assert elapsed < 100, f"Postal codes import took {elapsed:.1f}ms, expected <100ms"

    @pytest.mark.skipif(
        not _has_data(CzechNamesData, 5000),
        reason="Names data not populated (run extract_cz_names.py)",
    )
    def test_names_import_time(self):
        names = CzechNamesData()
        elapsed = names.get_import_time()
        assert elapsed < 50, f"Names import took {elapsed:.1f}ms, expected <50ms"

    @pytest.mark.skipif(
        not _has_data(CzechBankCodesData, 1),
        reason="Data not populated — total import time requires real data",
    )
    def test_total_import_time(self):
        from fastpii.countries.cz.data import CzechModule

        module = CzechModule()
        times = module.benchmark_import_times()
        total = sum(times.values())
        assert total < 200, f"Total import took {total:.1f}ms, expected <200ms"


class TestLookupTimes:
    """Test that data lookups meet performance requirements."""

    def test_insurance_code_lookup(self):
        codes = CzechInsuranceCodesData()
        data = codes.get_data()
        start = time.perf_counter()
        for _ in range(1000):
            _ = "111" in data
        elapsed_ms = (time.perf_counter() - start) * 1000
        per_lookup = elapsed_ms / 1000
        assert per_lookup < 1, f"Insurance code lookup took {per_lookup:.4f}ms, expected <1ms"

    @pytest.mark.skipif(
        not _has_data(CzechCitiesData, 100),
        reason="Cities data not populated — lookup tests require real data",
    )
    def test_city_lookup(self):
        cities = CzechCitiesData()
        data = cities.get_data()
        sample = next(iter(data))
        start = time.perf_counter()
        for _ in range(1000):
            _ = sample in data
        elapsed_ms = (time.perf_counter() - start) * 1000
        per_lookup = elapsed_ms / 1000
        assert per_lookup < 1, f"City lookup took {per_lookup:.4f}ms, expected <1ms"
