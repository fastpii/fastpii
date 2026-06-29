import pytest

from fastpii import FastPII, DEFAULT_PRIORITY, DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST
from fastpii.core.confidence import ConfidenceScorer
from fastpii.core.overlap import deduplicate_findings
from fastpii.countries.cz import CzechPack
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


def build_engine(priority: dict[str, int] | None = None) -> FastPII:
    guard = FastPII(
        priority=priority or DEFAULT_PRIORITY,
        confidence_scorer=ConfidenceScorer(
            base_scores=DEFAULT_CONFIDENCE_SCORES,
            context_boost=DEFAULT_CONTEXT_BOOST,
        ),
    )
    guard.register(CzechPack())
    return guard


def collect_raw_findings(engine: FastPII, text: str, *detector_names: str) -> list[Finding]:
    findings: list[Finding] = []
    for detector_name in detector_names:
        findings.extend(engine.get_detector(detector_name).detect(text))
    return findings


COMPREHENSIVE_CZ_DOC = (
    "Jan Novák\n"
    "Email: jan.novak@example.cz\n"
    "RČ: 800101/1238\n"
    "IČO: 25596641\n"
    "DIČ: CZ25596641\n"
    "Číslo účtu: 19-2000145399/0800\n"
    "IBAN: CZ2908000000000192000145\n"
    "Credit card: 4111111111111111\n"
    "občanský průkaz: 123456789\n"
    "Pojištění: 111/123456\n"
    "Datum narození: 15.03.1980\n"
    "Vinohradská 45\n"
    "PSČ: 120 00\n"
    "Tel: +420 777 123 456\n"
    "SPZ: 1A2 3456\n"
)


def finding_signature(finding: Finding) -> tuple[str, int, int]:
    return (finding.type, finding.start, finding.end)


@pytest.fixture
def engine() -> FastPII:
    return build_engine()


