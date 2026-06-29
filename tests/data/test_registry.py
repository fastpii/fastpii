"""Tests for fastpii.data.registry module."""

from datetime import datetime

import pytest

from fastpii.data.base import CountryData, CountryMetadata, CountryModule, DataSource
from fastpii.data.registry import CountryRegistry


class SimpleData(CountryData[dict[str, str]]):
    def get_data(self) -> dict[str, str]:
        return {"test": "data"}

    def get_source(self) -> DataSource:
        return DataSource(
            name="Test", url="https://example.com", license="MIT",
            last_updated=datetime(2025, 1, 15), entry_count=1,
        )

    def validate(self) -> bool:
        return bool(self.get_data())


class StubModule(CountryModule):
    def get_metadata(self) -> CountryMetadata:
        return CountryMetadata(code="XX", name="Test Country", language_codes=("xx",), currency_code="XXX")

    def get_bank_codes(self) -> CountryData:
        return SimpleData()

    def get_cities(self) -> CountryData:
        return SimpleData()

    def get_postal_codes(self) -> CountryData:
        return SimpleData()

    def get_names(self) -> CountryData:
        return SimpleData()


class AnotherStubModule(CountryModule):
    def get_metadata(self) -> CountryMetadata:
        return CountryMetadata(code="YY", name="Another Country", language_codes=("yy",), currency_code="YYY")

    def get_bank_codes(self) -> CountryData:
        return SimpleData()

    def get_cities(self) -> CountryData:
        return SimpleData()

    def get_postal_codes(self) -> CountryData:
        return SimpleData()

    def get_names(self) -> CountryData:
        return SimpleData()


class TestCountryRegistry:
    def setup_method(self):
        CountryRegistry.clear()

    def test_register_and_get(self):
        CountryRegistry.register("xx", StubModule)
        module = CountryRegistry.get("xx")
        assert isinstance(module, StubModule)
        assert isinstance(module, CountryModule)

    def test_case_insensitive_get(self):
        CountryRegistry.register("xx", StubModule)
        assert isinstance(CountryRegistry.get("XX"), StubModule)
        assert isinstance(CountryRegistry.get("Xx"), StubModule)
        assert isinstance(CountryRegistry.get("xx"), StubModule)

    def test_case_insensitive_register(self):
        CountryRegistry.register("XX", StubModule)
        assert isinstance(CountryRegistry.get("xx"), StubModule)

    def test_get_unknown_raises_keyerror(self):
        with pytest.raises(KeyError, match="not registered"):
            CountryRegistry.get("unknown")

    def test_list_countries(self):
        CountryRegistry.register("xx", StubModule)
        CountryRegistry.register("yy", AnotherStubModule)
        countries = CountryRegistry.list_countries()
        assert "xx" in countries
        assert "yy" in countries

    def test_list_countries_empty(self):
        assert CountryRegistry.list_countries() == []

    def test_get_all(self):
        CountryRegistry.register("xx", StubModule)
        CountryRegistry.register("yy", AnotherStubModule)
        all_modules = CountryRegistry.get_all()
        assert "xx" in all_modules
        assert "yy" in all_modules
        assert isinstance(all_modules["xx"], StubModule)
        assert isinstance(all_modules["yy"], AnotherStubModule)

    def test_get_metadata(self):
        CountryRegistry.register("xx", StubModule)
        metadata = CountryRegistry.get_metadata("xx")
        assert metadata.code == "XX"
        assert metadata.name == "Test Country"

    def test_clear(self):
        CountryRegistry.register("xx", StubModule)
        assert "xx" in CountryRegistry.list_countries()
        CountryRegistry.clear()
        assert CountryRegistry.list_countries() == []

    def test_overwrite_registration(self):
        CountryRegistry.register("xx", StubModule)
        CountryRegistry.register("xx", AnotherStubModule)
        module = CountryRegistry.get("xx")
        assert isinstance(module, AnotherStubModule)