import pytest

from fastpii import (
    DEFAULT_CONFIDENCE_SCORES,
    DEFAULT_CONTEXT_BOOST,
    DEFAULT_PRIORITY,
    FastPII,
)
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.fr.pack import FrenchPack
from fastpii.countries.fr.validators import (
    extract_insee_metadata,
    is_valid_insee,
    is_valid_siren,
    is_valid_siret,
)


@pytest.fixture
def fr_engine():
    engine = FastPII(
        priority=DEFAULT_PRIORITY,
        confidence_scorer=ConfidenceScorer(
            base_scores=DEFAULT_CONFIDENCE_SCORES,
            context_boost=DEFAULT_CONTEXT_BOOST,
        ),
    )
    engine.register(FrenchPack())
    return engine


def detect_type(engine: FastPII, text: str, entity_type: str):
    return [finding for finding in engine.detect(text).findings if finding.type == entity_type]


def calculate_metrics(engine: FastPII, entity_type: str, positives: list[str], negatives: list[str]) -> tuple[float, float]:
    true_positives = sum(1 for text in positives if detect_type(engine, text, entity_type))
    false_negatives = len(positives) - true_positives
    false_positives = sum(1 for text in negatives if detect_type(engine, text, entity_type))

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 1.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) else 1.0
    return precision, recall


class TestSIRENBenchmark:
    def test_valid_and_invalid_luhn(self, fr_engine: FastPII):
        assert is_valid_siren("552120222") is True
        assert is_valid_siren("732829320") is True
        assert is_valid_siren("552120223") is False

        assert detect_type(fr_engine, "SIREN: 552120222", "siren")
        assert detect_type(fr_engine, "numéro SIREN: 732829320", "siren")
        assert not detect_type(fr_engine, "SIREN: 552120223", "siren")

    def test_format_validation(self, fr_engine: FastPII):
        assert is_valid_siren("12345678") is False
        assert not detect_type(fr_engine, "SIREN: 12345678", "siren")
        assert not detect_type(fr_engine, "SIREN: 1234567890", "siren")

    def test_context_gating(self, fr_engine: FastPII):
        with_context = detect_type(fr_engine, "SIREN: 552120222", "siren")
        without_context = detect_type(fr_engine, "552120222", "siren")

        assert with_context and without_context
        assert with_context[0].confidence > without_context[0].confidence


class TestSIRETBenchmark:
    def test_valid_invalid_and_embedded_siren(self, fr_engine: FastPII):
        assert is_valid_siret("73282932000074") is True
        assert is_valid_siret("55212022200005") is True
        assert is_valid_siret("73282932000075") is False

        findings = detect_type(fr_engine, "SIRET: 73282932000074", "siret")
        assert findings
        assert findings[0].metadata["checksum_valid"] is True
        assert findings[0].metadata["siren"] == "732829320"

        second = detect_type(fr_engine, "numéro SIRET: 55212022200005", "siret")
        assert second
        assert second[0].metadata["siren"] == "552120222"
        assert not detect_type(fr_engine, "SIRET: 73282932000075", "siret")

    def test_format_validation(self, fr_engine: FastPII):
        assert not detect_type(fr_engine, "SIRET: 7328293200007", "siret")
        assert not detect_type(fr_engine, "SIRET: 732829320000740", "siret")

    def test_context_gating(self, fr_engine: FastPII):
        with_context = detect_type(fr_engine, "SIRET: 73282932000074", "siret")
        without_context = detect_type(fr_engine, "73282932000074", "siret")

        assert with_context and without_context
        assert with_context[0].confidence > without_context[0].confidence


class TestINSEEBenchmark:
    def test_valid_invalid_mod97(self, fr_engine: FastPII):
        assert is_valid_insee("184127511500156") is True
        assert is_valid_insee("285017504204584") is True
        assert is_valid_insee("185077504204878") is False

        assert detect_type(fr_engine, "INSEE: 184127511500156", "insee")
        assert detect_type(fr_engine, "NIR: 285017504204584", "insee")
        assert not detect_type(fr_engine, "INSEE: 185077504204878", "insee")

    def test_format_validation(self, fr_engine: FastPII):
        assert not detect_type(fr_engine, "INSEE: 18412751150015", "insee")
        assert not detect_type(fr_engine, "INSEE: 384127511500156", "insee")

    def test_context_gating(self, fr_engine: FastPII):
        with_context = detect_type(fr_engine, "INSEE: 184127511500156", "insee")
        without_context = detect_type(fr_engine, "184127511500156", "insee")

        assert with_context
        assert is_valid_insee("184127511500156") is True
        assert len(without_context) <= 1
        if without_context:
            assert without_context[0].confidence < with_context[0].confidence
            assert without_context[0].confidence <= 0.85

    def test_corsica_2a_and_2b(self, fr_engine: FastPII):
        corsica_2a = "180012A00100161"
        corsica_2b = "180012B00100188"

        assert is_valid_insee(corsica_2a) is True
        assert is_valid_insee(corsica_2b) is True

        findings_2a = detect_type(fr_engine, f"NIR: {corsica_2a}", "insee")
        findings_2b = detect_type(fr_engine, f"INSEE: {corsica_2b}", "insee")

        assert findings_2a
        assert findings_2b
        assert findings_2a[0].metadata["department"] == "Corse-du-Sud"
        assert findings_2b[0].metadata["department"] == "Haute-Corse"
        assert extract_insee_metadata(corsica_2a)["checksum_valid"] is True
        assert extract_insee_metadata(corsica_2b)["checksum_valid"] is True


