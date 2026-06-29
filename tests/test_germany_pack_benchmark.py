from __future__ import annotations

from dataclasses import dataclass

import pytest

from fastpii import (
    DEFAULT_CONFIDENCE_SCORES,
    DEFAULT_CONTEXT_BOOST,
    DEFAULT_PRIORITY,
    FastPII,
)
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.de.pack import GermanPack


VALID_STEUER_IDS = (
    "86095742719",
    "84237594599",
    "86937640926",
)
VALID_UST_IDS = (
    "DE136695976",
    "DE247033107",
)


@dataclass(frozen=True)
class AccuracyExample:
    text: str
    should_detect: bool
    expected_value: str | None = None


@dataclass(frozen=True)
class AccuracyMetrics:
    precision: float
    recall: float
    true_positives: int
    false_positives: int
    false_negatives: int


@pytest.fixture
def de_engine() -> FastPII:
    engine = FastPII(
        priority=DEFAULT_PRIORITY,
        confidence_scorer=ConfidenceScorer(
            base_scores=DEFAULT_CONFIDENCE_SCORES,
            context_boost=DEFAULT_CONTEXT_BOOST,
        ),
    )
    engine.register(GermanPack())
    return engine


def _detect_findings(engine: FastPII, text: str, detector_name: str):
    return [
        finding
        for finding in engine.detect(text, detector_names=[detector_name]).findings
        if finding.type == detector_name
    ]


def _assert_single_detection(engine: FastPII, text: str, detector_name: str):
    findings = _detect_findings(engine, text, detector_name)
    assert len(findings) == 1
    return findings[0]


def _assert_no_detection(engine: FastPII, text: str, detector_name: str) -> None:
    assert _detect_findings(engine, text, detector_name) == []


def _measure_accuracy(
    engine: FastPII,
    detector_name: str,
    examples: tuple[AccuracyExample, ...],
) -> AccuracyMetrics:
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    for example in examples:
        findings = _detect_findings(engine, example.text, detector_name)
        values = [finding.value for finding in findings]

        if example.should_detect:
            assert example.expected_value is not None
            if example.expected_value in values:
                true_positives += 1
                false_positives += max(0, len(values) - 1)
            else:
                false_negatives += 1
                false_positives += len(values)
        else:
            false_positives += len(values)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) else 0.0

    return AccuracyMetrics(
        precision=precision,
        recall=recall,
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
    )


class TestSteuerIDBenchmark:
    @pytest.mark.parametrize(
        ("text", "expected_value"),
        [
            ("Steuer-ID: 86095742719", "86095742719"),
            ("Steueridentifikationsnummer: 84237594599", "84237594599"),
        ],
    )
    def test_detects_valid_ids_with_context(self, de_engine: FastPII, text: str, expected_value: str) -> None:
        finding = _assert_single_detection(de_engine, text, "steuer_id")

        assert finding.value == expected_value
        assert finding.metadata["checksum_valid"] is True
        assert finding.confidence >= 0.95

    @pytest.mark.parametrize("value", ["86095742710", "12345", "06095742719"])
    def test_rejects_invalid_checksum_and_format(self, de_engine: FastPII, value: str) -> None:
        assert de_engine.validate(value, "steuer_id").is_valid is False
        _assert_no_detection(de_engine, f"Steuer-ID: {value}", "steuer_id")

    def test_validate_accepts_whitespace_variation(self, de_engine: FastPII) -> None:
        assert de_engine.validate("860 957 427 19", "steuer_id").is_valid is True

    def test_context_gating_uses_lower_confidence_without_label(self, de_engine: FastPII) -> None:
        finding = _assert_single_detection(de_engine, VALID_STEUER_IDS[0], "steuer_id")

        assert 0.8 <= finding.confidence < 0.95


class TestUStIdBenchmark:
    @pytest.mark.parametrize(
        ("text", "expected_value"),
        [
            ("USt-IdNr: DE136695976", "DE136695976"),
            ("VAT: DE247033107", "DE247033107"),
        ],
    )
    def test_detects_valid_ids_with_context(self, de_engine: FastPII, text: str, expected_value: str) -> None:
        finding = _assert_single_detection(de_engine, text, "ust_id")

        assert finding.value == expected_value
        assert finding.metadata["checksum_valid"] is True
        assert finding.confidence >= 0.95

    @pytest.mark.parametrize("value", ["DE123456789", "136695976", "DE023456789"])
    def test_rejects_invalid_checksum_and_prefix(self, de_engine: FastPII, value: str) -> None:
        assert de_engine.validate(value, "ust_id").is_valid is False
        if value.startswith("DE"):
            _assert_no_detection(de_engine, f"USt-IdNr: {value}", "ust_id")

    def test_validate_accepts_lowercase_prefix(self, de_engine: FastPII) -> None:
        assert de_engine.validate("de136695976", "ust_id").is_valid is True

    def test_context_gating_uses_lower_confidence_without_label(self, de_engine: FastPII) -> None:
        finding = _assert_single_detection(de_engine, VALID_UST_IDS[0], "ust_id")

        assert 0.85 <= finding.confidence < 0.95


