"""Redaction and anonymization correctness tests for all Czech privacy modes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fastpii import FastPII, DEFAULT_PRIORITY, DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST, Finding
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.cz import CzechPack
from fastpii.evaluation.evaluator import CorpusSample, Evaluator


DETECTOR_CASES = [
    ("rodne_cislo", "RČ: 800101/1238"),
    ("ico", "IČO: 25596641"),
    ("dic", "DIČ: CZ25596641"),
    ("bank_account", "Číslo účtu: 19-2000145399/0800"),
    ("postal_code", "PSČ: 110 00"),
    ("phone", "Telefon: +420 777 888 999"),
    ("date_of_birth", "Datum narození: 01.01.1980"),
    ("address", "Adresa: Vinohradská 45, 120 00 Praha 2"),
    ("name", "Jméno: Jan Novák"),
    ("email", "Email: jan@email.cz"),
    ("vehicle_plate", "SPZ: 1A2 3456"),
    ("date", "Datum: 15.03.2024"),
    ("identity_card", "OP: 123456789"),
    ("health_insurance", "Pojištění: 211/123456"),
    ("iban", "IBAN: CZ29 0800 0000 0001 9200 0145"),
]

MODE_NAMES = ["anonymize", "redact", "mask", "remove"]


@pytest.fixture
def engine() -> FastPII:
    guard = FastPII(
        priority=DEFAULT_PRIORITY,
        confidence_scorer=ConfidenceScorer(
            base_scores=DEFAULT_CONFIDENCE_SCORES,
            context_boost=DEFAULT_CONTEXT_BOOST,
        ),
    )
    guard.register(CzechPack())
    return guard


def _expected_finding(engine: FastPII, text: str, expected_type: str) -> Finding:
    result = engine.detect(text)
    assert [finding.type for finding in result.findings] == [expected_type]
    return result.findings[0]


def _original_tokens(text: str, finding: Finding) -> set[str]:
    tokens = {finding.value, text[finding.start:finding.end]}
    return {token for token in tokens if token}


def _assert_tokens_removed(output: str, text: str, finding: Finding) -> None:
    for token in _original_tokens(text, finding):
        assert token not in output, f"Original PII token {token!r} leaked into {output!r}"


def _transform(engine: FastPII, mode: str, text: str) -> str:
    if mode == "anonymize":
        return engine.anonymize(text)
    if mode == "redact":
        return engine.redact(text)
    if mode == "mask":
        return engine.mask(text)
    if mode == "remove":
        return engine.remove(text)
    raise ValueError(f"Unsupported mode: {mode}")


def _combined_text() -> str:
    return "\n".join(text for _, text in DETECTOR_CASES)


def _build_samples() -> list[CorpusSample]:
    samples: list[CorpusSample] = []
    for detector_type, text in DETECTOR_CASES:
        pii_value = text.split(": ", maxsplit=1)[1]
        samples.append(
            CorpusSample(
                id=f"CZ-{detector_type.upper()}-001",
                category="redaction_correctness",
                description=f"Evaluation harness sample for {detector_type}",
                input=text,
                expected_findings=[{"type": detector_type, "value": pii_value}],
                difficulty="easy",
            )
        )
    return samples


class TestPerDetectorAnonymize:
    @pytest.mark.parametrize(("detector_type", "text"), DETECTOR_CASES)
    def test_anonymize_replaces_each_detector(self, engine: FastPII, detector_type: str, text: str) -> None:
        finding = _expected_finding(engine, text, detector_type)
        output = engine.anonymize(text)

        _assert_tokens_removed(output, text, finding)
        assert "[REDACTED]" in output


class TestPerDetectorRedact:
    @pytest.mark.parametrize(("detector_type", "text"), DETECTOR_CASES)
    def test_redact_replaces_each_detector(self, engine: FastPII, detector_type: str, text: str) -> None:
        finding = _expected_finding(engine, text, detector_type)
        output = engine.redact(text)

        _assert_tokens_removed(output, text, finding)
        assert f"[{detector_type.upper()}]" in output


class TestPerDetectorMask:
    @pytest.mark.parametrize(("detector_type", "text"), DETECTOR_CASES)
    def test_mask_replaces_each_detector(self, engine: FastPII, detector_type: str, text: str) -> None:
        finding = _expected_finding(engine, text, detector_type)
        output = engine.mask(text)

        _assert_tokens_removed(output, text, finding)
        assert "*" in output
        assert len(output) == len(text)


class TestPerDetectorRemove:
    @pytest.mark.parametrize(("detector_type", "text"), DETECTOR_CASES)
    def test_remove_replaces_each_detector(self, engine: FastPII, detector_type: str, text: str) -> None:
        finding = _expected_finding(engine, text, detector_type)
        output = engine.remove(text)

        _assert_tokens_removed(output, text, finding)
        assert output == text[:finding.start] + text[finding.end:]


class TestRoundTripSafety:
    @pytest.mark.parametrize("mode", MODE_NAMES)
    def test_redetect_transformed_text_finds_no_original_pii(self, engine: FastPII, mode: str) -> None:
        text = _combined_text()
        original = engine.detect(text)
        transformed = _transform(engine, mode, text)
        redetected = engine.detect(transformed)

        original_tokens = {
            token
            for finding in original.findings
            for token in _original_tokens(text, finding)
        }
        redetected_tokens = {
            token
            for finding in redetected.findings
            for token in _original_tokens(transformed, finding)
        }

        for token in original_tokens:
            assert token not in transformed
            assert token not in redetected_tokens


class TestCompleteness:
    @pytest.mark.parametrize("mode", MODE_NAMES)
    def test_all_original_pii_tokens_are_removed_from_combined_text(self, engine: FastPII, mode: str) -> None:
        text = _combined_text()
        result = engine.detect(text)
        transformed = _transform(engine, mode, text)

        for finding in result.findings:
            _assert_tokens_removed(transformed, text, finding)

    @pytest.mark.parametrize("mode", MODE_NAMES)
    def test_repeated_transformation_does_not_restore_original_values(self, engine: FastPII, mode: str) -> None:
        text = _combined_text()
        result = engine.detect(text)
        first_pass = _transform(engine, mode, text)
        second_pass = _transform(engine, mode, first_pass)

        for finding in result.findings:
            _assert_tokens_removed(second_pass, text, finding)


class TestBoundaryCases:
    @pytest.mark.parametrize("mode", MODE_NAMES)
    def test_pii_at_document_start_and_end(self, engine: FastPII, mode: str) -> None:
        text = "jan@email.cz je kontakt a OP: 123456789"
        transformed = _transform(engine, mode, text)

        assert "jan@email.cz" not in transformed
        assert "123456789" not in transformed
        assert "je kontakt a OP: " in transformed

    def test_overlapping_identifiers_transform_safely(self, engine: FastPII) -> None:
        text = "DIČ: CZ25596641 obsahuje IČO: 25596641"
        redacted = engine.redact(text)

        assert "CZ25596641" not in redacted
        assert "25596641" not in redacted
        assert "[DIC]" in redacted
        assert "[ICO]" in redacted

    def test_adjacent_identifiers_transform_safely(self, engine: FastPII) -> None:
        text = "Email: jan@email.cz,OP: 123456789"
        masked = engine.mask(text)

        assert "jan@email.cz" not in masked
        assert "123456789" not in masked
        assert len(masked) == len(text)

    def test_multiple_sensitive_spans_on_separate_lines(self, engine: FastPII) -> None:
        text = "RČ: 800101/1238\nIBAN: CZ29 0800 0000 0001 9200 0145"
        removed = engine.remove(text)

        assert "800101/1238" not in removed
        assert "CZ29 0800 0000 0001 9200 0145" not in removed
        assert removed == "RČ: \nIBAN: "


class TestFormatPreservation:
    @pytest.mark.parametrize(("detector_type", "text"), DETECTOR_CASES)
    def test_mask_preserves_full_input_length(self, engine: FastPII, detector_type: str, text: str) -> None:
        _ = _expected_finding(engine, text, detector_type)
        masked = engine.mask(text)

        assert len(masked) == len(text)

    @pytest.mark.parametrize(("detector_type", "text"), DETECTOR_CASES)
    def test_redact_uses_uppercase_type_labels(self, engine: FastPII, detector_type: str, text: str) -> None:
        _ = _expected_finding(engine, text, detector_type)
        redacted = engine.redact(text)

        assert f"[{detector_type.upper()}]" in redacted

    def test_mask_only_replaces_detected_span_with_asterisks(self, engine: FastPII) -> None:
        text = "Telefon: +420 777 888 999"
        finding = _expected_finding(engine, text, "phone")
        masked = engine.mask(text)

        assert masked[:finding.start] == text[:finding.start]
        assert masked[finding.start:finding.end] == "*" * (finding.end - finding.start)
        assert masked[finding.end:] == text[finding.end:]


class TestEvaluationHarnessIntegration:
    def test_czech_transformation_samples_score_perfectly_in_evaluator(self, engine: FastPII, tmp_path: Path) -> None:
        corpus_path = tmp_path / "cz_redaction_correctness.json"
        payload = {
            "version": "1.0",
            "samples": [
                {
                    "id": sample.id,
                    "category": sample.category,
                    "description": sample.description,
                    "input": sample.input,
                    "expected_findings": sample.expected_findings,
                    "difficulty": sample.difficulty,
                }
                for sample in _build_samples()
            ],
        }
        _ = corpus_path.write_text(json.dumps(payload), encoding="utf-8")

        evaluator = Evaluator(engine)
        result = evaluator.evaluate_corpus(tmp_path)

        assert result.total_samples == len(DETECTOR_CASES)
        assert result.overall_metrics.precision == 1.0
        assert result.overall_metrics.recall == 1.0
        assert result.overall_metrics.f1 == 1.0
        assert set(result.per_detector_metrics) == {detector_type for detector_type, _ in DETECTOR_CASES}