class TestOverlapPairScenarios:
    def test_address_and_postal_code_raw_detectors_overlap(self, engine: FastPII):
        text = "Vinohradská 45, 120 00 Praha 2"

        raw_findings = collect_raw_findings(engine, text, "address", "postal_code")

        assert [finding.type for finding in raw_findings] == ["address", "postal_code"]
        assert raw_findings[0].start < raw_findings[1].end
        assert raw_findings[1].start < raw_findings[0].end

    def test_address_beats_postal_code_in_engine_detection(self, engine: FastPII):
        text = "Vinohradská 45, 120 00 Praha 2"

        result = engine.detect(text)

        assert len(result.findings) == 1
        assert result.findings[0].type == "address"
        assert text[result.findings[0].start:result.findings[0].end] == "Vinohradská 45, 120 00 Praha 2"

    def test_custom_priority_can_make_postal_code_win(self):
        custom_priority = dict(DEFAULT_PRIORITY)
        custom_priority["postal_code"] = 120
        custom_priority["address"] = 10
        custom_engine = build_engine(priority=custom_priority)

        result = custom_engine.detect("Vinohradská 45, 120 00 Praha 2")

        assert len(result.findings) == 1
        assert result.findings[0].type == "postal_code"
        assert result.findings[0].value == "120 00"

    def test_name_and_address_are_preserved_when_spans_do_not_overlap(self, engine: FastPII):
        text = "Jan Novák, Vinohradská 45"

        result = engine.detect(text)

        assert [finding.type for finding in result.findings] == ["name", "address"]
        assert text[result.findings[0].start:result.findings[0].end] == "Jan Novák"
        assert text[result.findings[1].start:result.findings[1].end] == "Vinohradská 45"

    def test_rodne_cislo_beats_embedded_date_when_spans_overlap(self):
        findings = [
            make_finding("date", 0, 6, value="800101", confidence=0.90),
            make_finding("rodne_cislo", 0, 10, value="8001011238", confidence=0.95),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["rodne_cislo"]

    def test_ico_beats_dic_when_using_same_overlapping_numeric_span(self):
        findings = [
            make_finding("dic", 0, 8, value="25596641", confidence=0.95),
            make_finding("ico", 0, 8, value="25596641", confidence=0.95),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["ico"]

    def test_dic_and_ico_both_survive_when_they_appear_in_separate_spans(self, engine: FastPII):
        text = "DIČ: CZ25596641 obsahuje IČO 25596641"

        result = engine.detect(text)

        assert [finding.type for finding in result.findings] == ["dic", "ico"]

    def test_bank_account_loses_to_ico_on_same_overlapping_span_by_default(self):
        findings = [
            make_finding("bank_account", 0, 8, value="25596641", confidence=1.0),
            make_finding("ico", 0, 8, value="25596641", confidence=1.0),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["ico"]

    def test_postal_code_beats_phone_on_same_span_by_default(self):
        findings = [
            make_finding("phone", 0, 6, value="602000", confidence=0.95),
            make_finding("postal_code", 0, 6, value="602 00", confidence=0.95),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["postal_code"]

    def test_phone_and_postal_code_both_survive_when_adjacent(self, engine: FastPII):
        text = "Kontakt: tel 602 123 456, PSČ 602 00"

        result = engine.detect(text)

        assert [finding.type for finding in result.findings] == ["phone", "postal_code"]


class TestPriorityResolution:
    def test_higher_priority_type_wins_on_partial_overlap(self):
        findings = [
            make_finding("postal_code", 5, 11, value="120 00"),
            make_finding("address", 0, 20, value="Vinohradská 45, 120 00"),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["address"]

    def test_custom_priority_changes_winner_for_same_overlap(self):
        findings = [
            make_finding("postal_code", 5, 11, value="120 00"),
            make_finding("address", 0, 20, value="Vinohradská 45, 120 00"),
        ]
        custom_priority = dict(DEFAULT_PRIORITY)
        custom_priority["postal_code"] = 200

        result = deduplicate_findings(findings, priority=custom_priority)

        assert [finding.type for finding in result] == ["postal_code"]

    def test_ico_has_higher_priority_than_dic(self):
        findings = [
            make_finding("dic", 0, 8, confidence=0.99),
            make_finding("ico", 0, 8, confidence=0.80),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["ico"]

    def test_confidence_breaks_ties_when_priorities_match(self):
        priority = {"date": 60, "date_of_birth": 60}
        findings = [
            make_finding("date", 0, 10, confidence=0.70),
            make_finding("date_of_birth", 0, 10, confidence=0.95),
        ]

        result = deduplicate_findings(findings, priority=priority)

        assert [finding.type for finding in result] == ["date_of_birth"]

    def test_length_breaks_ties_when_priority_and_confidence_match(self):
        priority = {"alpha": 50, "beta": 50}
        findings = [
            make_finding("alpha", 0, 4, confidence=0.90),
            make_finding("beta", 0, 8, confidence=0.90),
        ]

        result = deduplicate_findings(findings, priority=priority)

        assert [finding.type for finding in result] == ["beta"]

    def test_unknown_type_defaults_to_zero_priority_and_loses(self):
        findings = [
            make_finding("unknown", 0, 8, confidence=1.0),
            make_finding("email", 0, 8, confidence=0.70),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["email"]

    def test_final_output_is_sorted_by_start_position(self):
        findings = [
            make_finding("email", 20, 30),
            make_finding("phone", 40, 50),
            make_finding("name", 0, 10),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.start for finding in result] == [0, 20, 40]


class TestDeduplicateFindings:
    def test_empty_findings_list_returns_empty_result(self):
        assert deduplicate_findings([], priority=DEFAULT_PRIORITY) == []

    def test_single_finding_is_preserved(self):
        finding = make_finding("email", 0, 10)

        result = deduplicate_findings([finding], priority=DEFAULT_PRIORITY)

        assert result == [finding]

    def test_non_overlapping_findings_are_all_preserved(self):
        findings = [
            make_finding("name", 0, 9),
            make_finding("email", 11, 25),
            make_finding("phone", 27, 39),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert result == findings

    def test_identical_span_same_type_is_reported_once(self):
        findings = [
            make_finding("email", 0, 12, confidence=0.95),
            make_finding("email", 0, 12, confidence=0.70),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert len(result) == 1
        assert result[0].type == "email"
        assert result[0].confidence == 0.95

    def test_identical_span_different_types_keeps_higher_priority(self):
        findings = [
            make_finding("phone", 0, 9),
            make_finding("postal_code", 0, 9),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["postal_code"]

    def test_partial_overlap_keeps_higher_priority_and_drops_lower(self):
        findings = [
            make_finding("name", 0, 9),
            make_finding("email", 5, 20),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["email"]

    def test_nested_overlap_keeps_higher_priority_inner_finding(self):
        findings = [
            make_finding("address", 0, 24),
            make_finding("postal_code", 16, 22),
        ]
        custom_priority = dict(DEFAULT_PRIORITY)
        custom_priority["postal_code"] = 100
        custom_priority["address"] = 10

        result = deduplicate_findings(findings, priority=custom_priority)

        assert [finding.type for finding in result] == ["postal_code"]

    def test_adjacent_spans_are_not_treated_as_overlapping(self):
        findings = [
            make_finding("name", 0, 9),
            make_finding("email", 9, 20),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["name", "email"]

    def test_zero_width_span_at_boundary_does_not_overlap(self):
        findings = [
            make_finding("name", 0, 5),
            make_finding("email", 5, 5, value=""),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert len(result) == 2
        assert [finding.start for finding in result] == [0, 5]

    def test_zero_width_span_inside_existing_span_counts_as_overlap(self):
        findings = [
            make_finding("name", 0, 5, confidence=0.60),
            make_finding("email", 2, 2, value="", confidence=0.95),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["email"]


class TestNoFindingsLost:
    def test_non_overlapping_multi_detector_findings_all_survive(self, engine: FastPII):
        text = "Jan Novák, Email: jan@example.cz, Tel: +420 777 123 456"

        result = engine.detect(text)

        assert [finding.type for finding in result.findings] == ["name", "email", "phone"]

    def test_address_and_separate_postal_code_both_survive_when_not_overlapping(self, engine: FastPII):
        text = "Vinohradská 45. PSČ: 120 00"

        result = engine.detect(text)

        assert [finding.type for finding in result.findings] == ["address", "postal_code"]

    def test_same_value_at_different_positions_is_not_lost(self, engine: FastPII):
        text = "Email: jan@example.cz; znovu Email: jan@example.cz"

        result = engine.detect(text)

        email_findings = [finding for finding in result.findings if finding.type == "email"]
        assert len(email_findings) == 2
        assert email_findings[0].start != email_findings[1].start

    def test_only_truly_overlapping_findings_are_deduplicated(self):
        findings = [
            make_finding("address", 0, 20),
            make_finding("postal_code", 10, 16),
            make_finding("email", 30, 45),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["address", "email"]

    def test_name_and_address_are_not_lost_in_common_contact_line(self, engine: FastPII):
        text = "Jan Novák, Vinohradská 45, tel: +420 777 123 456"

        result = engine.detect(text)

        assert [finding.type for finding in result.findings] == ["name", "address", "phone"]


class TestNoFindingsDuplicated:
    def test_same_span_and_type_manual_duplicate_is_emitted_once(self):
        findings = [
            make_finding("rodne_cislo", 0, 10, confidence=0.95),
            make_finding("rodne_cislo", 0, 10, confidence=0.85),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert len(result) == 1
        assert result[0].type == "rodne_cislo"

    def test_same_span_and_type_from_multiple_code_paths_keeps_highest_confidence(self):
        findings = [
            make_finding("date", 0, 10, confidence=0.70),
            make_finding("date", 0, 10, confidence=0.95),
            make_finding("date", 0, 10, confidence=0.85),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert len(result) == 1
        assert result[0].confidence == 0.95

    def test_duplicate_overlap_does_not_remove_distinct_non_overlapping_finding(self):
        findings = [
            make_finding("email", 0, 12, confidence=0.95),
            make_finding("email", 0, 12, confidence=0.70),
            make_finding("phone", 20, 32, confidence=0.95),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["email", "phone"]

    def test_engine_comprehensive_document_has_no_duplicate_span_type_pairs(self, engine: FastPII):
        result = engine.detect(COMPREHENSIVE_CZ_DOC)
        signatures = [finding_signature(finding) for finding in result.findings]

        assert len(signatures) == len(set(signatures))

    def test_engine_does_not_duplicate_same_email_value_at_different_positions(self, engine: FastPII):
        text = "Email: jan@example.cz a pak znovu jan@example.cz"

        result = engine.detect(text)

        signatures = [finding_signature(finding) for finding in result.findings]
        assert len(signatures) == len(set(signatures))
        assert sum(finding.type == "email" for finding in result.findings) == 2


class TestMultiDetectorIntegration:
    def test_comprehensive_document_triggers_all_15_czech_detectors(self, engine: FastPII):
        result = engine.detect(COMPREHENSIVE_CZ_DOC)
        types = {finding.type for finding in result.findings}

        assert len(result.findings) == 15
        assert types == {
            "address",
            "bank_account",
            "credit_card",
            "date_of_birth",
            "dic",
            "email",
            "health_insurance",
            "iban",
            "ico",
            "identity_card",
            "name",
            "phone",
            "postal_code",
            "rodne_cislo",
            "vehicle_plate",
        }

    def test_comprehensive_document_detector_names_match_finding_types(self, engine: FastPII):
        result = engine.detect(COMPREHENSIVE_CZ_DOC)

        assert set(result.detector_names) == {finding.type for finding in result.findings}
        assert len(result.detector_names) == 15

    def test_comprehensive_document_findings_are_sorted_by_start(self, engine: FastPII):
        result = engine.detect(COMPREHENSIVE_CZ_DOC)

        assert [finding.start for finding in result.findings] == sorted(
            finding.start for finding in result.findings
        )

    def test_comprehensive_document_has_unique_span_type_pairs(self, engine: FastPII):
        result = engine.detect(COMPREHENSIVE_CZ_DOC)
        signatures = [finding_signature(finding) for finding in result.findings]

        assert len(signatures) == len(set(signatures))


class TestEdgeCases:
    def test_three_overlapping_detectors_keep_only_highest_priority(self):
        findings = [
            make_finding("phone", 0, 10, confidence=0.95),
            make_finding("postal_code", 0, 10, confidence=0.95),
            make_finding("address", 0, 10, confidence=0.95),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["address"]

    def test_three_way_overlap_followed_by_non_overlapping_finding_preserves_tail(self):
        findings = [
            make_finding("phone", 0, 10),
            make_finding("postal_code", 0, 10),
            make_finding("address", 0, 10),
            make_finding("email", 20, 30),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["address", "email"]

    def test_adjacent_non_overlapping_findings_are_all_kept(self):
        findings = [
            make_finding("name", 0, 4),
            make_finding("email", 4, 10),
            make_finding("phone", 10, 14),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["name", "email", "phone"]

    def test_pii_at_start_and_end_of_text_is_detected(self, engine: FastPII):
        text = "jan@example.cz text mezi tím RČ: 800101/1238"

        result = engine.detect(text)

        assert [finding.type for finding in result.findings] == ["email", "rodne_cislo"]
        assert result.findings[0].start == 0
        assert result.findings[-1].end == len(text)

    def test_empty_string_returns_no_findings(self, engine: FastPII):
        result = engine.detect("")

        assert result.findings == []

    def test_same_pii_value_appearing_multiple_times_is_kept_per_position(self, engine: FastPII):
        text = "RČ: 800101/1238 a znovu RČ: 800101/1238"

        result = engine.detect(text)

        rodne_findings = [finding for finding in result.findings if finding.type == "rodne_cislo"]
        assert len(rodne_findings) == 2
        assert rodne_findings[0].start != rodne_findings[1].start

    def test_custom_priority_can_invert_normal_order(self):
        findings = [
            make_finding("ico", 0, 8),
            make_finding("dic", 0, 8),
        ]
        custom_priority = dict(DEFAULT_PRIORITY)
        custom_priority["dic"] = 150
        custom_priority["ico"] = 10

        result = deduplicate_findings(findings, priority=custom_priority)

        assert [finding.type for finding in result] == ["dic"]

    def test_zero_width_finding_inside_higher_priority_span_wins_if_sorted_first(self):
        findings = [
            make_finding("phone", 1, 4, confidence=0.60),
            make_finding("address", 2, 2, value="", confidence=0.95),
        ]

        result = deduplicate_findings(findings, priority=DEFAULT_PRIORITY)

        assert [finding.type for finding in result] == ["address"]
