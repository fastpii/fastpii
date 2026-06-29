from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    pii_type: str
    value: str


def calculate_iou(span1: Span, span2: Span) -> float:
    if span1.end <= span2.start or span2.end <= span1.start:
        return 0.0

    intersection_start = max(span1.start, span2.start)
    intersection_end = min(span1.end, span2.end)
    intersection = intersection_end - intersection_start

    union_start = min(span1.start, span2.start)
    union_end = max(span1.end, span2.end)
    union = union_end - union_start

    return intersection / union if union > 0 else 0.0


def match_spans(
    predicted: list[Span],
    ground_truth: list[Span],
    iou_threshold: float = 0.5,
    type_match: bool = True,
) -> tuple[list[tuple[Span, Span, float]], list[Span], list[Span]]:
    matched: list[tuple[Span, Span, float]] = []
    used_gt_indices: set[int] = set()

    for pred in predicted:
        best_iou = 0.0
        best_idx = -1

        for i, gt in enumerate(ground_truth):
            if i in used_gt_indices:
                continue
            if type_match and pred.pii_type != gt.pii_type:
                continue

            iou = calculate_iou(pred, gt)
            if iou >= iou_threshold and iou > best_iou:
                best_iou = iou
                best_idx = i

        if best_idx >= 0:
            matched.append((pred, ground_truth[best_idx], best_iou))
            used_gt_indices.add(best_idx)

    matched_pred_ids = {id(m[0]) for m in matched}
    false_positives = [p for p in predicted if id(p) not in matched_pred_ids]
    false_negatives = [gt for i, gt in enumerate(ground_truth) if i not in used_gt_indices]

    return matched, false_positives, false_negatives