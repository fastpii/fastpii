from typing import TypeAlias

import pytest

from fastpii import FastPII, DEFAULT_PRIORITY, DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.pl.pack import PolishPack
from fastpii.countries.pl.validators import is_valid_nip, is_valid_pesel, is_valid_regon
from fastpii.models import Finding


VALID_PESELS = {
    "44051401458": {"birth_date": "1944-05-14", "gender": "male"},
    "72010102823": {"birth_date": "1972-01-01", "gender": "female"},
}
INVALID_PESELS = ["44051401459", "72010102824"]

VALID_NIPS = ["5260250274"]
INVALID_NIPS = ["5260250275", "1234567890"]

VALID_REGONS = {
    "123456785": "9-digit",
    "12345678512347": "14-digit",
}
INVALID_REGONS = ["123456789", "12345678512348"]

PositiveCase: TypeAlias = tuple[str, str]
PositiveCases: TypeAlias = list[PositiveCase]
NegativeCases: TypeAlias = list[str]


@pytest.fixture
def pl_engine() -> FastPII:
    engine = FastPII(
        priority=DEFAULT_PRIORITY,
        confidence_scorer=ConfidenceScorer(
            base_scores=DEFAULT_CONFIDENCE_SCORES,
            context_boost=DEFAULT_CONTEXT_BOOST,
        ),
    )
    engine.register(PolishPack())
    return engine


def _detector_findings(pl_engine: FastPII, detector_name: str, text: str) -> list[Finding]:
    return pl_engine.detect(text, detector_names=[detector_name]).findings


def _single_finding(pl_engine: FastPII, detector_name: str, text: str) -> Finding:
    findings = _detector_findings(pl_engine, detector_name, text)
    assert len(findings) == 1
    return findings[0]


def _measure_precision_recall(
    pl_engine: FastPII,
    detector_name: str,
    positives: PositiveCases,
    negatives: NegativeCases,
) -> tuple[float, float]:
    true_positives = 0
    false_negatives = 0

    for text, expected_value in positives:
        findings = _detector_findings(pl_engine, detector_name, text)
        matched = any(f.type == detector_name and f.value == expected_value for f in findings)
        if matched:
            true_positives += 1
        else:
            false_negatives += 1

    false_positives = sum(
        1
        for text in negatives
        if any(f.type == detector_name for f in _detector_findings(pl_engine, detector_name, text))
    )

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 1.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) else 1.0
    return precision, recall


class TestPESELBenchmark:
    def test_validator_approved_reference_samples(self):
        assert all(is_valid_pesel(value) for value in VALID_PESELS)
        assert all(not is_valid_pesel(value) for value in INVALID_PESELS)

    @pytest.mark.parametrize("value", list(VALID_PESELS))
    def test_valid_mod10_checksum_detected(self, pl_engine: FastPII, value: str) -> None:
        assert is_valid_pesel(value) is True

        finding = _single_finding(pl_engine, "pesel", f"PESEL: {value}")

        assert finding.type == "pesel"
        assert finding.value == value
        assert finding.metadata["checksum_valid"] is True

    @pytest.mark.parametrize("value", INVALID_PESELS)
    def test_invalid_mod10_checksum_rejected(self, pl_engine: FastPII, value: str) -> None:
        assert is_valid_pesel(value) is False
        assert _detector_findings(pl_engine, "pesel", f"PESEL: {value}") == []

    def test_date_and_gender_extraction(self, pl_engine: FastPII) -> None:
        for value, expected in VALID_PESELS.items():
            finding = _single_finding(pl_engine, "pesel", f"PESEL: {value}")

            assert finding.metadata["birth_date"] == expected["birth_date"]
            assert finding.metadata["gender"] == expected["gender"]

    def test_context_gating_prefers_contextual_matches(self, pl_engine: FastPII) -> None:
        with_context = _single_finding(pl_engine, "pesel", "PESEL: 44051401458")
        without_context = _single_finding(pl_engine, "pesel", "44051401458")

        assert with_context.confidence > without_context.confidence