class TestHandelsregisterBenchmark:
    @pytest.mark.parametrize(
        ("text", "court", "register_type", "number"),
        [
            ("Handelsregister: München HRB 12345", "München", "HRB", "12345"),
            ("Registernummer: Berlin HRB 98765", "Berlin", "HRB", "98765"),
            ("Handelsregister: Hamburg HRA 54321", "Hamburg", "HRA", "54321"),
            ("Register: Köln PR 11223", "Köln", "PR", "11223"),
        ],
    )
    def test_detects_common_register_formats(
        self,
        de_engine: FastPII,
        text: str,
        court: str,
        register_type: str,
        number: str,
    ) -> None:
        finding = _assert_single_detection(de_engine, text, "handelsregister")

        assert finding.metadata["court"] == court
        assert finding.metadata["type"] == register_type
        assert finding.metadata["number"] == number
        assert finding.confidence >= 0.9

    @pytest.mark.parametrize("value", ["XYZ", "HRB 01234", "Berlin HR 12345"])
    def test_rejects_invalid_formats(self, de_engine: FastPII, value: str) -> None:
        assert de_engine.validate(value, "handelsregister").is_valid is False
        _assert_no_detection(de_engine, f"Handelsregister: {value}", "handelsregister")

    def test_context_gating_uses_lower_confidence_without_label(self, de_engine: FastPII) -> None:
        finding = _assert_single_detection(de_engine, "München HRB 12345", "handelsregister")

        assert 0.75 <= finding.confidence < 0.9


class TestDEPostalCodeBenchmark:
    @pytest.mark.parametrize(
        ("text", "expected_value"),
        [
            ("PLZ: 10115 Berlin", "10115"),
            ("Postleitzahl: 80331 München", "80331"),
            ("Hauptstraße 12, 50667 Köln", "50667"),
        ],
    )
    def test_detects_valid_postal_codes_with_context(
        self,
        de_engine: FastPII,
        text: str,
        expected_value: str,
    ) -> None:
        finding = _assert_single_detection(de_engine, text, "postal_code")

        assert finding.value == expected_value
        assert finding.metadata["zone"] == expected_value[0]
        assert finding.confidence >= 0.75

    def test_validate_known_invalid_postal_code(self, de_engine: FastPII) -> None:
        assert de_engine.validate("00000", "postal_code").is_valid is False

    @pytest.mark.parametrize("text", ["10115", "00000", "Ticket 99999 ist offen"])
    def test_context_gating_blocks_bare_or_trap_values(self, de_engine: FastPII, text: str) -> None:
        _assert_no_detection(de_engine, text, "postal_code")


class TestDEPhoneBenchmark:
    @pytest.mark.parametrize(
        ("text", "expected_value", "phone_type"),
        [
            ("+49 30 1234567", "49301234567", "landline"),
            ("+49-170-1234567", "491701234567", "mobile"),
            ("Telefon: 030 1234567", "49301234567", "landline"),
        ],
    )
    def test_detects_valid_numbers(
        self,
        de_engine: FastPII,
        text: str,
        expected_value: str,
        phone_type: str,
    ) -> None:
        finding = _assert_single_detection(de_engine, text, "phone")

        assert finding.value == expected_value
        assert finding.metadata["phone_type"] == phone_type
        assert finding.confidence >= 0.85

    @pytest.mark.parametrize("text", ["030 1234567", "123", "012345"])
    def test_context_gating_and_length_rules_block_invalid_cases(self, de_engine: FastPII, text: str) -> None:
        _assert_no_detection(de_engine, text, "phone")


class TestDEAddressBenchmark:
    def test_detects_full_address_with_embedded_postal_code(self, de_engine: FastPII) -> None:
        finding = _assert_single_detection(de_engine, "Adresse: Hauptstraße 12, 10115 Berlin", "address")

        assert finding.value == "Hauptstraße 12, 10115 Berlin"
        assert finding.metadata["street"] == "Hauptstraße"
        assert finding.metadata["house_number"] == "12"
        assert finding.metadata["postal_code"] == "10115"
        assert finding.metadata["city"] == "Berlin"
        assert finding.confidence >= 0.8

    def test_raw_address_and_postal_code_detectors_overlap(self, de_engine: FastPII) -> None:
        text = "Hauptstraße 12, 10115 Berlin"
        address_finding = de_engine.get_detector("address").detect(text)[0]
        postal_finding = de_engine.get_detector("postal_code").detect(text)[0]

        assert address_finding.start < postal_finding.end
        assert postal_finding.start < address_finding.end

    def test_address_beats_postal_code_in_engine_overlap_resolution(self, de_engine: FastPII) -> None:
        result = de_engine.detect("Hauptstraße 12, 10115 Berlin")

        assert [finding.type for finding in result.findings] == ["address"]
        assert result.findings[0].value == "Hauptstraße 12, 10115 Berlin"

    def test_address_and_separate_postal_code_both_survive_when_not_overlapping(self, de_engine: FastPII) -> None:
        result = de_engine.detect("Hauptstraße 12. PLZ: 10115 Berlin")

        assert [finding.type for finding in result.findings] == ["address", "postal_code"]

    @pytest.mark.parametrize("text", ["Hauptstraße", "12, 10115 Berlin", "Artikel 12, 10115"])
    def test_rejects_incomplete_address_shapes(self, de_engine: FastPII, text: str) -> None:
        _assert_no_detection(de_engine, text, "address")


