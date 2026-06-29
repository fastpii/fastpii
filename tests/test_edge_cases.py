import pytest

from fastpii import FastPII, DEFAULT_PRIORITY, DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.cz import CzechPack


@pytest.fixture
def engine():
    guard = FastPII(
        priority=DEFAULT_PRIORITY,
        confidence_scorer=ConfidenceScorer(
            base_scores=DEFAULT_CONFIDENCE_SCORES,
            context_boost=DEFAULT_CONTEXT_BOOST,
        ),
    )
    guard.register(CzechPack())
    return guard


class TestCzechDetectorEdgeCases:
    def test_rodne_cislo_edge_case_9_digit(self, engine):
        result = engine.detect("RČ: 530201123")
        
        assert len(result.findings) >= 1
        # 9-digit pre-1954 format should be detected
        rn_findings = [f for f in result.findings if f.type == "rodne_cislo"]
        assert len(rn_findings) >= 1

    def test_rodne_cislo_edge_case_female(self, engine):
        result = engine.detect("Female: 8051011232")
        
        assert len(result.findings) >= 1
        assert result.findings[0].metadata["gender"] == "female"

    def test_rodne_cislo_edge_case_invalid_checksum(self, engine):
        result = engine.validate("8001011235", detector_name="rodne_cislo")
        
        assert result.is_valid is False

    def test_rodne_cislo_edge_case_with_slash(self, engine):
        result = engine.detect("RČ: 800101/1238")
        
        assert len(result.findings) >= 1

    def test_rodne_cislo_edge_case_without_slash(self, engine):
        result = engine.detect("RČ: 8001011238")
        
        assert len(result.findings) >= 1
        assert "800101" in result.findings[0].value

    def test_ico_edge_case_25596641(self, engine):
        result = engine.validate("25596641", detector_name="ico")
        
        assert result.is_valid is True

    def test_ico_edge_case_leading_zeros(self, engine):
        result = engine.detect("IČO: 00000019")

        assert len(result.findings) >= 1
        assert result.findings[0].value == "00000019"

    def test_ico_edge_case_invalid_checksum(self, engine):
        result = engine.validate("12345678", detector_name="ico")
        
        assert result.is_valid is False

    def test_dic_edge_case_company(self, engine):
        result = engine.validate("CZ25596641", detector_name="dic")
        
        assert result.is_valid is True

    def test_dic_edge_case_individual(self, engine):
        result = engine.validate("CZ8001011238", detector_name="dic")
        
        assert result.is_valid is True

    def test_dic_edge_case_special(self, engine):
        result = engine.validate("CZ612345678", detector_name="dic")
        
        assert result.is_valid is True

    def test_bank_account_edge_case_without_prefix(self, engine):
        result = engine.detect("Account: 2000145399/0800")
        
        assert len(result.findings) >= 1

    def test_bank_account_edge_case_with_prefix(self, engine):
        result = engine.detect("Account: 19-2000145399/0800")
        
        assert len(result.findings) >= 1

    def test_bank_account_edge_case_invalid_checksum(self, engine):
        result = engine.validate("19-12/0800", detector_name="bank_account")
        
        assert result.is_valid is False

    def test_postal_code_edge_case_prague(self, engine):
        result = engine.detect("PSČ: 110 00")
        
        assert len(result.findings) >= 1
        assert result.findings[0].value == "110 00"

    def test_postal_code_edge_case_without_space(self, engine):
        result = engine.detect("PSČ: 11000")
        
        assert len(result.findings) >= 1
        assert "110" in result.findings[0].value

    def test_postal_code_edge_case_range_validation(self, engine):
        result = engine.validate("099 99", detector_name="postal_code")
        
        assert result.is_valid is False

    def test_phone_edge_case_mobile_with_country_code(self, engine):
        result = engine.detect("Tel: +420 777 123 456")
        
        assert len(result.findings) >= 1
        assert result.findings[0].metadata["phone_type"] == "mobile"

    def test_phone_edge_case_landline_prague(self, engine):
        result = engine.detect("Office: +420 2 1234 5678")
        
        assert len(result.findings) >= 1
        assert result.findings[0].metadata["phone_type"] == "landline"

    def test_phone_edge_case_without_country_code(self, engine):
        result = engine.detect("Mobile: 777 123 456")
        
        assert len(result.findings) >= 1

    def test_multiple_identifiers_same_line(self, engine):
        result = engine.detect("IČO: 25596641, RČ: 8001011238")
        
        assert len(result.findings) >= 2

    def test_overlapping_matches(self, engine):
        text = "DIČ: CZ25596641 contains IČO: 25596641"
        result = engine.detect(text)
        
        dic_findings = [f for f in result.findings if f.type == "dic"]
        ico_findings = [f for f in result.findings if f.type == "ico"]
        
        assert len(dic_findings) >= 1
        assert len(ico_findings) >= 1

    def test_empty_text(self, engine):
        result = engine.detect("")
        
        assert len(result.findings) == 0

    def test_text_with_no_pii(self, engine):
        result = engine.detect("Hello world, no personal information")
        
        assert len(result.findings) == 0

    def test_unicode_text(self, engine):
        result = engine.detect("Jan Novák Červený, RČ: 8001011238")
        
        assert len(result.findings) >= 1

    def test_long_text_performance(self, engine):
        long_text = "Jan Novák, RČ: 8001011238 " * 1000
        
        result = engine.detect(long_text)
        
        assert result.processing_time_ms < 2000
        assert len(result.findings) >= 1000

    def test_detector_specific_selection(self, engine):
        text = "IČO: 25596641, RČ: 8001011238"
        
        result = engine.detect(text, detector_names=["ico"])
        
        ico_findings = [f for f in result.findings if f.type == "ico"]
        rodne_cislo_findings = [f for f in result.findings if f.type == "rodne_cislo"]
        
        assert len(ico_findings) >= 1
        assert len(rodne_cislo_findings) == 0
