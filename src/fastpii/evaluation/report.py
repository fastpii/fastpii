from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastpii.evaluation.evaluator import EvaluationResult


def generate_json_report(result: EvaluationResult, output_path: Path) -> None:
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "corpus_version": result.corpus_version,
        "total_samples": result.total_samples,
        "word_count": result.word_count,
        "overall": {
            "precision": round(result.overall_metrics.precision, 4),
            "recall": round(result.overall_metrics.recall, 4),
            "f1": round(result.overall_metrics.f1, 4),
            "f2": round(result.overall_metrics.f2, 4),
            "true_positives": result.overall_metrics.true_positives,
            "false_positives": result.overall_metrics.false_positives,
            "false_negatives": result.overall_metrics.false_negatives,
            "fp_per_1000_words": round(result.fp_per_1000_words, 2),
        },
        "per_detector": {
            k: {
                "precision": round(v.precision, 4),
                "recall": round(v.recall, 4),
                "f1": round(v.f1, 4),
                "f2": round(v.f2, 4),
                "support": v.support,
                "true_positives": v.true_positives,
                "false_positives": v.false_positives,
                "false_negatives": v.false_negatives,
            }
            for k, v in result.per_detector_metrics.items()
        },
        "per_category": {
            k: {
                "precision": round(v.precision, 4),
                "recall": round(v.recall, 4),
                "f1": round(v.f1, 4),
                "support": v.support,
            }
            for k, v in result.per_category_metrics.items()
        },
        "per_difficulty": {
            k: {
                "precision": round(v.precision, 4),
                "recall": round(v.recall, 4),
                "f1": round(v.f1, 4),
                "support": v.support,
            }
            for k, v in result.per_difficulty_metrics.items()
        },
        "confusion_matrix": result.confusion_matrix,
        "false_positives_count": len(result.false_positives),
        "false_negatives_count": len(result.false_negatives),
        "false_positives": [
            {
                "sample_id": fp.sample_id,
                "predicted_type": fp.predicted_type,
                "predicted_value": fp.predicted_value,
                "context": fp.context,
            }
            for fp in result.false_positives[:100]
        ],
        "false_negatives": [
            {
                "sample_id": fn.sample_id,
                "expected_type": fn.expected_type,
                "expected_value": fn.expected_value,
                "context": fn.context,
            }
            for fn in result.false_negatives[:100]
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def generate_markdown_report(result: EvaluationResult, output_path: Path) -> None:
    lines = [
        "# FastPII Evaluation Report",
        "",
        f"**Timestamp:** {datetime.now(timezone.utc).isoformat()}",
        f"**Corpus Version:** {result.corpus_version}",
        f"**Total Samples:** {result.total_samples}",
        f"**Total Words:** {result.word_count}",
        "",
        "## Overall Metrics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Precision | {result.overall_metrics.precision:.2%} |",
        f"| Recall | {result.overall_metrics.recall:.2%} |",
        f"| F1 | {result.overall_metrics.f1:.2%} |",
        f"| F2 | {result.overall_metrics.f2:.2%} |",
        f"| FP/1000 words | {result.fp_per_1000_words:.2f} |",
        "",
        "## Per-Detector Metrics",
        "",
        "| Detector | Precision | Recall | F1 | Support |",
        "|----------|-----------|--------|-----|---------|",
    ]

    for det in sorted(result.per_detector_metrics.keys()):
        m = result.per_detector_metrics[det]
        lines.append(
            f"| {det} | {m.precision:.2%} | {m.recall:.2%} | {m.f1:.2%} | {m.support} |"
        )

    if result.per_category_metrics:
        lines.extend([
            "",
            "## Per-Category Metrics",
            "",
            "| Category | Precision | Recall | F1 |",
            "|----------|-----------|--------|-----|",
        ])
        for cat in sorted(result.per_category_metrics.keys()):
            m = result.per_category_metrics[cat]
            lines.append(f"| {cat} | {m.precision:.2%} | {m.recall:.2%} | {m.f1:.2%} |")

    if result.per_difficulty_metrics:
        lines.extend([
            "",
            "## Per-Difficulty Metrics",
            "",
            "| Difficulty | Precision | Recall | F1 |",
            "|-----------|-----------|--------|-----|",
        ])
        for diff in sorted(result.per_difficulty_metrics.keys()):
            m = result.per_difficulty_metrics[diff]
            lines.append(f"| {diff} | {m.precision:.2%} | {m.recall:.2%} | {m.f1:.2%} |")

    lines.extend([
        "",
        f"## False Positives ({len(result.false_positives)} total)",
        "",
    ])
    for fp in result.false_positives[:20]:
        lines.append(f"- **{fp.sample_id}**: `{fp.predicted_type}` = `{fp.predicted_value}` — {fp.context[:80]}")

    lines.extend([
        "",
        f"## False Negatives ({len(result.false_negatives)} total)",
        "",
    ])
    for fn in result.false_negatives[:20]:
        lines.append(f"- **{fn.sample_id}**: `{fn.expected_type}` = `{fn.expected_value}` — {fn.context[:80]}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        _ = f.write("\n".join(lines))