class TestDEFalsePositiveTraps:
    @pytest.mark.parametrize(
        ("detector_name", "text"),
        [
            ("steuer_id", "Bestellnummer 86095742710"),
            ("ust_id", "Artikelnummer DE123456789"),
            ("handelsregister", "Interner Code HRB 01234"),
            ("postal_code", "Ticket 10115 wurde geschlossen"),
            ("phone", "Build 030 1234567 fehlgeschlagen"),
            ("address", "Projekt Hauptstraße ohne Hausnummer"),
        ],
    )
    def test_trap_values_do_not_trigger_detection(
        self,
        de_engine: FastPII,
        detector_name: str,
        text: str,
    ) -> None:
        _assert_no_detection(de_engine, text, detector_name)


DETECTOR_BENCHMARKS: dict[str, tuple[AccuracyExample, ...]] = {
    "steuer_id": (
        AccuracyExample("Steuer-ID: 86095742719", True, "86095742719"),
        AccuracyExample("Steueridentifikationsnummer: 84237594599", True, "84237594599"),
        AccuracyExample("86937640926", True, "86937640926"),
        AccuracyExample("Steuer-ID: 86095742710", False),
        AccuracyExample("12345", False),
        AccuracyExample("Bestellnummer 86095742710", False),
    ),
    "ust_id": (
        AccuracyExample("USt-IdNr: DE136695976", True, "DE136695976"),
        AccuracyExample("VAT: DE247033107", True, "DE247033107"),
        AccuracyExample("DE136695976", True, "DE136695976"),
        AccuracyExample("USt-IdNr: DE123456789", False),
        AccuracyExample("DE023456789", False),
        AccuracyExample("Artikelnummer DE123456789", False),
    ),
    "handelsregister": (
        AccuracyExample("Handelsregister: München HRB 12345", True, "München HRB 12345"),
        AccuracyExample("Registernummer: Berlin HRB 98765", True, "Berlin HRB 98765"),
        AccuracyExample("Hamburg HRA 54321", True, "Hamburg HRA 54321"),
        AccuracyExample("Handelsregister: HRB 01234", False),
        AccuracyExample("Interner Code HRB 01234", False),
        AccuracyExample("Berlin HR 12345", False),
    ),
    "postal_code": (
        AccuracyExample("PLZ: 10115 Berlin", True, "10115"),
        AccuracyExample("Postleitzahl: 80331 München", True, "80331"),
        AccuracyExample("50667 Köln", True, "50667"),
        AccuracyExample("10115", False),
        AccuracyExample("00000", False),
        AccuracyExample("Ticket 99999 ist offen", False),
    ),
    "phone": (
        AccuracyExample("+49 30 1234567", True, "49301234567"),
        AccuracyExample("+49-170-1234567", True, "491701234567"),
        AccuracyExample("Telefon: 030 1234567", True, "49301234567"),
        AccuracyExample("030 1234567", False),
        AccuracyExample("123", False),
        AccuracyExample("Build 030 1234567 fehlgeschlagen", False),
    ),
    "address": (
        AccuracyExample("Adresse: Hauptstraße 12, 10115 Berlin", True, "Hauptstraße 12, 10115 Berlin"),
        AccuracyExample("Schillerstraße 8, 80331 München", True, "Schillerstraße 8, 80331 München"),
        AccuracyExample("Bahnhofstraße 5", True, "Bahnhofstraße 5"),
        AccuracyExample("Hauptstraße", False),
        AccuracyExample("12, 10115 Berlin", False),
        AccuracyExample("Projekt Hauptstraße ohne Hausnummer", False),
    ),
}


class TestDEDetectorAccuracy:
    @pytest.mark.parametrize("detector_name", sorted(DETECTOR_BENCHMARKS))
    def test_precision_and_recall_thresholds(self, de_engine: FastPII, detector_name: str) -> None:
        metrics = _measure_accuracy(de_engine, detector_name, DETECTOR_BENCHMARKS[detector_name])

        assert metrics.precision >= 0.90, metrics
        assert metrics.recall >= 0.80, metrics
