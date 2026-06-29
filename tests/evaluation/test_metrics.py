import pytest

from fastpii.evaluation.metrics import Metrics, calculate_metrics, aggregate_metrics


class TestCalculateMetrics:
    def test_perfect_scores(self):
        m = calculate_metrics(10, 0, 0)
        assert m.precision == 1.0
        assert m.recall == 1.0
        assert m.f1 == 1.0
        assert m.f2 == 1.0

    def test_zero_denominators(self):
        m = calculate_metrics(0, 0, 0)
        assert m.precision == 0.0
        assert m.recall == 0.0
        assert m.f1 == 0.0
        assert m.f2 == 0.0

    def test_all_false_positives(self):
        m = calculate_metrics(0, 5, 0)
        assert m.precision == 0.0
        assert m.recall == 0.0

    def test_all_false_negatives(self):
        m = calculate_metrics(0, 0, 5)
        assert m.precision == 0.0
        assert m.recall == 0.0

    def test_mixed_results(self):
        m = calculate_metrics(8, 2, 2)
        assert m.precision == pytest.approx(0.8)
        assert m.recall == pytest.approx(0.8)
        assert m.f1 == pytest.approx(0.8)
        assert m.true_positives == 8
        assert m.false_positives == 2
        assert m.false_negatives == 2

    def test_support_property(self):
        m = calculate_metrics(8, 2, 2)
        assert m.support == 10

    def test_f2_weighted_recall(self):
        m = calculate_metrics(4, 1, 5)
        assert m.precision == pytest.approx(0.8)
        assert m.recall == pytest.approx(4 / 9)
        assert m.f2 < m.f1

    def test_precision_only(self):
        m = calculate_metrics(5, 0, 5)
        assert m.precision == 1.0
        assert m.recall == pytest.approx(0.5)

    def test_recall_only(self):
        m = calculate_metrics(5, 5, 0)
        assert m.precision == pytest.approx(0.5)
        assert m.recall == 1.0


class TestAggregateMetrics:
    def test_aggregate_single(self):
        m = calculate_metrics(10, 2, 3)
        result = aggregate_metrics([m])
        assert result.precision == m.precision
        assert result.recall == m.recall

    def test_aggregate_multiple(self):
        m1 = calculate_metrics(10, 2, 3)
        m2 = calculate_metrics(8, 1, 2)
        result = aggregate_metrics([m1, m2])
        assert result.true_positives == 18
        assert result.false_positives == 3
        assert result.false_negatives == 5

    def test_aggregate_empty(self):
        result = aggregate_metrics([])
        assert result.true_positives == 0
        assert result.precision == 0.0