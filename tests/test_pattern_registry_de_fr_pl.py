import re
from typing import TypeAlias

import pytest

from fastpii.countries.de.patterns import GermanPatternLoader
from fastpii.countries.fr.patterns import FrenchPatternLoader
from fastpii.countries.pl.patterns import PolishPatternLoader
from fastpii.patterns.base import PatternDefinition
from fastpii.patterns.regions import PatternLoader, get_region_loaders
from fastpii.patterns.registry import PatternRegistry


LoaderClass: TypeAlias = type[PatternLoader]


class TestGermanPatternLoader:
    def test_load_returns_expected_german_patterns(self):
        patterns = GermanPatternLoader.load()

        assert len(patterns) == 6
        assert all(isinstance(pattern, PatternDefinition) for pattern in patterns)
        assert all(pattern.region == "de" for pattern in patterns)

    def test_german_entity_types_match_expected_list(self):
        patterns = GermanPatternLoader.load()

        entity_types = [pattern.entity_type for pattern in patterns]
        assert entity_types == [
            "steuer_id",
            "ust_id",
            "handelsregister",
            "postal_code",
            "phone",
            "email",
        ]

    @pytest.mark.parametrize(
        ("entity_type", "sample_text", "expected_match"),
        [
            ("steuer_id", "Steuer-ID: 52481530987", "52481530987"),
            ("ust_id", "USt-IdNr: DE123456789", "DE123456789"),
            ("handelsregister", "Handelsregister: HRB 12345 Berlin", "HRB 12345 Berlin"),
            ("postal_code", "PLZ 10115 Berlin", "10115"),
            ("phone", "Telefon: +49 15123456789", "+49 15123456789"),
            ("email", "E-Mail: max.mustermann@example.de", "max.mustermann@example.de"),
        ],
    )
    def test_german_patterns_compile_and_match_examples(
        self, entity_type: str, sample_text: str, expected_match: str
    ):
        patterns = GermanPatternLoader.load()
        pattern = next(pattern for pattern in patterns if pattern.entity_type == entity_type)

        assert isinstance(pattern.compiled, re.Pattern)
        match = pattern.compiled.search(sample_text)
        assert match is not None
        assert match.group(0) == expected_match

    @pytest.mark.parametrize(
        "entity_type",
        ["steuer_id", "ust_id", "handelsregister", "postal_code", "phone", "email"],
    )
    def test_german_patterns_have_context_words(self, entity_type: str):
        patterns = GermanPatternLoader.load()
        pattern = next(pattern for pattern in patterns if pattern.entity_type == entity_type)

        assert pattern.context_words
        assert isinstance(pattern.context_words, list)

    @pytest.mark.parametrize(
        ("entity_type", "value"),
        [
            ("steuer_id", "52481530987"),
            ("ust_id", "123456789"),
            ("postal_code", "10115"),
            ("email", "max.mustermann@example.de"),
        ],
    )
    def test_german_validation_regex_matches_expected_inputs(self, entity_type: str, value: str):
        patterns = GermanPatternLoader.load()
        pattern = next(pattern for pattern in patterns if pattern.entity_type == entity_type)

        assert pattern.validation_compiled is not None
        assert pattern.validation_compiled.match(value) is not None


