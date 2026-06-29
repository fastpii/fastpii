from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from fastpii.evaluation.metrics import Metrics

__all__ = ["REGRESSION_THRESHOLDS", "compare_results", "save_baseline"]

REGRESSION_THRESHOLDS: dict[str, float] = {
    "precision": 0.02,
    "recall": 0.02,
    "f1": 0.02,
}


def compare_results(
    current_metrics: Metrics,
    previous_path: Path,
) -> tuple[bool, list[str]]:
    if not previous_path.exists():
        return True, ["No previous results found — first run"]

    with open(previous_path, encoding="utf-8") as f:
        previous: dict[str, dict[str, float]] = json.load(f)

    previous_overall = previous.get("overall", {})
    issues: list[str] = []
    passed = True

    for metric, threshold in REGRESSION_THRESHOLDS.items():
        current_val = getattr(current_metrics, metric)
        previous_val = previous_overall.get(metric, 0.0)
        delta = current_val - previous_val

        if delta < -threshold:
            passed = False
            issues.append(
                f"REGRESSION: {metric} dropped {delta:.2%} "
                f"({previous_val:.2%} -> {current_val:.2%}, "
                f"threshold: {threshold:.2%})"
            )
        elif delta < 0:
            issues.append(
                f"WARNING: {metric} decreased {delta:.2%} "
                f"({previous_val:.2%} -> {current_val:.2%})"
            )

    return passed, issues


def save_baseline(result_path: Path, metrics: Metrics, extra: dict[str, object] | None = None) -> None:
    baseline = {
        "overall": {
            "precision": metrics.precision,
            "recall": metrics.recall,
            "f1": metrics.f1,
            "f2": metrics.f2,
            "true_positives": metrics.true_positives,
            "false_positives": metrics.false_positives,
            "false_negatives": metrics.false_negatives,
        },
    }
    if extra:
        baseline.update(cast(dict[str, dict[str, float | int]], extra))

    result_path.parent.mkdir(parents=True, exist_ok=True)
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)
