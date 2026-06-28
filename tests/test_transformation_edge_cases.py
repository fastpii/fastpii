"""
Tests for transformation edge cases — value/span mismatches, multi-region,
custom strategies, and the TransformationEngine.

These tests cover the bug where mask() used len(finding.value) instead of
(finding.end - finding.start), producing wrong-length output when detectors
normalize values (strip spaces, dashes, slashes, country prefixes).
"""

import pytest

from fastpii import (
    FastPII,
    PrivacyGuard,
    DEFAULT_PRIORITY,
    TransformationEngine,
    AnonymizeStrategy,
    RedactStrategy,
    MaskStrategy,
    RemoveStrategy,
)
from fastpii.countries.cz import CzechPack
from fastpii.countries.pl import PolishPack
from fastpii.countries.de import GermanPack
from fastpii.countries.fr import FrenchPack


@pytest.fixture
def cz_engine():
    engine = FastPII(priority=DEFAULT_PRIORITY)
    engine.register(CzechPack())
    return engine


@pytest.fixture
def guard():
    return PrivacyGuard(regions=["cz"])


@pytest.fixture
def multi_guard():
    return PrivacyGuard(regions=["cz", "pl", "de", "fr"])


class TestValueSpanMismatch:
    """Verify transformations handle detectors that normalize values."""

    def test_mask_preserves_length_phone_with_spaces(self, cz_engine):
        text = "Tel: +420 777 888 999"
        masked = cz_engine.mask(text)
        assert len(masked) == len(text)

    def test_mask_preserves_length_phone_with_dashes(self, cz_engine):
        text = "Zavolejte na +420-777-888-999"
        masked = cz_engine.mask(text)
        assert len(masked) == len(text)

    def test_mask_preserves_length_rodne_cislo_with_slash(self, cz_engine):
        text = "RČ: 800101/1238"
        masked = cz_engine.mask(text)
        assert len(masked) == len(text)

    def test_no_original_pii_in_mask_phone_spaces(self, cz_engine):
        text = "Tel: +420 777 888 999"
        result = cz_engine.detect(text)
        masked = cz_engine.mask(text)
        for finding in result.findings:
            original = text[finding.start:finding.end]
            assert original not in masked

    def test_no_original_pii_in_anonymize_phone_spaces(self, cz_engine):
        text = "Tel: +420 777 888 999"
        result = cz_engine.detect(text)
        anonymized = cz_engine.anonymize(text)
        for finding in result.findings:
            original = text[finding.start:finding.end]
            assert original not in anonymized

    def test_no_original_pii_in_redact_phone_spaces(self, cz_engine):
        text = "Tel: +420 777 888 999"
        result = cz_engine.detect(text)
        redacted = cz_engine.redact(text)
        for finding in result.findings:
            original = text[finding.start:finding.end]
            assert original not in redacted

    def test_no_original_pii_in_remove_phone_spaces(self, cz_engine):
        text = "Tel: +420 777 888 999"
        result = cz_engine.detect(text)
        removed = cz_engine.remove(text)
        for finding in result.findings:
            original = text[finding.start:finding.end]
            assert original not in removed

    def test_no_original_pii_in_mask_rodne_cislo_slash(self, cz_engine):
        text = "RČ: 800101/1238"
        result = cz_engine.detect(text)
        masked = cz_engine.mask(text)
        for finding in result.findings:
            original = text[finding.start:finding.end]
            assert original not in masked

    def test_redact_phone_shows_type_label(self, cz_engine):
        text = "Tel: +420 777 888 999"
        redacted = cz_engine.redact(text)
        assert "[PHONE]" in redacted

    def test_anonymize_phone_custom_replacement(self, cz_engine):
        text = "Tel: +420 777 888 999"
        anonymized = cz_engine.anonymize(text, replacement="<PII>")
        assert "<PII>" in anonymized
        assert "+420 777 888 999" not in anonymized


class TestCzechIdentifiers:
    """Verify all Czech PII types transform correctly."""

    def test_rodne_cislo_with_slash(self, guard):
        text = "RČ: 800101/1238"
        masked = guard.mask(text)
        assert len(masked) == len(text)
        assert "800101/1238" not in masked
        assert "8001011238" not in masked

    def test_rodne_cislo_without_slash(self, guard):
        text = "RČ: 8001011238"
        masked = guard.mask(text)
        assert len(masked) == len(text)
        assert "8001011238" not in masked

    def test_ico(self, guard):
        text = "IČO: 25596641"
        redacted = guard.redact(text)
        assert "[ICO]" in redacted
        assert "25596641" not in redacted

    def test_dic_with_prefix(self, guard):
        text = "DIČ: CZ25596641"
        redacted = guard.redact(text)
        assert "[DIC]" in redacted
        assert "CZ25596641" not in redacted

    def test_email_cz_domain(self, guard):
        text = "Email: jan@email.cz"
        redacted = guard.redact(text)
        assert "[EMAIL]" in redacted
        assert "jan@email.cz" not in redacted

    def test_phone_with_country_prefix_spaces(self, guard):
        text = "Tel: +420 777 888 999"
        masked = guard.mask(text)
        assert len(masked) == len(text)
        assert "+420 777 888 999" not in masked

    def test_phone_with_country_prefix_dashes(self, guard):
        text = "Zavolejte na +420-777-888-999"
        masked = guard.mask(text)
        assert len(masked) == len(text)

    def test_postal_code_with_space(self, guard):
        text = "PSČ: 110 00"
        redacted = guard.redact(text)
        assert "[POSTAL_CODE]" in redacted

    def test_multiple_czech_pii(self, guard):
        text = "Jan Novák, RČ: 800101/1238, IČO: 25596641"
        result = guard.detect(text)
        assert len(result.findings) >= 2
        masked = guard.mask(text)
        assert len(masked) == len(text)


