from __future__ import annotations

import pytest

from fastpii import (
    DEFAULT_CONFIDENCE_SCORES,
    DEFAULT_CONTEXT_BOOST,
    DEFAULT_PRIORITY,
    DetectionResult,
    FastPII,
    Finding,
    MaskStrategy,
    RedactStrategy,
    RemoveStrategy,
    TransformationEngine,
)
from fastpii.core.confidence import ConfidenceScorer
from fastpii.core.overlap import deduplicate_findings
from fastpii.countries.cz import CzechPack


def _finding(
    start: int,
    end: int,
    *,
    finding_type: str = "secret",
    value: str = "",
    confidence: float = 1.0,
    region: str = "cz",
) -> Finding:
    return Finding(
        type=finding_type,
        value=value,
        start=start,
        end=end,
        confidence=confidence,
        region=region,
    )


def _result(text: str, *findings: Finding) -> DetectionResult:
    return DetectionResult(
        text=text,
        findings=list(findings),
        detector_names=[],
        processing_time_ms=0,
    )


@pytest.fixture
def engine() -> FastPII:
    guard = FastPII(
        priority=DEFAULT_PRIORITY,
        confidence_scorer=ConfidenceScorer(
            base_scores=DEFAULT_CONFIDENCE_SCORES,
            context_boost=DEFAULT_CONTEXT_BOOST,
        ),
    )
    guard.register(CzechPack())
    return guard


class TestBoundsValidation:
    def test_skips_negative_start(self) -> None:
        result = _result("abcdef", _finding(-1, 3, finding_type="email"))

        assert TransformationEngine.apply(result, RedactStrategy()) == "abcdef"

    def test_skips_negative_end(self) -> None:
        result = _result("abcdef", _finding(1, -3, finding_type="email"))

        assert TransformationEngine.apply(result, RedactStrategy()) == "abcdef"

    def test_skips_start_beyond_text_length(self) -> None:
        result = _result("abcdef", _finding(7, 9, finding_type="email"))

        assert TransformationEngine.apply(result, RedactStrategy()) == "abcdef"

    def test_skips_start_at_text_length(self) -> None:
        result = _result("abcdef", _finding(6, 6, finding_type="email"))

        assert TransformationEngine.apply(result, RedactStrategy()) == "abcdef"

    def test_clips_end_beyond_text_length_for_redact(self) -> None:
        result = _result("abcdef", _finding(2, 99, finding_type="email"))

        assert TransformationEngine.apply(result, RedactStrategy()) == "ab[EMAIL]"

    def test_clips_end_beyond_text_length_for_mask(self) -> None:
        result = _result("abcdef", _finding(2, 99))

        assert TransformationEngine.apply(result, MaskStrategy()) == "ab****"

    def test_skips_start_greater_than_end(self) -> None:
        result = _result("abcdef", _finding(5, 3, finding_type="email"))

        assert TransformationEngine.apply(result, RedactStrategy()) == "abcdef"

    def test_skips_zero_length_finding_for_redact(self) -> None:
        result = _result("abcdef", _finding(3, 3, finding_type="email"))

        assert TransformationEngine.apply(result, RedactStrategy()) == "abcdef"

    def test_skips_zero_length_finding_for_remove(self) -> None:
        result = _result("abcdef", _finding(3, 3))

        assert TransformationEngine.apply(result, RemoveStrategy()) == "abcdef"

    def test_applies_finding_at_full_text_boundaries(self) -> None:
        result = _result("abcdef", _finding(0, 6, finding_type="email"))

        assert TransformationEngine.apply(result, RedactStrategy()) == "[EMAIL]"

    def test_applies_finding_at_start_boundary(self) -> None:
        result = _result("abcdef", _finding(0, 2))

        assert TransformationEngine.apply(result, MaskStrategy()) == "**cdef"

    def test_applies_finding_at_end_boundary(self) -> None:
        result = _result("abcdef", _finding(4, 6))

        assert TransformationEngine.apply(result, RemoveStrategy()) == "abcd"


class TestEmptyTextAndZeroLength:
    @pytest.mark.parametrize(
        "strategy",
        [RedactStrategy(), MaskStrategy(), RemoveStrategy()],
    )
    def test_empty_text_returns_empty(
        self,
        strategy: RedactStrategy | MaskStrategy | RemoveStrategy,
    ) -> None:
        result = _result("", _finding(0, 4, finding_type="email"))

        assert TransformationEngine.apply(result, strategy) == ""

    def test_mask_strategy_returns_empty_for_zero_length(self) -> None:
        assert MaskStrategy().replace(_finding(2, 2), "abcdef") == ""

    def test_mask_strategy_returns_empty_for_negative_width(self) -> None:
        assert MaskStrategy().replace(_finding(4, 2), "abcdef") == ""


