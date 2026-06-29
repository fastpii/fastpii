from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from fastpii import FastPII
from fastpii.evaluation.iou_matcher import Span, match_spans
from fastpii.evaluation.metrics import Metrics, calculate_metrics, aggregate_metrics


__all__ = ["CorpusSample", "EvaluationResult", "Evaluator"]


@dataclass
class CorpusSample:
    id: str
    category: str
    description: str
    input: str
    expected_findings: list[dict[str, str | int]]
    difficulty: str


@dataclass
class SampleError:
    sample_id: str
    predicted_type: str
    predicted_value: str
    expected_type: str
    expected_value: str
    context: str


@dataclass
class EvaluationResult:
    corpus_version: str
    overall_metrics: Metrics
    per_detector_metrics: dict[str, Metrics]
    per_category_metrics: dict[str, Metrics]
    per_difficulty_metrics: dict[str, Metrics]
    confusion_matrix: dict[str, dict[str, int]]
    false_positives: list[SampleError]
    false_negatives: list[SampleError]
    word_count: int
    fp_per_1000_words: float
    total_samples: int


class Evaluator:
    engine: FastPII
    iou_threshold: float

    def __init__(self, engine: FastPII, iou_threshold: float = 0.5) -> None:
        self.engine = engine
        self.iou_threshold = iou_threshold

    def load_corpus(self, corpus_path: Path) -> list[CorpusSample]:
        samples: list[CorpusSample] = []
        for json_file in sorted(corpus_path.glob("*.json")):
            if json_file.name == "schema.json":
                continue
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
            for s in data.get("samples", []):
                samples.append(CorpusSample(
                    id=s.get("id", ""),
                    category=s.get("category", ""),
                    description=s.get("description", ""),
                    input=s.get("input", ""),
                    expected_findings=s.get("expected_findings", []),
                    difficulty=s.get("difficulty", ""),
                ))
        return samples

    def evaluate_sample(self, sample: CorpusSample) -> tuple[list[tuple[Span, Span, float]], list[SampleError], list[SampleError]]:
        result = self.engine.detect(sample.input)

        predicted = [
            Span(start=f.start, end=f.end, pii_type=f.type, value=f.value)
            for f in result.findings
        ]

        ground_truth = self._build_ground_truth(sample)

        matched, false_positives, false_negatives = match_spans(
            predicted, ground_truth, self.iou_threshold
        )

        fp_errors = [
            SampleError(
                sample_id=sample.id,
                predicted_type=fp.pii_type,
                predicted_value=fp.value,
                expected_type="",
                expected_value="",
                context=self._get_context(sample.input, fp.start, fp.end),
            )
            for fp in false_positives
        ]

        fn_errors = [
            SampleError(
                sample_id=sample.id,
                predicted_type="",
                predicted_value="",
                expected_type=fn.pii_type,
                expected_value=fn.value,
                context=self._get_context(sample.input, fn.start, fn.end),
            )
            for fn in false_negatives
        ]

        return matched, fp_errors, fn_errors

    def evaluate_corpus(self, corpus_path: Path) -> EvaluationResult:
        samples = self.load_corpus(corpus_path)

        detector_tp: dict[str, int] = {}
        detector_fp: dict[str, int] = {}
        detector_fn: dict[str, int] = {}
        category_tp: dict[str, int] = {}
        category_fp: dict[str, int] = {}
        category_fn: dict[str, int] = {}
        difficulty_tp: dict[str, int] = {}
        difficulty_fp: dict[str, int] = {}
        difficulty_fn: dict[str, int] = {}
        confusion: dict[str, dict[str, int]] = {}
        all_fps: list[SampleError] = []
        all_fns: list[SampleError] = []
        total_words = 0

        for sample in samples:
            matched_list, fp_errors, fn_errors = self.evaluate_sample(sample)
            total_words += len(sample.input.split())

            tp = len(matched_list)
            fp = len(fp_errors)
            fn = len(fn_errors)

            for m in matched_list:
                det = m[0].pii_type
                detector_tp[det] = detector_tp.get(det, 0) + 1

            for fp_err in fp_errors:
                det = fp_err.predicted_type
                detector_fp[det] = detector_fp.get(det, 0) + 1
                if det not in confusion:
                    confusion[det] = {}
                confusion[det].setdefault("none", 0)
                confusion[det]["none"] += 1

            for fn_err in fn_errors:
                det = fn_err.expected_type
                detector_fn[det] = detector_fn.get(det, 0) + 1

            category_tp[sample.category] = category_tp.get(sample.category, 0) + tp
            category_fp[sample.category] = category_fp.get(sample.category, 0) + fp
            category_fn[sample.category] = category_fn.get(sample.category, 0) + fn

            difficulty_tp[sample.difficulty] = difficulty_tp.get(sample.difficulty, 0) + tp
            difficulty_fp[sample.difficulty] = difficulty_fp.get(sample.difficulty, 0) + fp
            difficulty_fn[sample.difficulty] = difficulty_fn.get(sample.difficulty, 0) + fn

            all_fps.extend(fp_errors)
            all_fns.extend(fn_errors)

        per_detector = {
            t: calculate_metrics(detector_tp.get(t, 0), detector_fp.get(t, 0), detector_fn.get(t, 0))
            for t in set(list(detector_tp.keys()) + list(detector_fn.keys()))
        }

        per_category = {
            c: calculate_metrics(category_tp.get(c, 0), category_fp.get(c, 0), category_fn.get(c, 0))
            for c in set(list(category_tp.keys()) + list(category_fn.keys()))
        }

        per_difficulty = {
            d: calculate_metrics(difficulty_tp.get(d, 0), difficulty_fp.get(d, 0), difficulty_fn.get(d, 0))
            for d in set(list(difficulty_tp.keys()) + list(difficulty_fn.keys()))
        }

        overall = aggregate_metrics(list(per_detector.values())) if per_detector else calculate_metrics(0, 0, 0)

        fp_per_1000 = (len(all_fps) / total_words * 1000) if total_words > 0 else 0.0

        return EvaluationResult(
            corpus_version="1.0",
            overall_metrics=overall,
            per_detector_metrics=per_detector,
            per_category_metrics=per_category,
            per_difficulty_metrics=per_difficulty,
            confusion_matrix=confusion,
            false_positives=all_fps,
            false_negatives=all_fns,
            word_count=total_words,
            fp_per_1000_words=fp_per_1000,
            total_samples=len(samples),
        )

    def _build_ground_truth(self, sample: CorpusSample) -> list[Span]:
        spans: list[Span] = []
        for ef in sample.expected_findings:
            pii_type = str(ef.get("type", ""))
            value = str(ef.get("value", ""))
            start_val = ef.get("start")
            end_val = ef.get("end")

            if isinstance(start_val, int) and isinstance(end_val, int):
                spans.append(Span(start=start_val, end=end_val, pii_type=pii_type, value=value))
            else:
                idx = sample.input.find(value)
                if idx >= 0:
                    spans.append(Span(start=idx, end=idx + len(value), pii_type=pii_type, value=value))

        return spans

    @staticmethod
    def _get_context(text: str, start: int, end: int, window: int = 50) -> str:
        ctx_start = max(0, start - window)
        ctx_end = min(len(text), end + window)
        return text[ctx_start:ctx_end]