class TestPolishIdentifiers:

    @pytest.fixture
    def pl_guard(self):
        return PrivacyGuard(regions=["pl"])

    def test_pesel(self, pl_guard):
        text = "PESEL: 44051401458"
        redacted = pl_guard.redact(text)
        assert "[PESEL]" in redacted

    def test_nip(self, pl_guard):
        text = "NIP: 5260250274"
        redacted = pl_guard.redact(text)
        assert "[NIP]" in redacted

    def test_polish_phone_with_prefix(self, pl_guard):
        text = "Numer telefonu: +48 123456789"
        masked = pl_guard.mask(text)
        assert len(masked) == len(text)
        assert "+48 123456789" not in masked


class TestGermanIdentifiers:

    @pytest.fixture
    def de_engine(self):
        engine = FastPII(priority=DEFAULT_PRIORITY)
        engine.register(GermanPack())
        return engine

    def test_steuer_id(self, de_engine):
        text = "Steuer-ID: 86095742719"
        redacted = de_engine.redact(text)
        assert "[STEUER_ID]" in redacted

    def test_ust_id_with_prefix(self, de_engine):
        text = "USt-IdNr: DE136695976"
        redacted = de_engine.redact(text)
        assert "[UST_ID]" in redacted

    def test_german_phone_with_spaces(self, de_engine):
        text = "Telefon: +49 170 1234567"
        masked = de_engine.mask(text)
        assert len(masked) == len(text)
        assert "+49 170 1234567" not in masked


class TestFrenchIdentifiers:

    @pytest.fixture
    def fr_engine(self):
        engine = FastPII(priority=DEFAULT_PRIORITY)
        engine.register(FrenchPack())
        return engine

    def test_siren(self, fr_engine):
        text = "SIREN: 552120222"
        redacted = fr_engine.redact(text)
        assert "[SIREN]" in redacted

    def test_siret(self, fr_engine):
        text = "SIRET: 73282932000074"
        redacted = fr_engine.redact(text)
        assert "[SIRET]" in redacted

    def test_french_phone_with_spaces(self, fr_engine):
        text = "Tél: +33 1 23 45 67 89"
        masked = fr_engine.mask(text)
        assert len(masked) == len(text)
        assert "+33 1 23 45 67 89" not in masked


class TestOverlappingEntities:

    def test_overlapping_rodne_cislo_and_ico(self, guard):
        text = "DIČ: CZ25596641 contains IČO: 25596641"
        result = guard.detect(text)
        dic_findings = [f for f in result.findings if f.type == "dic"]
        ico_findings = [f for f in result.findings if f.type == "ico"]
        assert len(dic_findings) >= 1
        assert len(ico_findings) >= 1

        masked = guard.mask(text)
        assert len(masked) == len(text)

    def test_adjacent_entities(self, guard):
        text = "Email: jan@email.cz, RČ: 8001011238"
        masked = guard.mask(text)
        assert len(masked) == len(text)
        assert "jan@email.cz" not in masked
        assert "8001011238" not in masked


class TestRepeatedEntities:

    def test_multiple_emails(self, guard):
        text = "Emails: jan@email.cz and info@firma.cz"
        anonymized = guard.anonymize(text)
        assert "jan@email.cz" not in anonymized
        assert "info@firma.cz" not in anonymized
        assert anonymized.count("[REDACTED]") == 2

    def test_multiple_rodne_cisla(self, guard):
        text = "RČ: 8001011238 a RČ: 8051011232"
        masked = guard.mask(text)
        assert "8001011238" not in masked
        assert "8051011232" not in masked
        assert len(masked) == len(text)


class TestUnicodeAndEdgeCases:

    def test_unicode_czech_names(self, guard):
        text = "Tomáš Müller napsal email"
        result = guard.detect(text)
        masked = guard.mask(text)
        assert len(masked) == len(text)

    def test_empty_string(self, guard):
        for method in [guard.anonymize, guard.redact, guard.mask, guard.remove]:
            assert method("") == ""

    def test_no_pii_returns_original(self, guard):
        text = "Hello world, nothing to see here"
        assert guard.anonymize(text) == text
        assert guard.redact(text) == text
        assert guard.mask(text) == text
        assert guard.remove(text) == text

    def test_fastpii_without_detectors_returns_original(self):
        engine = FastPII(priority={"email": 70})
        text = "Email: jan@email.cz"
        assert engine.anonymize(text) == text
        assert engine.redact(text) == text
        assert engine.mask(text) == text
        assert engine.remove(text) == text


