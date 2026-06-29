"""Comprehensive tests for FastPII redaction with all detector types."""

import pytest

from fastpii import FastPII, DEFAULT_PRIORITY, DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.cz import CzechPack


class TestFastPIIRedactionAllDetectors:
    """Test redaction methods work for all registered detectors."""

    @pytest.fixture
    def engine(self):
        """Create FastPII instance with Czech detectors registered."""
        guard = FastPII(
            priority=DEFAULT_PRIORITY,
            confidence_scorer=ConfidenceScorer(
                base_scores=DEFAULT_CONFIDENCE_SCORES,
                context_boost=DEFAULT_CONTEXT_BOOST,
            ),
        )
        guard.register(CzechPack())
        return guard

    @pytest.mark.parametrize("text,pii_type,pii_value", [
        # Rodné číslo
        ("RČ: 8001011238", "RODNE_CISLO", "8001011238"),
        
        # IČO (Company ID) - use format that detector recognizes
        ("IČO: 25596641", "ICO", "25596641"),
        
        # Postal Code (PSČ)
        ("PSČ: 11000", "POSTAL_CODE", "11000"),
        
        # Phone Number
        ("Tel: +420777888999", "PHONE", "+420777888999"),
        
        # Email Address
        ("Email: jan@email.cz", "EMAIL", "jan@email.cz"),
    ])
    def test_redact_all_detector_types(self, engine, text, pii_type, pii_value):
        """Test redaction works for each detector type."""
        redacted = engine.redact(text)
        
        # PII value should be removed
        assert pii_value not in redacted, f"PII {pii_value} still present in: {redacted}"
        
        # Type placeholder should be present  
        assert f"[{pii_type}]" in redacted, f"[{pii_type}] not found in: {redacted}"

    @pytest.mark.parametrize("text,pii_type,pii_value", [
        ("RČ: 8001011238", "RODNE_CISLO", "8001011238"),
        ("IČO: 25596641", "ICO", "25596641"),
        ("PSČ: 11000", "POSTAL_CODE", "11000"),
        ("Tel: +420777888999", "PHONE", "+420777888999"),
        ("Email: jan@email.cz", "EMAIL", "jan@email.cz"),
    ])
    def test_anonymize_all_detector_types(self, engine, text, pii_type, pii_value):
        """Test anonymization works for each detector type."""
        anonymized = engine.anonymize(text)
        
        # PII value should be removed
        assert f"{pii_value}" not in anonymized
        
        # Generic placeholder should be present
        assert "[REDACTED]" in anonymized

    @pytest.mark.parametrize("text,pii_value", [
        ("RČ: 8001011238", "8001011238"),
        ("IČO: 25596641", "25596641"),
        ("Email: jan@email.cz", "jan@email.cz"),
    ])
    def test_mask_all_detector_types(self, engine, text, pii_value):
        """Test masking works for each detector type."""
        masked = engine.mask(text)
        
        # PII value should be masked
        assert pii_value not in masked
        
        # Asterisks should be present
        assert "*" in masked
        
        # Result should be same length or longer (due to masking keeping length)
        # Actually masking replaces PII with asterisks of same length
        # So total length should be preserved
        original_pii_length = len(pii_value)
        asterisk_count = masked.count("*")
        assert asterisk_count >= original_pii_length  # At least as many asterisks as PII length

    @pytest.mark.parametrize("text,pii_value", [
        ("RČ: 8001011238", "8001011238"),
        ("IČO: 25596641", "25596641"),
        ("Email: jan@email.cz", "jan@email.cz"),
    ])
    def test_remove_all_detector_types(self, engine, text, pii_value):
        """Test removal works for each detector type."""
        removed = engine.remove(text)
        
        # PII value should be completely removed
        assert pii_value not in removed

    def test_redact_multiple_different_pii_types(self, engine):
        """Test redaction handles multiple PII of different types."""
        text = "Email: jan@email.cz, IČO: 25596641, RČ: 8001011238"
        
        redacted = engine.redact(text)
        
        # All PII should be replaced
        assert "jan@email.cz" not in redacted
        assert "25596641" not in redacted
        assert "8001011238" not in redacted
        
        # Type placeholders should be present
        assert "[EMAIL]" in redacted
        assert "[ICO]" in redacted
        assert "[RODNE_CISLO]" in redacted

    def test_anonymize_multiple_pii_of_same_type(self, engine):
        """Test anonymization handles multiple PII of same type."""
        text = "Emails: jan@email.cz and info@firma.cz"
        
        anonymized = engine.anonymize(text)
        
        # Both emails should be anonymized
        assert "jan@email.cz" not in anonymized
        assert "info@firma.cz" not in anonymized
        
        # Should have generic placeholders
        assert "[REDACTED]" in anonymized
        # Multiple instances should result in multiple placeholders
        assert anonymized.count("[REDACTED]") == 2

    def test_redact_preserves_text_structure(self, engine):
        """Test that redaction preserves surrounding text."""
        text = "Contact info at email: jan@email.cz for more details"
        
        redacted = engine.redact(text)
        
        # Email should be replaced
        assert "jan@email.cz" not in redacted
        assert "[EMAIL]" in redacted
        
        # Surrounding text should be preserved
        assert redacted.endswith("for more details")

    def test_no_pii_detection_no_modification(self, engine):
        """Test that text without PII is not modified."""
        text = "This is normal text without any PII data"
        
        redacted = engine.redact(text)
        anonymized = engine.anonymize(text)
        masked = engine.mask(text)
        removed = engine.remove(text)
        
        # All should return original text
        assert redacted == text
        assert anonymized == text
        assert masked == text
        assert removed == text

    def test_empty_string_handling(self, engine):
        """Test that all methods handle empty strings correctly."""
        text = ""
        
        redacted = engine.redact(text)
        anonymized = engine.anonymize(text)
        masked = engine.mask(text)
        removed = engine.remove(text)
        
        # All should return empty string
        assert redacted == ""
        assert anonymized == ""
        assert masked == ""
        assert removed == ""

    def test_custom_replacement_in_anonymize(self, engine):
        """Test anonymize with custom replacement string."""
        text = "Email: jan@email.cz"
        
        result = engine.anonymize(text, replacement="<PII_REMOVED>")
        
        assert "jan@email.cz" not in result
        assert "<PII_REMOVED>" in result

    def test_czech_domain_email_higher_confidence(self, engine):
        """Test that Czech domain emails get proper redaction."""
        text = "Kontakt: novak@firma.cz"
        
        result = engine.detect(text)
        
        assert len(result.findings) == 1
        assert result.findings[0].type == "email"
        # Czech domain should have higher confidence
        assert result.findings[0].confidence >= 0.95
        
        # Redaction should still work
        redacted = engine.redact(text)
        assert "[EMAIL]" in redacted
        assert "novak@firma.cz" not in redacted
