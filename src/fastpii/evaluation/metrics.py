from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Metrics:
    precision: float
    recall: float
    f1: float
    f2: float
    true_positives: int
    false_positives: int
    false_negatives: int

    @property
    def support(self) -> int:
        return self.true_positives + self.false_negatives


def calculate_metrics(tp: int, fp: int, fn: int) -> Metrics:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    if precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
        f2 = 5 * precision * recall / (4 * precision + recall)
    else:
        f1 = 0.0
        f2 = 0.0

    return Metrics(
        precision=precision,
        recall=recall,
        f1=f1,
        f2=f2,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
    )


def aggregate_metrics(metrics_list: list[Metrics]) -> Metrics:
    total_tp = sum(m.true_positives for m in metrics_list)
    total_fp = sum(m.false_positives for m in metrics_list)
    total_fn = sum(m.false_negatives for m in metrics_list)
    return calculate_metrics(total_tp, total_fp, total_fn)