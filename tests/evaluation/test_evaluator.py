import json
from pathlib import Path

import pytest

from fastpii.evaluation.evaluator import Evaluator, CorpusSample
from fastpii.evaluation.metrics import Metrics, calculate_metrics
from fastpii.evaluation.report import generate_json_report, generate_markdown_report
from fastpii.evaluation.regression import compare_results, save_baseline


class TestCorpusSample:
    def test_creation(self):
        sample = CorpusSample(
            id="CZ-ICO-001",
            category="contract",
            description="Test contract",
            input="IČO: 25596641",
            expected_findings=[{"type": "ico", "value": "25596641", "start": 5, "end": 13}],
            difficulty="easy",
        )
        assert sample.id == "CZ-ICO-001"
        assert sample.category == "contract"


class TestEvaluatorLoadCorpus:
    def test_load_corpus_from_json(self, tmp_path):
        corpus_data = {
            "version": "1.0",
            "samples": [
                {
                    "id": "CZ-ICO-001",
                    "category": "contract",
                    "description": "Test",
                    "input": "IČO: 25596641",
                    "expected_findings": [
                        {"type": "ico", "value": "25596641", "start": 5, "end": 13}
                    ],
                    "difficulty": "easy",
                }
            ],
        }
        json_path = tmp_path / "test_corpus.json"
        with open(json_path, "w") as f:
            json.dump(corpus_data, f)

        from fastpii import FastPII, DEFAULT_PRIORITY
        engine = FastPII(priority=DEFAULT_PRIORITY)
        evaluator = Evaluator(engine)
        samples = evaluator.load_corpus(tmp_path)
        assert len(samples) == 1
        assert samples[0].id == "CZ-ICO-001"

    def test_skip_schema_json(self, tmp_path):
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema"}
        schema_path = tmp_path / "schema.json"
        with open(schema_path, "w") as f:
            json.dump(schema, f)

        from fastpii import FastPII, DEFAULT_PRIORITY
        engine = FastPII(priority=DEFAULT_PRIORITY)
        evaluator = Evaluator(engine)
        samples = evaluator.load_corpus(tmp_path)
        assert len(samples) == 0


class TestEvaluatorEvaluateSample:
    def test_build_ground_truth_with_offsets(self):
        from fastpii import FastPII, DEFAULT_PRIORITY
        engine = FastPII(priority=DEFAULT_PRIORITY)
        evaluator = Evaluator(engine)

        sample = CorpusSample(
            id="CZ-ICO-001",
            category="contract",
            description="Test",
            input="IČO: 25596641 je registrováno",
            expected_findings=[
                {"type": "ico", "value": "25596641", "start": 5, "end": 13}
            ],
            difficulty="easy",
        )

        spans = evaluator._build_ground_truth(sample)
        assert len(spans) == 1
        assert spans[0].start == 5
        assert spans[0].end == 13

    def test_build_ground_truth_without_offsets(self):
        from fastpii import FastPII, DEFAULT_PRIORITY
        engine = FastPII(priority=DEFAULT_PRIORITY)
        evaluator = Evaluator(engine)

        sample = CorpusSample(
            id="CZ-ICO-001",
            category="contract",
            description="Test",
            input="IČO: 25596641",
            expected_findings=[
                {"type": "ico", "value": "25596641"}
            ],
            difficulty="easy",
        )

        spans = evaluator._build_ground_truth(sample)
        assert len(spans) == 1
        assert spans[0].start == 5
        assert spans[0].end == 13

    def test_get_context(self):
        text = "A" * 100 + "TARGET" + "B" * 100
        result = Evaluator._get_context(text, 100, 106, window=20)
        assert "TARGET" in result


class TestReportGeneration:
    def _make_result(self) -> Metrics:
        return calculate_metrics(80, 5, 15)

    def test_generate_json_report(self, tmp_path):
        metrics = self._make_result()
        from fastpii.evaluation.evaluator import EvaluationResult
        result = EvaluationResult(
            corpus_version="1.0",
            overall_metrics=metrics,
            per_detector_metrics={"ico": metrics},
            per_category_metrics={"contract": metrics},
            per_difficulty_metrics={"easy": metrics},
            confusion_matrix={},
            false_positives=[],
            false_negatives=[],
            word_count=10000,
            fp_per_1000_words=0.5,
            total_samples=100,
        )

        output_path = tmp_path / "results.json"
        generate_json_report(result, output_path)

        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
        assert "overall" in data
        assert data["overall"]["true_positives"] == 80

    def test_generate_markdown_report(self, tmp_path):
        metrics = self._make_result()
        from fastpii.evaluation.evaluator import EvaluationResult
        result = EvaluationResult(
            corpus_version="1.0",
            overall_metrics=metrics,
            per_detector_metrics={"ico": metrics},
            per_category_metrics={"contract": metrics},
            per_difficulty_metrics={"easy": metrics},
            confusion_matrix={},
            false_positives=[],
            false_negatives=[],
            word_count=10000,
            fp_per_1000_words=0.5,
            total_samples=100,
        )

        output_path = tmp_path / "report.md"
        generate_markdown_report(result, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "FastPII Evaluation Report" in content
        assert "Per-Detector Metrics" in content


class TestRegressionDetection:
    def test_first_run_no_baseline(self, tmp_path):
        metrics = calculate_metrics(80, 5, 15)
        passed, issues = compare_results(metrics, tmp_path / "nonexistent.json")
        assert passed is True
        assert "first run" in issues[0].lower()

    def test_regression_detected(self, tmp_path):
        baseline = {
            "overall": {
                "precision": 0.95,
                "recall": 0.90,
                "f1": 0.92,
                "f2": 0.91,
            }
        }
        baseline_path = tmp_path / "baseline.json"
        with open(baseline_path, "w") as f:
            json.dump(baseline, f)

        current_metrics = calculate_metrics(70, 10, 20)
        passed, issues = compare_results(current_metrics, baseline_path)
        assert passed is False
        assert any("REGRESSION" in i for i in issues)

    def test_no_regression(self, tmp_path):
        baseline = {
            "overall": {
                "precision": 0.90,
                "recall": 0.85,
                "f1": 0.87,
                "f2": 0.86,
            }
        }
        baseline_path = tmp_path / "baseline.json"
        with open(baseline_path, "w") as f:
            json.dump(baseline, f)

        current_metrics = calculate_metrics(92, 5, 10)
        passed, issues = compare_results(current_metrics, baseline_path)
        assert passed is True

    def test_save_baseline(self, tmp_path):
        metrics = calculate_metrics(80, 5, 15)
        baseline_path = tmp_path / "baseline.json"
        save_baseline(baseline_path, metrics)

        assert baseline_path.exists()
        with open(baseline_path) as f:
            data = json.load(f)
        assert data["overall"]["true_positives"] == 80