class TestFRPostalCodeBenchmark:
    def test_valid_invalid_five_digit_codes(self, fr_engine: FastPII):
        assert detect_type(fr_engine, "Code postal: 75001", "postal_code")
        assert detect_type(fr_engine, "69001 Lyon", "postal_code")
        assert detect_type(fr_engine, "13001 Marseille", "postal_code")
        assert fr_engine.validate("00000", "postal_code").is_valid is False
        assert not detect_type(fr_engine, "99999 Marseille", "postal_code")

    def test_context_gating(self, fr_engine: FastPII):
        assert detect_type(fr_engine, "Code postal: 75001", "postal_code")
        assert detect_type(fr_engine, "75001 Paris", "postal_code")
        assert not detect_type(fr_engine, "75001", "postal_code")


class TestFRPhoneBenchmark:
    def test_mobile_and_landline_formats(self, fr_engine: FastPII):
        mobile = detect_type(fr_engine, "+33 6 12 34 56 78", "phone")
        landline = detect_type(fr_engine, "téléphone: +33 1 23 45 67 89", "phone")
        domestic = detect_type(fr_engine, "portable: 06 12 34 56 78", "phone")

        assert mobile
        assert landline
        assert domestic
        assert mobile[0].metadata["phone_type"] == "mobile"
        assert landline[0].metadata["phone_type"] == "landline"
        assert domestic[0].value == "33612345678"

    def test_context_gating(self, fr_engine: FastPII):
        assert detect_type(fr_engine, "portable: 06 12 34 56 78", "phone")
        assert detect_type(fr_engine, "+33 6 12 34 56 78", "phone")
        assert not detect_type(fr_engine, "06 12 34 56 78", "phone")


class TestFRAddressBenchmark:
    def test_address_patterns(self, fr_engine: FastPII):
        full = detect_type(fr_engine, "Adresse: 15 Rue de Rivoli, 75001 Paris", "address")
        simple = detect_type(fr_engine, "Livraison au 8 Avenue de l'Opéra.", "address")

        assert full
        assert simple
        assert full[0].metadata["postal_code"] == "75001"
        assert full[0].metadata["city"] == "Paris"
        assert simple[0].metadata["street"] == "Avenue de l'Opéra"

    def test_overlap_with_postal_code(self, fr_engine: FastPII):
        result = fr_engine.detect("Adresse: 15 Rue de Rivoli, 75001 Paris")
        types = [finding.type for finding in result.findings]

        assert "address" in types
        assert "postal_code" not in types

    def test_context_gating(self, fr_engine: FastPII):
        assert detect_type(fr_engine, "15 Rue de Rivoli, 75001 Paris", "address")
        assert not detect_type(fr_engine, "Rue de Rivoli, 75001 Paris", "address")
        assert not detect_type(fr_engine, "15 Rivoli 75001 Paris", "address")


class TestFRFalsePositiveTraps:
    @pytest.mark.parametrize(
        ("entity_type", "text"),
        [
            ("siren", "Commande #552120223 validée"),
            ("siret", "Référence lot 73282932000075 à vérifier"),
            ("insee", "Ticket interne 185077504204878 archivé"),
            ("postal_code", "Le score 75001 dépasse l'objectif"),
            ("phone", "La suite 06 12 34 56 78 est un exemple sans contexte"),
            ("address", "Rue de Rivoli est magnifique au printemps"),
        ],
    )
    def test_similar_looking_values_are_rejected(self, fr_engine: FastPII, entity_type: str, text: str):
        assert not detect_type(fr_engine, text, entity_type)


class TestFRDetectorAccuracy:
    @pytest.mark.parametrize(
        ("entity_type", "positives", "negatives"),
        [
            (
                "siren",
                [
                    "SIREN: 552120222",
                    "numéro SIREN: 732829320",
                    "company ID 552120222",
                    "732829320",
                ],
                [
                    "SIREN: 552120223",
                    "Identifiant: 12345678",
                    "SIRET: 73282932000074",
                ],
            ),
            (
                "siret",
                [
                    "SIRET: 73282932000074",
                    "numéro SIRET: 55212022200005",
                    "73282932000074",
                ],
                [
                    "SIRET: 73282932000075",
                    "SIRET: 7328293200007",
                    "SIREN: 552120222",
                ],
            ),
            (
                "insee",
                [
                    "INSEE: 184127511500156",
                    "NIR: 285017504204584",
                    "numéro de sécurité sociale: 180012A00100161",
                ],
                [
                    "INSEE: 185077504204878",
                    "NIR: 18412751150015",
                    "numéro social: 384127511500156",
                ],
            ),
            (
                "postal_code",
                [
                    "Code postal: 75001",
                    "69001 Lyon",
                    "13001 Marseille",
                ],
                [
                    "75001",
                    "00000",
                    "96000 Marseille",
                    "99999 Marseille",
                ],
            ),
            (
                "phone",
                [
                    "+33 6 12 34 56 78",
                    "téléphone: +33 1 23 45 67 89",
                    "portable: 06 12 34 56 78",
                    "contact: 01 23 45 67 89",
                ],
                [
                    "06 12 34 56 78",
                    "01 23 45 67 89",
                    "Référence 33612345678",
                ],
            ),
            (
                "address",
                [
                    "15 Rue de Rivoli, 75001 Paris",
                    "8 Avenue de l'Opéra",
                    "20 Boulevard Saint-Germain, 75005 Paris",
                ],
                [
                    "Rue de Rivoli, 75001 Paris",
                    "75001 Paris",
                    "Boulevard Saint-Germain",
                ],
            ),
        ],
    )
    def test_precision_and_recall(self, fr_engine: FastPII, entity_type: str, positives: list[str], negatives: list[str]):
        precision, recall = calculate_metrics(fr_engine, entity_type, positives, negatives)

        assert precision >= 0.90, f"{entity_type} precision below target: {precision:.2%}"
        assert recall >= 0.80, f"{entity_type} recall below target: {recall:.2%}"