class TestNIPBenchmark:
    def test_validator_approved_reference_samples(self):
        assert all(is_valid_nip(value) for value in VALID_NIPS)
        assert all(not is_valid_nip(value) for value in INVALID_NIPS)

    def test_valid_weighted_mod11_detected(self, pl_engine: FastPII) -> None:
        value = VALID_NIPS[0]
        assert is_valid_nip(value) is True

        finding = _single_finding(pl_engine, "nip", f"NIP: {value}")

        assert finding.type == "nip"
        assert finding.value == value
        assert finding.metadata["checksum_valid"] is True

    @pytest.mark.parametrize("value", INVALID_NIPS)
    def test_invalid_weighted_mod11_rejected(self, pl_engine: FastPII, value: str) -> None:
        assert is_valid_nip(value) is False
        assert _detector_findings(pl_engine, "nip", f"NIP: {value}") == []

    @pytest.mark.parametrize("formatted", ["526 025 02 74", "526-025-02-74"])
    def test_validator_accepts_supported_formats(self, pl_engine: FastPII, formatted: str) -> None:
        assert pl_engine.validate(formatted, "nip").is_valid is True

    def test_context_gating_prefers_contextual_matches(self, pl_engine: FastPII) -> None:
        with_context = _single_finding(pl_engine, "nip", "NIP: 5260250274")
        without_context = _single_finding(pl_engine, "nip", "5260250274")

        assert with_context.confidence > without_context.confidence


class TestREGONBenchmark:
    @pytest.mark.parametrize("value", list(VALID_REGONS))
    def test_validator_approved_reference_samples(self, value: str) -> None:
        assert is_valid_regon(value) is True

    @pytest.mark.parametrize("value", INVALID_REGONS)
    def test_invalid_reference_samples_fail_validation(self, value: str) -> None:
        assert is_valid_regon(value) is False

    @pytest.mark.parametrize("value, expected_format", list(VALID_REGONS.items()))
    def test_valid_weighted_mod11_variants_detected(
        self,
        pl_engine: FastPII,
        value: str,
        expected_format: str,
    ) -> None:
        finding = _single_finding(pl_engine, "regon", f"REGON: {value}")

        assert finding.value == value
        assert finding.metadata["checksum_valid"] is True
        assert finding.metadata["format"] == expected_format

    @pytest.mark.parametrize("value", INVALID_REGONS)
    def test_invalid_weighted_mod11_variants_rejected(self, pl_engine: FastPII, value: str) -> None:
        assert _detector_findings(pl_engine, "regon", f"REGON: {value}") == []

    def test_context_gating_prefers_contextual_matches(self, pl_engine: FastPII) -> None:
        with_context = _single_finding(pl_engine, "regon", "REGON: 123456785")
        without_context = _single_finding(pl_engine, "regon", "123456785")

        assert with_context.confidence > without_context.confidence


class TestPLPostalCodeBenchmark:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("kod pocztowy: 00-001", "00-001"),
            ("30 001 Kraków", "30-001"),
            ("50-001", "50-001"),
        ],
    )
    def test_xx_xxx_format_detected(self, pl_engine: FastPII, text: str, expected: str) -> None:
        finding = _single_finding(pl_engine, "postal_code", text)

        assert finding.type == "postal_code"
        assert finding.value == expected

    def test_context_gating_rejects_plain_digits_without_label_or_city(self, pl_engine: FastPII) -> None:
        assert _detector_findings(pl_engine, "postal_code", "00001") == []

    def test_context_label_scores_higher_than_standalone_hyphenated_code(self, pl_engine: FastPII) -> None:
        with_context = _single_finding(pl_engine, "postal_code", "kod pocztowy: 00-001")
        standalone = _single_finding(pl_engine, "postal_code", "00-001")

        assert with_context.confidence > standalone.confidence


class TestPLPhoneBenchmark:
    @pytest.mark.parametrize(
        ("text", "expected", "phone_type"),
        [
            ("+48 512 345 678", "48512345678", "mobile"),
            ("Telefon: 512 345 678", "48512345678", "mobile"),
            ("tel 22 123 45 67", "48221234567", "landline"),
        ],
    )
    def test_plus48_and_domestic_formats_detected(
        self,
        pl_engine: FastPII,
        text: str,
        expected: str,
        phone_type: str,
    ) -> None:
        finding = _single_finding(pl_engine, "phone", text)

        assert finding.type == "phone"
        assert finding.value == expected
        assert finding.metadata["phone_type"] == phone_type

    @pytest.mark.parametrize("text", ["512 345 678", "22 123 45 67"])
    def test_context_gating_rejects_domestic_numbers_without_context(self, pl_engine: FastPII, text: str) -> None:
        assert _detector_findings(pl_engine, "phone", text) == []


