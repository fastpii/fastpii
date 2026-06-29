import pytest

from fastpii import FastPII, DEFAULT_PRIORITY, DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST
from fastpii.countries import get_country_pack
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.fr.pack import FrenchPack
from fastpii.detectors.fr import (
    FrenchAddressDetector,
    FrenchPhoneDetector,
    FrenchPostalCodeDetector,
    INSEEDetector,
    SIRENDetector,
    SIRETDetector,
)
from fastpii.patterns.registry import PatternRegistry


@pytest.fixture
def engine():
    guard = FastPII(
        priority=DEFAULT_PRIORITY,
        confidence_scorer=ConfidenceScorer(
            base_scores=DEFAULT_CONFIDENCE_SCORES,
            context_boost=DEFAULT_CONTEXT_BOOST,
        ),
    )
    guard.register(FrenchPack())
    return guard


def make_fr_registry() -> PatternRegistry:
    registry = PatternRegistry()
    registry.load_patterns("fr")
    return registry


class TestSIRENDetector:
    def test_detector_creation(self):
        detector = SIRENDetector(registry=make_fr_registry())

        assert detector.name == "siren"
        assert detector.region == "fr"
        assert "SIREN" in detector.description

    def test_detect_valid(self):
        detector = SIRENDetector(registry=make_fr_registry())
        text = "552120222"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "siren"
        assert findings[0].value == "552120222"
        assert findings[0].region == "fr"
        assert findings[0].confidence == 0.75
        assert findings[0].metadata["checksum_valid"] is True

    def test_detect_with_context(self):
        detector = SIRENDetector(registry=make_fr_registry())
        text = "SIREN: 552120222"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "552120222"
        assert findings[0].confidence == 0.90

    def test_validate_valid(self):
        detector = SIRENDetector(registry=make_fr_registry())

        valid = detector.validate("552120222")

        assert valid is True

    def test_validate_invalid(self):
        detector = SIRENDetector(registry=make_fr_registry())

        valid = detector.validate("552120223")

        assert valid is False


class TestSIRETDetector:
    def test_detector_creation(self):
        detector = SIRETDetector(registry=make_fr_registry())

        assert detector.name == "siret"
        assert detector.region == "fr"
        assert "SIRET" in detector.description

    def test_detect_valid(self):
        detector = SIRETDetector(registry=make_fr_registry())
        text = "SIRET: 73282932000074"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "siret"
        assert findings[0].value == "73282932000074"
        assert findings[0].region == "fr"
        assert findings[0].confidence == 0.95
        assert findings[0].metadata["checksum_valid"] is True
        assert findings[0].metadata["siren"] == "732829320"

    def test_validate_valid(self):
        detector = SIRETDetector(registry=make_fr_registry())

        valid = detector.validate("73282932000074")

        assert valid is True

    def test_validate_invalid(self):
        detector = SIRETDetector(registry=make_fr_registry())

        valid = detector.validate("73282932000075")

        assert valid is False


class TestINSEEDetector:
    def test_detector_creation(self):
        detector = INSEEDetector(registry=make_fr_registry())

        assert detector.name == "insee"
        assert detector.region == "fr"
        assert "INSEE" in detector.description

    def test_detect_valid(self):
        detector = INSEEDetector(registry=make_fr_registry())
        text = "NIR: 185047511600341"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "insee"
        assert findings[0].value == "185047511600341"
        assert findings[0].region == "fr"
        assert findings[0].confidence == 0.95

    def test_detect_corsica(self):
        detector = INSEEDetector(registry=make_fr_registry())
        text = "INSEE: 180012A00100161"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "180012A00100161"
        assert findings[0].metadata["department"] == "Corse-du-Sud"
        assert findings[0].metadata["checksum_valid"] is True

    def test_validate_valid(self):
        detector = INSEEDetector(registry=make_fr_registry())

        valid = detector.validate("185047511600341")

        assert valid is True

    def test_validate_invalid(self):
        detector = INSEEDetector(registry=make_fr_registry())

        valid = detector.validate("185047511600342")

        assert valid is False

    def test_validate_corsica(self):
        detector = INSEEDetector(registry=make_fr_registry())

        valid = detector.validate("180012A00100161")

        assert valid is True

    def test_extract_metadata(self):
        detector = INSEEDetector(registry=make_fr_registry())
        text = "NIR: 285047511600388"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].metadata["sex"] == "female"
        assert findings[0].metadata["birth_year"] == 85
        assert findings[0].metadata["department"] == "75"
        assert findings[0].metadata["checksum_valid"] is True


class TestFrenchPostalCodeDetector:
    def test_detector_creation(self):
        detector = FrenchPostalCodeDetector(registry=make_fr_registry())

        assert detector.name == "postal_code"
        assert detector.region == "fr"
        assert "postal code" in detector.description.lower()

    def test_detect_valid(self):
        detector = FrenchPostalCodeDetector(registry=make_fr_registry())
        text = "Code postal: 75001"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "postal_code"
        assert findings[0].value == "75001"
        assert findings[0].region == "fr"
        assert findings[0].confidence == 0.90
        assert findings[0].metadata["department"] == "75"
        assert detector.validate("75001") is True
        assert detector.validate("13001") is True
        assert detector.validate("00000") is False


