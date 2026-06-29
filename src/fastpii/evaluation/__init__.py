"""FastPII Evaluation Harness.

Production-grade evaluation with IoU-based span matching,
per-detector metrics, regression detection, and report generation.

Usage:
    from fastpii.evaluation import Evaluator, Span, Metrics
    from fastpii import FastPII
    from fastpii.countries.cz import CzechPack

    engine = FastPII(priority={"rodne_cislo": 100, "ico": 95})
    engine.register(CzechPack())

    evaluator = Evaluator(engine)
    result = evaluator.evaluate_corpus(Path("tests/benchmarks/corpus"))
    print(f"Precision: {result.overall_metrics.precision:.2%}")
    print(f"Recall:    {result.overall_metrics.recall:.2%}")
    print(f"F1:        {result.overall_metrics.f1:.2%}")
"""

from fastpii.evaluation.iou_matcher import Span, calculate_iou, match_spans
from fastpii.evaluation.metrics import Metrics, calculate_metrics, aggregate_metrics
from fastpii.evaluation.evaluator import Evaluator, EvaluationResult, CorpusSample
from fastpii.evaluation.report import generate_json_report, generate_markdown_report
from fastpii.evaluation.regression import compare_results, REGRESSION_THRESHOLDS

__all__ = [
    "Span",
    "calculate_iou",
    "match_spans",
    "Metrics",
    "calculate_metrics",
    "aggregate_metrics",
    "Evaluator",
    "EvaluationResult",
    "CorpusSample",
    "generate_json_report",
    "generate_markdown_report",
    "compare_results",
    "REGRESSION_THRESHOLDS",
]