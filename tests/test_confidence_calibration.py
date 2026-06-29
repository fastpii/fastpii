from fastpii import DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST
from fastpii.core.confidence import ConfidenceScorer


class TestConfidenceScorerBasics:
    def test_checksum_validated_returns_1_0(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=DEFAULT_CONTEXT_BOOST)

        assert scorer.calculate(has_context=False, has_checksum=True) == 1.0

    def test_context_match_returns_base(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=DEFAULT_CONTEXT_BOOST)

        assert scorer.calculate(has_context=False, base_confidence=DEFAULT_CONFIDENCE_SCORES["context_match"]) == 0.95

    def test_pattern_match_returns_base(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=DEFAULT_CONTEXT_BOOST)

        assert scorer.calculate(has_context=False, base_confidence=DEFAULT_CONFIDENCE_SCORES["pattern_match"]) == 0.85

    def test_no_context_returns_base(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=DEFAULT_CONTEXT_BOOST)

        assert scorer.calculate(has_context=False) == 0.7

    def test_base_confidence_overrides_all(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=DEFAULT_CONTEXT_BOOST)

        assert scorer.calculate(has_context=True, has_checksum=True, base_confidence=0.321) == 0.321

    def test_context_boost_applied_when_context_and_no_checksum(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=DEFAULT_CONTEXT_BOOST)

        assert scorer.calculate(has_context=True, base_confidence=0.8) == 0.9

    def test_context_boost_not_applied_when_checksum(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=DEFAULT_CONTEXT_BOOST)

        assert scorer.calculate(has_context=True, has_checksum=True, base_confidence=0.8) == 0.8

    def test_context_boost_capped_at_1_0(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=DEFAULT_CONTEXT_BOOST)

        assert scorer.calculate(has_context=True, base_confidence=0.97) == 1.0

    def test_scores_are_rounded_to_3_decimals(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=DEFAULT_CONTEXT_BOOST)

        assert scorer.calculate(has_context=False, base_confidence=0.123456) == 0.123


class TestConfidenceScorerCustomScores:
    def test_custom_base_scores(self):
        scorer = ConfidenceScorer(
            base_scores={
                "checksum_validated": 0.99,
                "context_match": 0.88,
                "pattern_match": 0.77,
                "no_context": 0.66,
            },
            context_boost=0.05,
        )

        assert scorer.calculate(has_context=False, has_checksum=True) == 0.99
        assert scorer.calculate(has_context=False, base_confidence=0.88) == 0.88
        assert scorer.calculate(has_context=False, base_confidence=0.77) == 0.77
        assert scorer.calculate(has_context=False) == 0.66

    def test_custom_context_boost(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=0.2)

        assert scorer.calculate(has_context=True, base_confidence=0.6) == 0.8

    def test_zero_context_boost(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=0.0)

        assert scorer.calculate(has_context=True, base_confidence=0.6) == 0.6

    def test_large_context_boost_capped(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=0.5)

        assert scorer.calculate(has_context=True, base_confidence=0.8) == 1.0


class TestConfidenceCalibrationContract:
    def test_checksum_always_highest(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=DEFAULT_CONTEXT_BOOST)

        checksum = scorer.calculate(has_context=False, has_checksum=True)
        context = scorer.calculate(has_context=True)
        pattern = scorer.calculate(has_context=False, base_confidence=DEFAULT_CONFIDENCE_SCORES["pattern_match"])
        no_context = scorer.calculate(has_context=False)

        assert checksum >= context >= pattern >= no_context

    def test_confidence_never_below_zero(self):
        scorer = ConfidenceScorer(base_scores={
            "checksum_validated": 0.0,
            "context_match": 0.0,
            "pattern_match": 0.0,
            "no_context": 0.0,
        }, context_boost=0.0)

        assert scorer.calculate(has_context=False, has_checksum=True) >= 0.0
        assert scorer.calculate(has_context=True) >= 0.0
        assert scorer.calculate(has_context=False) >= 0.0

    def test_confidence_never_above_one(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=DEFAULT_CONTEXT_BOOST)

        assert scorer.calculate(has_context=False, has_checksum=True) <= 1.0
        assert scorer.calculate(has_context=True) <= 1.0
        assert scorer.calculate(has_context=False) <= 1.0

    def test_default_scores_satisfy_invariants(self):
        assert DEFAULT_CONFIDENCE_SCORES["checksum_validated"] >= DEFAULT_CONFIDENCE_SCORES["context_match"]
        assert DEFAULT_CONFIDENCE_SCORES["context_match"] >= DEFAULT_CONFIDENCE_SCORES["pattern_match"]
        assert DEFAULT_CONFIDENCE_SCORES["pattern_match"] >= DEFAULT_CONFIDENCE_SCORES["no_context"]
        assert DEFAULT_CONTEXT_BOOST >= 0.0

    def test_context_always_boosts_when_no_checksum(self):
        scorer = ConfidenceScorer(base_scores=DEFAULT_CONFIDENCE_SCORES, context_boost=DEFAULT_CONTEXT_BOOST)

        assert scorer.calculate(has_context=True, base_confidence=0.4) >= scorer.calculate(has_context=False, base_confidence=0.4)