class TestFrenchPatternLoader:
    def test_load_returns_expected_french_patterns(self):
        patterns = FrenchPatternLoader.load()

        assert len(patterns) == 7
        assert all(isinstance(pattern, PatternDefinition) for pattern in patterns)
        assert all(pattern.region == "fr" for pattern in patterns)

    def test_french_entity_types_match_expected_list(self):
        patterns = FrenchPatternLoader.load()

        entity_types = [pattern.entity_type for pattern in patterns]
        assert entity_types == [
            "siren",
            "siret",
            "insee",
            "postal_code",
            "phone",
            "phone",
            "email",
        ]

    @pytest.mark.parametrize(
        ("entity_type", "name", "sample_text", "expected_match"),
        [
            ("siren", "standard", "SIREN: 732829320", "732829320"),
            ("siret", "standard", "SIRET: 73282932000074", "73282932000074"),
            ("insee", "standard", "NIR: 184127645108946", "184127645108946"),
            ("postal_code", "standard", "Code postal 75008 Paris", "75008"),
            ("phone", "mobile", "Portable: +33 6 12 34 56 78", "+33 6 12 34 56 78"),
            ("phone", "landline", "Téléphone: 01 44 55 66 77", "01 44 55 66 77"),
            ("email", "standard", "Courriel: jean.dupont@example.fr", "jean.dupont@example.fr"),
        ],
    )
    def test_french_patterns_compile_and_match_examples(
        self, entity_type: str, name: str, sample_text: str, expected_match: str
    ):
        patterns = FrenchPatternLoader.load()
        pattern = next(
            pattern for pattern in patterns if pattern.entity_type == entity_type and pattern.name == name
        )

        assert isinstance(pattern.compiled, re.Pattern)
        match = pattern.compiled.search(sample_text)
        assert match is not None
        assert match.group(0) == expected_match

    @pytest.mark.parametrize(
        ("entity_type", "name"),
        [
            ("siren", "standard"),
            ("siret", "standard"),
            ("insee", "standard"),
            ("postal_code", "standard"),
            ("phone", "mobile"),
            ("phone", "landline"),
            ("email", "standard"),
        ],
    )
    def test_french_patterns_have_context_words(self, entity_type: str, name: str):
        patterns = FrenchPatternLoader.load()
        pattern = next(
            pattern for pattern in patterns if pattern.entity_type == entity_type and pattern.name == name
        )

        assert pattern.context_words
        assert isinstance(pattern.context_words, list)

    @pytest.mark.parametrize(
        ("entity_type", "value"),
        [
            ("siren", "732829320"),
            ("siret", "73282932000074"),
            ("insee", "184127645108946"),
            ("postal_code", "75008"),
            ("email", "jean.dupont@example.fr"),
        ],
    )
    def test_french_validation_regex_matches_expected_inputs(self, entity_type: str, value: str):
        patterns = FrenchPatternLoader.load()
        pattern = next(pattern for pattern in patterns if pattern.entity_type == entity_type)

        assert pattern.validation_compiled is not None
        assert pattern.validation_compiled.match(value) is not None


class TestPolishPatternLoader:
    def test_load_returns_expected_polish_patterns(self):
        patterns = PolishPatternLoader.load()

        assert len(patterns) == 7
        assert all(isinstance(pattern, PatternDefinition) for pattern in patterns)
        assert all(pattern.region == "pl" for pattern in patterns)

    def test_polish_entity_types_match_expected_list(self):
        patterns = PolishPatternLoader.load()

        entity_types = [pattern.entity_type for pattern in patterns]
        assert entity_types == [
            "pesel",
            "nip",
            "regon",
            "postal_code",
            "phone",
            "phone",
            "email",
        ]

    @pytest.mark.parametrize(
        ("entity_type", "name", "sample_text", "expected_match"),
        [
            ("pesel", "standard", "PESEL: 44051401458", "44051401458"),
            ("nip", "standard", "NIP: 1234563218", "1234563218"),
            ("regon", "standard", "REGON: 123456785", "123456785"),
            ("postal_code", "standard", "Kod pocztowy 00-001 Warszawa", "00-001"),
            ("phone", "mobile", "Telefon: +48 501234567", "+48 501234567"),
            ("phone", "landline", "Telefon: 22 123 45 67", "22 123 45 67"),
            ("email", "standard", "E-mail: jan.kowalski@example.pl", "jan.kowalski@example.pl"),
        ],
    )
    def test_polish_patterns_compile_and_match_examples(
        self, entity_type: str, name: str, sample_text: str, expected_match: str
    ):
        patterns = PolishPatternLoader.load()
        pattern = next(
            pattern for pattern in patterns if pattern.entity_type == entity_type and pattern.name == name
        )

        assert isinstance(pattern.compiled, re.Pattern)
        match = pattern.compiled.search(sample_text)
        assert match is not None
        assert match.group(0) == expected_match

    @pytest.mark.parametrize(
        ("entity_type", "name"),
        [
            ("pesel", "standard"),
            ("nip", "standard"),
            ("regon", "standard"),
            ("postal_code", "standard"),
            ("phone", "mobile"),
            ("phone", "landline"),
            ("email", "standard"),
        ],
    )
    def test_polish_patterns_have_context_words(self, entity_type: str, name: str):
        patterns = PolishPatternLoader.load()
        pattern = next(
            pattern for pattern in patterns if pattern.entity_type == entity_type and pattern.name == name
        )

        assert pattern.context_words
        assert isinstance(pattern.context_words, list)

    @pytest.mark.parametrize(
        ("entity_type", "value"),
        [
            ("pesel", "44051401458"),
            ("nip", "1234563218"),
            ("regon", "123456785"),
            ("regon", "12345678512347"),
            ("postal_code", "00-001"),
            ("email", "jan.kowalski@example.pl"),
        ],
    )
    def test_polish_validation_regex_matches_expected_inputs(self, entity_type: str, value: str):
        patterns = PolishPatternLoader.load()
        pattern = next(pattern for pattern in patterns if pattern.entity_type == entity_type)

        assert pattern.validation_compiled is not None
        assert pattern.validation_compiled.match(value) is not None


