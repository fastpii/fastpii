"""Tests for fastpii.data.base module."""

from datetime import datetime

import pytest

from fastpii.data.base import CountryData, CountryMetadata, CountryModule, DataSource

DT = datetime(2025, 1, 15)


def _make_source(name: str = "Test", count: int = 1) -> DataSource:
    return DataSource(name=name, url="https://example.com", license="MIT", last_updated=DT, entry_count=count)


class _DictData(CountryData[dict[str, str]]):
    def get_data(self) -> dict[str, str]:
        return {"0100": "Test Bank"}

    def get_source(self) -> DataSource:
        return _make_source()

    def validate(self) -> bool:
        return bool(self.get_data())


class _SetData(CountryData[set[str]]):
    def get_data(self) -> set[str]:
        return {"praha", "brno"}

    def get_source(self) -> DataSource:
        return _make_source(name="Test Set", count=2)

    def validate(self) -> bool:
        return bool(self.get_data())


class _NamesData(CountryData[dict[str, set[str]]]):
    def get_data(self) -> dict[str, set[str]]:
        return {"male": {"jan"}, "female": {"jana"}}

    def get_source(self) -> DataSource:
        return _make_source(name="Test Names", count=2)

    def validate(self) -> bool:
        return bool(self.get_data())


class TestDataSource:
    def test_creation(self):
        source = DataSource(
            name="Test Source",
            url="https://example.com",
            license="MIT",
            last_updated=datetime(2025, 1, 15),
            entry_count=100,
        )
        assert source.name == "Test Source"
        assert source.url == "https://example.com"
        assert source.license == "MIT"
        assert source.last_updated == datetime(2025, 1, 15)
        assert source.entry_count == 100

    def test_frozen(self):
        source = DataSource(
            name="Test",
            url="https://example.com",
            license="MIT",
            last_updated=datetime(2025, 1, 15),
            entry_count=100,
        )
        with pytest.raises(AttributeError):
            source.name = "Changed"

    def test_equality(self):
        dt = datetime(2025, 1, 15)
        s1 = DataSource(name="Test", url="https://example.com", license="MIT", last_updated=dt, entry_count=100)
        s2 = DataSource(name="Test", url="https://example.com", license="MIT", last_updated=dt, entry_count=100)
        assert s1 == s2


class TestCountryMetadata:
    def test_creation(self):
        metadata = CountryMetadata(
            code="CZ",
            name="Czech Republic",
            language_codes=("cs",),
            currency_code="CZK",
        )
        assert metadata.code == "CZ"
        assert metadata.name == "Czech Republic"
        assert metadata.language_codes == ("cs",)
        assert metadata.currency_code == "CZK"

    def test_frozen(self):
        metadata = CountryMetadata(code="CZ", name="Czech Republic", language_codes=("cs",), currency_code="CZK")
        with pytest.raises(AttributeError):
            metadata.code = "SK"

    def test_equality(self):
        m1 = CountryMetadata(code="CZ", name="Czech Republic", language_codes=("cs",), currency_code="CZK")
        m2 = CountryMetadata(code="CZ", name="Czech Republic", language_codes=("cs",), currency_code="CZK")
        assert m1 == m2


class TestCountryData:
    def test_abstract(self):
        with pytest.raises(TypeError):
            CountryData()

    def test_concrete_subclass(self):
        data = _DictData()
        assert data.get_data() == {"0100": "Test Bank"}
        assert data.validate() is True
        assert data.get_entry_count() == 1

    def test_validate_returns_false_for_empty(self):
        class EmptyData(CountryData[dict[str, str]]):
            def get_data(self) -> dict[str, str]:
                return {}

            def get_source(self) -> DataSource:
                return _make_source(name="Empty", count=0)

            def validate(self) -> bool:
                return bool(self.get_data())

        data = EmptyData()
        assert data.validate() is False

    def test_get_import_time(self):
        data = _DictData()
        time_ms = data.get_import_time()
        assert isinstance(time_ms, float)
        assert time_ms >= 0


class TestCountryModule:
    def test_abstract(self):
        with pytest.raises(TypeError):
            CountryModule()

    def test_concrete_subclass(self):
        class TestModule(CountryModule):
            def get_metadata(self) -> CountryMetadata:
                return CountryMetadata(code="XX", name="Test Country", language_codes=("xx",), currency_code="XXX")

            def get_bank_codes(self) -> CountryData:
                return _DictData()

            def get_cities(self) -> CountryData:
                return _SetData()

            def get_postal_codes(self) -> CountryData:
                return _SetData()

            def get_names(self) -> CountryData:
                return _NamesData()

            def get_insurance_codes(self) -> CountryData:
                return _DictData()

            def get_streets(self) -> CountryData:
                return _SetData()

            def get_surnames(self) -> CountryData:
                return _NamesData()

        module = TestModule()
        assert module.get_metadata().code == "XX"
        assert module.get_bank_codes().validate() is True
        assert module.get_cities().validate() is True

        all_data = module.get_all_data()
        assert "bank_codes" in all_data
        assert "cities" in all_data
        assert "postal_codes" in all_data
        assert "names" in all_data
        assert "insurance_codes" in all_data
        assert "streets" in all_data
        assert "surnames" in all_data

        validation = module.validate_all()
        assert all(validation.values())

        times = module.benchmark_import_times()
        assert "bank_codes" in times
        assert all(isinstance(t, float) for t in times.values())