class TestFastPIIMatchesPrivacyGuard:

    def test_anonymize_matches(self, cz_engine, guard):
        text = "Email: jan@email.cz, RČ: 8001011238"
        assert cz_engine.anonymize(text) == guard.anonymize(text)

    def test_redact_matches(self, cz_engine, guard):
        text = "Email: jan@email.cz, RČ: 8001011238"
        assert cz_engine.redact(text) == guard.redact(text)

    def test_mask_matches(self, cz_engine, guard):
        text = "Email: jan@email.cz, RČ: 8001011238"
        assert cz_engine.mask(text) == guard.mask(text)

    def test_remove_matches(self, cz_engine, guard):
        text = "Email: jan@email.cz, RČ: 8001011238"
        assert cz_engine.remove(text) == guard.remove(text)


class TestTransformationEngineCustomStrategy:

    def test_custom_anonymize_strategy(self, cz_engine):
        text = "Email: jan@email.cz"
        result = cz_engine.detect(text)
        custom = AnonymizeStrategy(replacement="<PII>")
        output = TransformationEngine.apply(result, custom)
        assert "<PII>" in output
        assert "jan@email.cz" not in output

    def test_custom_strategy_class(self, cz_engine):
        class HashStrategy:
            def replace(self, finding, text):
                return f"{{hash:{finding.type}}}"

        text = "Email: jan@email.cz"
        result = cz_engine.detect(text)
        output = TransformationEngine.apply(result, HashStrategy())
        assert "{hash:email}" in output
        assert "jan@email.cz" not in output

    def test_strategy_protocol_instance_check(self):
        assert isinstance(AnonymizeStrategy(), AnonymizeStrategy)
        assert isinstance(RedactStrategy(), RedactStrategy)
        assert isinstance(MaskStrategy(), MaskStrategy)
        assert isinstance(RemoveStrategy(), RemoveStrategy)

    def test_apply_with_empty_findings(self, cz_engine):
        result = cz_engine.detect("Hello world")
        output = TransformationEngine.apply(result, RedactStrategy())
        assert output == "Hello world"

    def test_apply_with_single_finding(self, cz_engine):
        text = "IČO: 25596641"
        result = cz_engine.detect(text)
        output = TransformationEngine.apply(result, RedactStrategy())
        assert "[ICO]" in output
        assert "25596641" not in output

    def test_apply_with_multiple_findings(self, cz_engine):
        text = "Email: jan@email.cz, RČ: 8001011238"
        result = cz_engine.detect(text)
        output = TransformationEngine.apply(result, AnonymizeStrategy(replacement="XXX"))
        assert output.count("XXX") >= 2
        assert "jan@email.cz" not in output
        assert "8001011238" not in output


class TestMaskLengthInvariant:
    """mask() must always preserve original text length — the core bug fix."""

    @pytest.mark.parametrize("text", [
        "Tel: +420 777 888 999",
        "RČ: 800101/1238",
        "RČ: 8001011238",
        "PSČ: 110 00",
        "PSČ: 11000",
        "IČO: 25596641",
        "Email: jan@email.cz",
        "Jan Novák napsal email na petr@email.cz",
    ])
    def test_mask_preserves_length(self, guard, text):
        masked = guard.mask(text)
        assert len(masked) == len(text), f"mask changed length for: {text!r}"

    @pytest.mark.parametrize("text", [
        "Telefon: +420 777 888 999",
        "Zavolejte na +420-777-888-999",
        "Mobil: 777888999",
    ])
    def test_mask_preserves_length_phone_variants(self, guard, text):
        masked = guard.mask(text)
        assert len(masked) == len(text), f"mask changed length for: {text!r}"

    @pytest.mark.parametrize("text", [
        "Telefon: +49 170 1234567",
        "Telefon: +49-170-1234567",
    ])
    def test_mask_preserves_length_german_phone(self, text):
        engine = FastPII(priority=DEFAULT_PRIORITY)
        engine.register(GermanPack())
        masked = engine.mask(text)
        assert len(masked) == len(text), f"mask changed length for: {text!r}"

    @pytest.mark.parametrize("text", [
        "Tél: +33 1 23 45 67 89",
        "Appelez: +33-1-23-45-67-89",
    ])
    def test_mask_preserves_length_french_phone(self, text):
        engine = FastPII(priority=DEFAULT_PRIORITY)
        engine.register(FrenchPack())
        masked = engine.mask(text)
        assert len(masked) == len(text), f"mask changed length for: {text!r}"

    def test_mask_no_pii_preserves_length(self, guard):
        text = "Hello world, nothing here"
        assert len(guard.mask(text)) == len(text)

    def test_mask_empty_string_preserves_length(self, guard):
        assert len(guard.mask("")) == 0