import pytest

from fastpii import PrivacyGuard


class TestCzechDetectorEdgeCases:
    def test_rodne_cislo_edge_case_9_digit(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("Born before 1954: 530201123")
        
        assert len(result.findings) >= 1
        assert result.findings[0].value == "530201123"

    def test_rodne_cislo_edge_case_female(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("Female: 8051011232")
        
        assert len(result.findings) >= 1
        assert result.findings[0].metadata["gender"] == "female"

    def test_rodne_cislo_edge_case_invalid_checksum(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.validate("8001011235", detector_name="rodne_cislo")
        
        assert result.is_valid is False

    def test_rodne_cislo_edge_case_with_slash(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("RČ: 800101/1238")
        
        assert len(result.findings) >= 1

    def test_rodne_cislo_edge_case_without_slash(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("RČ: 8001011238")
        
        assert len(result.findings) >= 1
        assert "800101" in result.findings[0].value

    def test_ico_edge_case_25596641(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.validate("25596641", detector_name="ico")
        
        assert result.is_valid is True

    def test_ico_edge_case_leading_zeros(self):
        guard = PrivacyGuard(regions=["cz"])
        result = guard.detect("IČO: 00000019")

        assert len(result.findings) >= 1
        assert result.findings[0].value == "00000019"

    def test_ico_edge_case_invalid_checksum(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.validate("12345678", detector_name="ico")
        
        assert result.is_valid is False

    def test_dic_edge_case_company(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.validate("CZ25596641", detector_name="dic")
        
        assert result.is_valid is True

    def test_dic_edge_case_individual(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.validate("CZ8001011238", detector_name="dic")
        
        assert result.is_valid is True

    def test_dic_edge_case_special(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.validate("CZ612345678", detector_name="dic")
        
        assert result.is_valid is True

    def test_bank_account_edge_case_without_prefix(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("Account: 2000145399/0800")
        
        assert len(result.findings) >= 1

    def test_bank_account_edge_case_with_prefix(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("Account: 19-2000145399/0800")
        
        assert len(result.findings) >= 1

    def test_bank_account_edge_case_invalid_checksum(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.validate("19-12/0800", detector_name="bank_account")
        
        assert result.is_valid is False

    def test_postal_code_edge_case_prague(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("PSČ: 110 00")
        
        assert len(result.findings) >= 1
        assert result.findings[0].value == "110 00"

    def test_postal_code_edge_case_without_space(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("PSČ: 11000")
        
        assert len(result.findings) >= 1
        assert "110" in result.findings[0].value

    def test_postal_code_edge_case_range_validation(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.validate("099 99", detector_name="postal_code")
        
        assert result.is_valid is False

    def test_phone_edge_case_mobile_with_country_code(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("Tel: +420 777 123 456")
        
        assert len(result.findings) >= 1
        assert result.findings[0].metadata["phone_type"] == "mobile"

    def test_phone_edge_case_landline_prague(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("Office: +420 2 1234 5678")
        
        assert len(result.findings) >= 1
        assert result.findings[0].metadata["phone_type"] == "landline"

    def test_phone_edge_case_without_country_code(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("Mobile: 777 123 456")
        
        assert len(result.findings) >= 1

    def test_multiple_identifiers_same_line(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("IČO: 25596641, RČ: 8001011238")
        
        assert len(result.findings) >= 2

    def test_overlapping_matches(self):
        gateway = PrivacyGuard(regions=["cz"])
        text = "DIČ: CZ25596641 contains IČO: 25596641"
        result = gateway.detect(text)
        
        dic_findings = [f for f in result.findings if f.type == "dic"]
        ico_findings = [f for f in result.findings if f.type == "ico"]
        
        assert len(dic_findings) >= 1
        assert len(ico_findings) >= 1

    def test_empty_text(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("")
        
        assert len(result.findings) == 0

    def test_text_with_no_pii(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("Hello world, no personal information")
        
        assert len(result.findings) == 0

    def test_unicode_text(self):
        gateway = PrivacyGuard(regions=["cz"])
        result = gateway.detect("Jan Novák Červený, RČ: 8001011238")
        
        assert len(result.findings) >= 1

    def test_long_text_performance(self):
        gateway = PrivacyGuard(regions=["cz"])
        long_text = "Jan Novák, RČ: 8001011238 " * 1000
        
        result = gateway.detect(long_text)
        
        assert result.processing_time_ms < 1000
        assert len(result.findings) >= 1000

    def test_detector_specific_selection(self):
        gateway = PrivacyGuard(regions=["cz"])
        text = "IČO: 25596641, RČ: 8001011238"
        
        result = gateway.detect(text, detector_names=["ico"])
        
        ico_findings = [f for f in result.findings if f.type == "ico"]
        rodne_cislo_findings = [f for f in result.findings if f.type == "rodne_cislo"]
        
        assert len(ico_findings) >= 1
        assert len(rodne_cislo_findings) == 0