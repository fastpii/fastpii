import pytest

from fastpii import DEFAULT_PRIORITY
from fastpii.core.overlap import deduplicate_findings
from fastpii.models import Finding


def make_finding(
    finding_type: str,
    start: int,
    end: int,
    *,
    value: str | None = None,
    confidence: float = 0.95,
    region: str = "cz",
    metadata: dict[str, object] | None = None,
) -> Finding:
    return Finding(
        type=finding_type,
        value=value if value is not None else finding_type,
        start=start,
        end=end,
        confidence=confidence,
        region=region,
        metadata=metadata or {},
    )


class TestOverlapOrdering:
    def test_three_way_overlap_same_position_highest_priority_wins(self):
        findings = [
            make_finding("phone", 5, 15, confidence=0.99),
            make_finding("postal_code", 5, 15, confidence=0.99),
            make_finding("address", 5, 15, confidence=0.99),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["address"]

    def test_equal_priority_equal_confidence_longer_span_wins(self):
        priority = {"alpha": 50, "beta": 50}
        findings = [
            make_finding("alpha", 2, 8, confidence=0.90),
            make_finding("beta", 2, 12, confidence=0.90),
        ]

        result = deduplicate_findings(findings, priority=priority)

        assert [finding.type for finding in result] == ["beta"]

    def test_equal_priority_equal_confidence_equal_length_earlier_start_wins(self):
        priority = {"alpha": 50, "beta": 50, "gamma": 50}
        findings = [
            make_finding("gamma", 2, 6, confidence=0.90),
            make_finding("beta", 1, 5, confidence=0.90),
            make_finding("alpha", 0, 4, confidence=0.90),
        ]

        result = deduplicate_findings(findings, priority=priority)

        assert [finding.type for finding in result] == ["alpha"]

    def test_equal_priority_equal_confidence_equal_length_is_input_order_independent(self):
        priority = {"alpha": 50, "beta": 50, "gamma": 50}
        findings = [
            make_finding("alpha", 0, 4, confidence=0.90),
            make_finding("gamma", 2, 6, confidence=0.90),
            make_finding("beta", 1, 5, confidence=0.90),
        ]

        result = deduplicate_findings(findings, priority=priority)

        assert [finding.type for finding in result] == ["alpha"]

    def test_same_start_different_end_keeps_longer_container(self):
        priority = {"alpha": 50, "beta": 50}
        findings = [
            make_finding("alpha", 3, 9, confidence=0.90),
            make_finding("beta", 3, 12, confidence=0.90),
        ]

        result = deduplicate_findings(findings, priority=priority)

        assert [finding.type for finding in result] == ["beta"]

    def test_same_end_different_start_keeps_longer_container(self):
        priority = {"alpha": 50, "beta": 50}
        findings = [
            make_finding("alpha", 6, 12, confidence=0.90),
            make_finding("beta", 3, 12, confidence=0.90),
        ]

        result = deduplicate_findings(findings, priority=priority)

        assert [finding.type for finding in result] == ["beta"]

    def test_nested_findings_same_type_keep_longer_span(self):
        findings = [
            make_finding("email", 10, 18, confidence=0.95),
            make_finding("email", 12, 15, confidence=0.95),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [(finding.start, finding.end) for finding in result] == [(10, 18)]

    def test_adjacent_non_overlapping_findings_are_preserved(self):
        findings = [
            make_finding("name", 0, 4),
            make_finding("email", 4, 14),
            make_finding("phone", 14, 20),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["name", "email", "phone"]


class TestInvalidSpanHandling:
    def test_zero_length_non_empty_value_is_filtered_and_does_not_interfere(self):
        findings = [
            make_finding("email", 3, 3, value="ghost", confidence=1.0),
            make_finding("name", 0, 5, confidence=0.70),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["name"]

    def test_zero_length_non_empty_value_at_boundary_is_filtered(self):
        findings = [make_finding("email", 8, 8, value="ghost")]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert result == []

    def test_empty_value_zero_length_finding_is_preserved(self):
        findings = [make_finding("email", 8, 8, value="")]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert result == findings

    def test_negative_start_is_skipped(self):
        findings = [
            make_finding("email", -1, 8),
            make_finding("phone", 10, 18),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["phone"]

    def test_negative_end_is_skipped(self):
        findings = [
            make_finding("email", 1, -1),
            make_finding("phone", 10, 18),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["phone"]

    def test_start_greater_than_end_is_skipped(self):
        findings = [
            make_finding("email", 9, 3),
            make_finding("phone", 10, 18),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["phone"]

    def test_all_invalid_findings_return_empty_list(self):
        findings = [
            make_finding("email", -2, 4),
            make_finding("phone", 6, 3),
            make_finding("name", 9, 9, value="ghost"),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert result == []

    def test_mixed_invalid_and_valid_findings_keep_valid_results_sorted(self):
        findings = [
            make_finding("email", 15, 10),
            make_finding("phone", 20, 26),
            make_finding("name", 0, 4),
            make_finding("postal_code", -3, 2),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["name", "phone"]


class TestStressAndGeneralCases:
    def test_many_overlapping_findings_keep_only_highest_priority(self):
        priority = {f"type_{index}": index for index in range(12)}
        findings = [
            make_finding(f"type_{index}", 20, 40, confidence=0.50 + index / 100)
            for index in range(12)
        ]

        result = deduplicate_findings(findings, priority=priority)

        assert [finding.type for finding in result] == ["type_11"]

    def test_many_overlapping_findings_preserve_non_overlapping_tail(self):
        priority = {f"type_{index}": index for index in range(12)}
        findings = [
            make_finding(f"type_{index}", 20, 40, confidence=0.50 + index / 100)
            for index in range(12)
        ]
        findings.append(make_finding("tail", 50, 60, confidence=0.40))
        priority["tail"] = -1

        result = deduplicate_findings(findings, priority=priority)

        assert [finding.type for finding in result] == ["type_11", "tail"]

    def test_single_finding_is_preserved(self):
        finding = make_finding("email", 0, 12)

        result = deduplicate_findings([finding], priority=DEFAULT_PRIORITY)

        assert result == [finding]

    def test_single_finding_requires_explicit_priority(self):
        finding = make_finding("email", 0, 12)

        with pytest.raises(ValueError, match="Overlap priority is required"):
            _ = deduplicate_findings([finding], priority=None)

    def test_empty_findings_list_returns_empty_list(self):
        assert deduplicate_findings([], priority=DEFAULT_PRIORITY) == []

    def test_unknown_type_uses_zero_priority_but_keeps_non_overlapping_result(self):
        findings = [
            make_finding("unknown", 0, 6, confidence=0.99),
            make_finding("email", 8, 18, confidence=0.70),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["unknown", "email"]

    def test_identical_span_same_scores_prefers_first_stable_result(self):
        priority = {"alpha": 50, "beta": 50}
        findings = [
            make_finding("alpha", 0, 5, confidence=0.90),
            make_finding("beta", 0, 5, confidence=0.90),
        ]

        result = deduplicate_findings(findings, priority=priority)

        assert [finding.type for finding in result] == ["alpha"]