class TestFrenchPhoneDetector:
    def test_detector_creation(self):
        detector = FrenchPhoneDetector(registry=make_fr_registry())

        assert detector.name == "phone"
        assert detector.region == "fr"
        assert "French phone number" in detector.description

    def test_detect_with_prefix(self):
        detector = FrenchPhoneDetector(registry=make_fr_registry())
        text = "Appelez-moi au +33 6 12 34 56 78"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "phone"
        assert findings[0].value == "33612345678"
        assert findings[0].region == "fr"
        assert findings[0].metadata["phone_type"] == "mobile"
        assert detector.validate("+33 6 12 34 56 78") is True
        assert detector.validate("123") is False


class TestFrenchAddressDetector:
    def test_detector_creation(self):
        detector = FrenchAddressDetector(registry=make_fr_registry())

        assert detector.name == "address"
        assert detector.region == "fr"
        assert "French address" in detector.description

    def test_detect_full_address(self):
        detector = FrenchAddressDetector(registry=make_fr_registry())
        text = "Adresse: 15 Rue de Rivoli, 75001 Paris"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "address"
        assert findings[0].value == "15 Rue de Rivoli, 75001 Paris"
        assert findings[0].region == "fr"
        assert findings[0].confidence == 1.0
        assert findings[0].metadata["house_number"] == "15"
        assert findings[0].metadata["street"] == "Rue de Rivoli"
        assert findings[0].metadata["postal_code"] == "75001"
        assert findings[0].metadata["city"] == "Paris"
        assert detector.validate("15 Rue de Rivoli, 75001 Paris") is True
        assert detector.validate("123") is False


class TestFrenchPack:
    def test_code(self):
        pack = FrenchPack()

        assert pack.code == "fr"
        assert get_country_pack("fr") == FrenchPack

    def test_name(self):
        pack = FrenchPack()

        assert pack.name == "France"

    def test_metadata(self):
        pack = FrenchPack()
        metadata = pack.metadata

        assert metadata.code == "fr"
        assert metadata.name == "France"
        assert metadata.official_name == "République française"
        assert metadata.language_codes == ("fr", "fr-FR")
        assert metadata.iso_3166_alpha2 == "FR"
        assert metadata.iso_3166_alpha3 == "FRA"
        assert metadata.currency_code == "EUR"

    def test_detector_count(self):
        pack = FrenchPack()
        detectors = pack.detectors

        assert len(detectors) == 6
        assert {detector.name for detector in detectors} == {
            "siren",
            "siret",
            "insee",
            "postal_code",
            "phone",
            "address",
        }

    def test_entities(self):
        pack = FrenchPack()
        entities = pack.entities

        assert len(entities) == 6
        assert {entity.entity_type for entity in entities} == {
            "siren",
            "siret",
            "insee",
            "postal_code",
            "phone",
            "address",
        }
        assert all(entity.region == "fr" for entity in entities)


class TestFranceIntegration:
    def test_detect(self, engine):
        text = (
            "SIREN: 552120222, SIRET: 73282932000074, NIR: 185047511600341, "
            "code postal: 13001, téléphone: +33 6 12 34 56 78, "
            "adresse: 15 Rue de Rivoli, 75001 Paris"
        )

        result = engine.detect(text)

        assert len(result.findings) >= 6
        assert result.text == text
        assert result.processing_time_ms >= 0
        assert {finding.type for finding in result.findings} >= {
            "siren",
            "siret",
            "insee",
            "postal_code",
            "phone",
            "address",
        }

    def test_validate(self, engine):

        siren_result = engine.validate("552120222", "siren")
        siret_result = engine.validate("73282932000074", "siret")
        insee_result = engine.validate("180012A00100161", "insee")

        assert siren_result.is_valid is True
        assert siren_result.metadata["checksum_valid"] is True
        assert siret_result.is_valid is True
        assert siret_result.metadata["siren"] == "732829320"
        assert insee_result.is_valid is True
        assert insee_result.metadata["department"] == "Corse-du-Sud"

    def test_anonymize(self, engine):
        text = "SIREN: 552120222, téléphone: +33 6 12 34 56 78"

        anonymized = engine.anonymize(text)

        assert "552120222" not in anonymized
        assert "+33 6 12 34 56 78" not in anonymized
        assert anonymized.count("[REDACTED]") == 2

    def test_redact(self, engine):
        text = "SIREN: 552120222, NIR: 185047511600341"

        redacted = engine.redact(text)

        assert "552120222" not in redacted
        assert "185047511600341" not in redacted
        assert "[SIREN]" in redacted
        assert "[INSEE]" in redacted

    def test_mask(self, engine):
        text = "SIRET: 73282932000074, code postal: 75001"

        masked = engine.mask(text)

        assert "73282932000074" not in masked
        assert "75001" not in masked
        assert "**************" in masked
        assert "*****" in masked