class TestUnicodeCharacterPositions:
    def test_mask_preserves_length_for_czech_multibyte_characters(self) -> None:
        text = "Jméno: ěščřž"
        start = text.index("ě")
        end = len(text)
        result = _result(text, _finding(start, end, value="ěščřž"))
        masked = TransformationEngine.apply(result, MaskStrategy())

        assert masked == "Jméno: *****"
        assert len(masked) == len(text)

    def test_redact_replaces_czech_multibyte_characters_exactly(self) -> None:
        text = "Jméno: ěščřž"
        start = text.index("ě")
        end = len(text)
        result = _result(text, _finding(start, end, finding_type="name", value="ěščřž"))

        assert TransformationEngine.apply(result, RedactStrategy()) == "Jméno: [NAME]"

    def test_redact_replaces_flag_emoji_using_character_positions(self) -> None:
        text = "Vlajka 🇨🇿 je zde"
        start = text.index("🇨🇿")
        end = start + len("🇨🇿")
        result = _result(text, _finding(start, end, finding_type="flag", value="🇨🇿"))

        assert TransformationEngine.apply(result, RedactStrategy()) == "Vlajka [FLAG] je zde"

    def test_mask_preserves_length_for_flag_emoji_span(self) -> None:
        text = "Vlajka 🇨🇿 je zde"
        start = text.index("🇨🇿")
        end = start + len("🇨🇿")
        result = _result(text, _finding(start, end, value="🇨🇿"))
        masked = TransformationEngine.apply(result, MaskStrategy())

        assert masked == "Vlajka ** je zde"
        assert len(masked) == len(text)


class TestAdjacentFindings:
    def test_adjacent_findings_share_boundary_and_both_redact(self) -> None:
        result = _result(
            "abcdef",
            _finding(1, 3, finding_type="left"),
            _finding(3, 5, finding_type="right"),
        )

        assert TransformationEngine.apply(result, RedactStrategy()) == "a[LEFT][RIGHT]f"

    def test_adjacent_findings_both_mask_without_overlap(self) -> None:
        result = _result(
            "abcdef",
            _finding(1, 3),
            _finding(3, 5),
        )
        masked = TransformationEngine.apply(result, MaskStrategy())

        assert masked == "a****f"
        assert len(masked) == 6

    def test_adjacent_remove_produces_no_extra_whitespace(self) -> None:
        text = "foo abcd bar"
        result = _result(
            text,
            _finding(4, 6, value="ab"),
            _finding(6, 8, value="cd"),
        )

        assert TransformationEngine.apply(result, RemoveStrategy()) == "foo  bar"


class TestReverseOrderCorrectness:
    def test_reverse_order_handles_mixed_length_replacements(self) -> None:
        class VariableLengthStrategy:
            def replace(self, finding: Finding, text: str) -> str:
                _ = text
                replacements = {
                    "first": "<LONG-FIRST>",
                    "second": "?",
                    "third": "[END]",
                }
                return replacements[finding.type]

        result = _result(
            "abc def ghi",
            _finding(8, 11, finding_type="third"),
            _finding(0, 3, finding_type="first"),
            _finding(4, 7, finding_type="second"),
        )

        assert TransformationEngine.apply(result, VariableLengthStrategy()) == "<LONG-FIRST> ? [END]"

    def test_reverse_order_is_correct_with_unsorted_findings(self) -> None:
        class VariableLengthStrategy:
            def replace(self, finding: Finding, text: str) -> str:
                _ = text
                return {"tail": "<TAIL>", "head": "X"}[finding.type]

        result = _result(
            "abcdef",
            _finding(3, 6, finding_type="tail"),
            _finding(0, 3, finding_type="head"),
        )

        assert TransformationEngine.apply(result, VariableLengthStrategy()) == "X<TAIL>"


class TestNestedFindings:
    def test_nested_findings_keep_higher_priority_inner_before_transform(self) -> None:
        findings = deduplicate_findings(
            [
                _finding(1, 5, finding_type="outer", confidence=0.8),
                _finding(2, 4, finding_type="inner", confidence=0.9),
            ],
            priority={"outer": 10, "inner": 20},
        )
        result = _result("abcdef", *findings)

        assert TransformationEngine.apply(result, RedactStrategy()) == "ab[INNER]ef"

    def test_nested_findings_keep_higher_priority_outer_before_transform(self) -> None:
        findings = deduplicate_findings(
            [
                _finding(1, 5, finding_type="outer", confidence=0.9),
                _finding(2, 4, finding_type="inner", confidence=0.8),
            ],
            priority={"outer": 20, "inner": 10},
        )
        result = _result("abcdef", *findings)

        assert TransformationEngine.apply(result, RedactStrategy()) == "a[OUTER]f"


class TestRoundTripWithRealEngine:
    def test_unicode_context_does_not_break_mask_for_detected_email(self, engine: FastPII) -> None:
        text = "Pozdrav ěščřž 🇨🇿: jan@email.cz"
        masked = engine.mask(text)

        assert len(masked) == len(text)
        assert "jan@email.cz" not in masked

    def test_unicode_email_round_trip_remove(self, engine: FastPII) -> None:
        text = "Kontakt: uživatel@firma.cz"
        removed = engine.remove(text)

        assert "uživatel@firma.cz" not in removed
        assert removed == "Kontakt: "

    def test_findings_at_document_boundaries_with_real_detection(self, engine: FastPII) -> None:
        text = "jan@email.cz je kontakt 800101/1238"
        redacted = engine.redact(text)

        assert "jan@email.cz" not in redacted
        assert "800101/1238" not in redacted
        assert redacted.startswith("[EMAIL]")
        assert redacted.endswith("[RODNE_CISLO]")

    def test_remove_adjacent_real_findings_does_not_add_whitespace(self, engine: FastPII) -> None:
        text = "Email: jan@email.cz,OP: 123456789"
        removed = engine.remove(text)

        assert removed == "Email: ,OP: "