class TestRegionLoaderDispatch:
    def test_get_region_loaders_returns_all_supported_countries(self):
        loaders = get_region_loaders()

        assert set(loaders.keys()) == {"cz", "de", "fr", "pl"}

    @pytest.mark.parametrize("region_code", ["cz", "de", "fr", "pl"])
    def test_each_loader_class_loads_pattern_definitions(self, region_code: str):
        loaders: dict[str, LoaderClass] = get_region_loaders()
        loader_class: LoaderClass = loaders[region_code]

        assert hasattr(loader_class, "load")

        patterns = loader_class.load()
        assert isinstance(patterns, list)
        assert patterns
        assert all(isinstance(pattern, PatternDefinition) for pattern in patterns)
        assert all(pattern.region == region_code for pattern in patterns)
        assert all(isinstance(pattern.compiled, re.Pattern) for pattern in patterns)


class TestCrossCountryIsolation:
    def test_phone_patterns_are_isolated_by_region(self):
        registry = PatternRegistry()
        registry.load_all_regions()

        de_patterns = registry.get_patterns("phone", "de")
        fr_patterns = registry.get_patterns("phone", "fr")

        assert len(de_patterns) == 1
        assert {pattern.region for pattern in de_patterns} == {"de"}
        assert {pattern.name for pattern in de_patterns} == {"standard"}

        assert len(fr_patterns) == 2
        assert {pattern.region for pattern in fr_patterns} == {"fr"}
        assert {pattern.name for pattern in fr_patterns} == {"mobile", "landline"}

    def test_postal_code_patterns_are_isolated_by_region(self):
        registry = PatternRegistry()
        registry.load_all_regions()

        pl_patterns = registry.get_patterns("postal_code", "pl")

        assert len(pl_patterns) == 1
        assert {pattern.region for pattern in pl_patterns} == {"pl"}
        assert pl_patterns[0].entity_type == "postal_code"
        assert pl_patterns[0].regex == r"\b(\d{2})[-\s]?(\d{3})\b"


class TestPatternRegistryAutoDiscovery:
    def test_load_all_regions_loads_all_supported_regions(self):
        registry = PatternRegistry()

        assert registry.get_loaded_regions() == []

        registry.load_all_regions()

        assert set(registry.get_available_regions()) == {"cz", "de", "fr", "pl"}
        assert set(registry.get_loaded_regions()) == {"cz", "de", "fr", "pl"}

    def test_load_patterns_loads_single_region_lazily(self):
        registry = PatternRegistry()

        registry.load_patterns("de")

        assert set(registry.get_loaded_regions()) == {"de"}
        assert registry.get_patterns("steuer_id", "de")
        assert registry.get_patterns("steuer_id", "fr") == []


class TestPatternDefinitionFields:
    @pytest.mark.parametrize("loader_class, region_code", [
        (GermanPatternLoader, "de"),
        (FrenchPatternLoader, "fr"),
        (PolishPatternLoader, "pl"),
    ])
    def test_patterns_have_expected_field_types(self, loader_class: LoaderClass, region_code: str):
        patterns: list[PatternDefinition] = loader_class.load()

        for pattern in patterns:
            assert isinstance(pattern.entity_type, str)
            assert isinstance(pattern.name, str)
            assert pattern.region == region_code
            assert isinstance(pattern.score, float)
            assert isinstance(pattern.context_words, list)
            assert isinstance(pattern.compiled, re.Pattern)


class TestPatternValidationRegex:
    @pytest.mark.parametrize(
        ("loader_class", "entity_type", "value"),
        [
            (GermanPatternLoader, "steuer_id", "52481530987"),
            (GermanPatternLoader, "ust_id", "123456789"),
            (FrenchPatternLoader, "siren", "732829320"),
            (FrenchPatternLoader, "siret", "73282932000074"),
            (FrenchPatternLoader, "insee", "184127645108946"),
            (PolishPatternLoader, "pesel", "44051401458"),
            (PolishPatternLoader, "nip", "1234563218"),
            (PolishPatternLoader, "regon", "123456785"),
            (PolishPatternLoader, "regon", "12345678512347"),
        ],
    )
    def test_validation_patterns_compile_and_match_expected_inputs(
        self, loader_class: LoaderClass, entity_type: str, value: str
    ):
        patterns: list[PatternDefinition] = loader_class.load()
        pattern = next(pattern for pattern in patterns if pattern.entity_type == entity_type)

        assert pattern.validation_regex is not None
        assert pattern.validation_compiled is not None
        assert isinstance(pattern.validation_compiled, re.Pattern)
        assert pattern.validation_compiled.match(value) is not None