class TestPLAddressBenchmark:
    def test_street_number_and_city_detected(self, pl_engine: FastPII) -> None:
        finding = _single_finding(pl_engine, "address", "Adres: Długa 15 Warszawa")

        assert finding.type == "address"
        assert finding.value == "Długa 15 Warszawa"
        assert finding.metadata["street"] == "Długa"
        assert finding.metadata["house_number"] == "15"
        assert finding.metadata["score"] == 100

    def test_simple_address_detects_with_lower_confidence(self, pl_engine: FastPII) -> None:
        simple = _single_finding(pl_engine, "address", "Marszałkowska 10")
        rich = _single_finding(pl_engine, "address", "Marszałkowska 10 Warszawa")

        assert simple.value == "Marszałkowska 10"
        assert rich.confidence > simple.confidence

    def test_address_and_postal_code_can_coexist_in_full_engine_results(self, pl_engine: FastPII) -> None:
        result = pl_engine.detect("ul. Długa 15, 00-001 Warszawa")

        assert {finding.type for finding in result.findings} == {"address", "postal_code"}
        address = next(finding for finding in result.findings if finding.type == "address")
        postal = next(finding for finding in result.findings if finding.type == "postal_code")

        assert address.metadata["street"] == "Długa"
        assert address.metadata["house_number"] == "15"
        assert postal.value == "00-001"


class TestPLFalsePositiveTraps:
    @pytest.mark.parametrize(
        ("detector_name", "text"),
        [
            ("pesel", "PESEL: 44051401459"),
            ("nip", "NIP: 5260250275"),
            ("regon", "REGON: 123456789"),
            ("postal_code", "Ref 50 001"),
            ("phone", "512 345 678"),
            ("address", "sekcja 15"),
        ],
    )
    def test_similar_looking_values_do_not_trigger_detection(
        self,
        pl_engine: FastPII,
        detector_name: str,
        text: str,
    ) -> None:
        assert _detector_findings(pl_engine, detector_name, text) == []


class TestPLDetectorAccuracy:
    @pytest.mark.parametrize(
        ("detector_name", "positives", "negatives"),
        [
            (
                "pesel",
                [
                    ("PESEL: 44051401458", "44051401458"),
                    ("44051401458", "44051401458"),
                    ("numer PESEL 72010102823", "72010102823"),
                ],
                ["PESEL: 44051401459", "72010102824", "440514/01458"],
            ),
            (
                "nip",
                [
                    ("NIP: 5260250274", "5260250274"),
                    ("5260250274", "5260250274"),
                    ("VAT 5260250274", "5260250274"),
                ],
                ["NIP: 5260250275", "1234567890", "526-025-02-75"],
            ),
            (
                "regon",
                [
                    ("REGON: 123456785", "123456785"),
                    ("123456785", "123456785"),
                    ("REGON: 12345678512347", "12345678512347"),
                ],
                ["REGON: 123456789", "12345678512348", "111111111"],
            ),
            (
                "postal_code",
                [
                    ("kod pocztowy: 00-001", "00-001"),
                    ("30 001 Kraków", "30-001"),
                    ("50-001", "50-001"),
                ],
                ["00001", "Ref 50 001", "12345"],
            ),
            (
                "phone",
                [
                    ("+48 512 345 678", "48512345678"),
                    ("Telefon: 512 345 678", "48512345678"),
                    ("tel 22 123 45 67", "48221234567"),
                ],
                ["512 345 678", "22 123 45 67", "123-456"],
            ),
            (
                "address",
                [
                    ("Długa 15 Warszawa", "Długa 15 Warszawa"),
                    ("Marszałkowska 10", "Marszałkowska 10"),
                    ("Kwiatowa 7 Kraków", "Kwiatowa 7 Kraków"),
                ],
                ["sekcja 15", "konto 12345", "zamowienie 2024/15"],
            ),
        ],
    )
    def test_precision_and_recall_thresholds(
        self,
        pl_engine: FastPII,
        detector_name: str,
        positives: PositiveCases,
        negatives: NegativeCases,
    ) -> None:
        precision, recall = _measure_precision_recall(pl_engine, detector_name, positives, negatives)

        assert precision >= 0.90, f"{detector_name} precision below threshold: {precision:.2%}"
        assert recall >= 0.80, f"{detector_name} recall below threshold: {recall:.2%}"
