import pytest

from fastpii.evaluation.iou_matcher import Span, calculate_iou, match_spans


class TestCalculateIoU:
    def test_identical_spans(self):
        s1 = Span(start=10, end=20, pii_type="ico", value="12345678")
        s2 = Span(start=10, end=20, pii_type="ico", value="12345678")
        assert calculate_iou(s1, s2) == 1.0

    def test_no_overlap(self):
        s1 = Span(start=0, end=10, pii_type="ico", value="12345678")
        s2 = Span(start=10, end=20, pii_type="ico", value="87654321")
        assert calculate_iou(s1, s2) == 0.0

    def test_partial_overlap(self):
        s1 = Span(start=0, end=10, pii_type="ico", value="12345678")
        s2 = Span(start=5, end=15, pii_type="ico", value="87654321")
        assert calculate_iou(s1, s2) == pytest.approx(5 / 15)

    def test_contained_span(self):
        s1 = Span(start=0, end=20, pii_type="ico", value="12345678")
        s2 = Span(start=5, end=10, pii_type="ico", value="87654321")
        assert calculate_iou(s1, s2) == pytest.approx(5 / 20)

    def test_adjacent_spans_no_overlap(self):
        s1 = Span(start=0, end=5, pii_type="ico", value="12345")
        s2 = Span(start=5, end=10, pii_type="ico", value="67890")
        assert calculate_iou(s1, s2) == 0.0


class TestMatchSpans:
    def test_perfect_match(self):
        predicted = [Span(start=0, end=5, pii_type="ico", value="12345")]
        ground_truth = [Span(start=0, end=5, pii_type="ico", value="12345")]
        matched, fps, fns = match_spans(predicted, ground_truth)
        assert len(matched) == 1
        assert len(fps) == 0
        assert len(fns) == 0

    def test_no_match(self):
        predicted = [Span(start=0, end=5, pii_type="ico", value="12345")]
        ground_truth = [Span(start=50, end=55, pii_type="ico", value="67890")]
        matched, fps, fns = match_spans(predicted, ground_truth)
        assert len(matched) == 0
        assert len(fps) == 1
        assert len(fns) == 1

    def test_type_mismatch(self):
        predicted = [Span(start=0, end=5, pii_type="ico", value="12345")]
        ground_truth = [Span(start=0, end=5, pii_type="rodne_cislo", value="12345")]
        matched, fps, fns = match_spans(predicted, ground_truth, type_match=True)
        assert len(matched) == 0
        assert len(fps) == 1
        assert len(fns) == 1

    def test_type_mismatch_ignored(self):
        predicted = [Span(start=0, end=5, pii_type="ico", value="12345")]
        ground_truth = [Span(start=0, end=5, pii_type="rodne_cislo", value="12345")]
        matched, fps, fns = match_spans(predicted, ground_truth, type_match=False)
        assert len(matched) == 1
        assert len(fps) == 0
        assert len(fns) == 0

    def test_partial_overlap_below_threshold(self):
        predicted = [Span(start=0, end=10, pii_type="ico", value="12345")]
        ground_truth = [Span(start=8, end=18, pii_type="ico", value="5678")]
        matched, fps, fns = match_spans(predicted, ground_truth, iou_threshold=0.5)
        assert len(matched) == 0

    def test_multiple_predictions_multiple_ground_truth(self):
        predicted = [
            Span(start=0, end=5, pii_type="ico", value="12345"),
            Span(start=10, end=15, pii_type="email", value="a@b.cz"),
        ]
        ground_truth = [
            Span(start=0, end=5, pii_type="ico", value="12345"),
            Span(start=10, end=15, pii_type="email", value="a@b.cz"),
        ]
        matched, fps, fns = match_spans(predicted, ground_truth)
        assert len(matched) == 2
        assert len(fps) == 0
        assert len(fns) == 0

    def test_extra_prediction(self):
        predicted = [
            Span(start=0, end=5, pii_type="ico", value="12345"),
            Span(start=10, end=15, pii_type="email", value="a@b.cz"),
        ]
        ground_truth = [Span(start=0, end=5, pii_type="ico", value="12345")]
        matched, fps, fns = match_spans(predicted, ground_truth)
        assert len(matched) == 1
        assert len(fps) == 1
        assert len(fns) == 0

    def test_missing_prediction(self):
        predicted = [Span(start=0, end=5, pii_type="ico", value="12345")]
        ground_truth = [
            Span(start=0, end=5, pii_type="ico", value="12345"),
            Span(start=10, end=15, pii_type="email", value="a@b.cz"),
        ]
        matched, fps, fns = match_spans(predicted, ground_truth)
        assert len(matched) == 1
        assert len(fps) == 0
        assert len(fns) == 1

    def test_empty_lists(self):
        matched, fps, fns = match_spans([], [])
        assert len(matched) == 0
        assert len(fps) == 0
        assert len(fns) == 0

    def test_strict_threshold(self):
        predicted = [Span(start=0, end=10, pii_type="ico", value="12345")]
        ground_truth = [Span(start=0, end=10, pii_type="ico", value="12345")]
        matched, fps, fns = match_spans(predicted, ground_truth, iou_threshold=0.9)
        assert len(matched) == 1

    def test_strict_threshold_partial_rejected(self):
        predicted = [Span(start=0, end=10, pii_type="ico", value="12345")]
        ground_truth = [Span(start=3, end=13, pii_type="ico", value="34567")]
        matched, fps, fns = match_spans(predicted, ground_truth, iou_threshold=0.9)
        assert len(matched) == 0