"""Tests for FastPII redaction methods."""

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


class TestFastPIIAnonymize:
    """Test suite for anonymize() method."""

    def test_anonymize_basic(self, engine):
        """Test basic anonymization."""
        text = "Jan Novák, RČ: 8001011238, IČO: 25596641"
        
        result = engine.anonymize(text)
        
        assert "[REDACTED]" in result
        assert "8001011238" not in result
        assert "25596641" not in result

    def test_anonymize_with_custom_replacement(self, engine):
        """Test anonymization with custom replacement."""
        text = "Email: jan@email.cz"
        
        result = engine.anonymize(text, replacement="<PII>")
        
        assert result == "Email: <PII>"

    def test_anonymize_multiple_pii(self, engine):
        """Test anonymization with multiple PII instances."""
        text = "Email: jan@email.cz and RČ: 8001011238"
        
        result = engine.anonymize(text)
        
        # Both should be replaced
        assert "jan@email.cz" not in result
        assert "8001011238" not in result
        assert result.count("[REDACTED]") == 2

    def test_anonymize_no_pii(self, engine):
        """Test anonymization with no PII."""
        text = "This is a normal text without PII"
        
        result = engine.anonymize(text)
        
        assert result == text

    def test_anonymize_empty_string(self, engine):
        """Test anonymization with empty string."""
        
        result = engine.anonymize("")
        
        assert result == ""


class TestFastPIIRedact:
    """Test suite for redact() method."""

    def test_redact_basic(self, engine):
        """Test basic type-based redaction."""
        text = "Email: jan@email.cz"
        
        result = engine.redact(text)
        
        assert result == "Email: [EMAIL]"
        assert "jan@email.cz" not in result

    def test_redact_multiple_types(self, engine):
        """Test redaction with multiple PII types."""
        text = "Email: jan@email.cz, RČ: 8001011238"
        
        result = engine.redact(text)
        
        assert "[EMAIL]" in result
        assert "[RODNE_CISLO]" in result
        assert "jan@email.cz" not in result
        assert "8001011238" not in result

    def test_redact_preserves_context(self, engine):
        """Test that redaction preserves surrounding text."""
        text = "Contact info at email: jan@email.cz for details"
        
        result = engine.redact(text)
        
        # Email should be replaced
        assert "jan@email.cz" not in result
        assert "[EMAIL]" in result
        
        # Surrounding text should be preserved
        assert result.endswith("for details")

    def test_redact_no_pii(self, engine):
        """Test redaction with no PII."""
        text = "Normal text without PII"
        
        result = engine.redact(text)
        
        assert result == text


class TestFastPIIMask:
    """Test suite for mask() method."""

    def test_mask_basic(self, engine):
        """Test basic masking with asterisks."""
        text = "Email: jan@email.cz"
        
        result = engine.mask(text)
        
        # Should replace with asterisks
        assert "jan@email.cz" not in result
        assert result.startswith("Email: ")
        assert "*" in result
        # Length should match original PII length
        assert len(result) == len(text)

    def test_mask_preserves_length(self, engine):
        """Test that masking preserves PII length."""
        text = "RČ: 8001011238"  # 10 digits
        
        result = engine.mask(text)
        
        # Count asterisks (should be 10 for rodné číslo)
        assert "*" * 10 in result
        assert "8001011238" not in result

    def test_mask_multiple_pii(self, engine):
        """Test masking with multiple PII."""
        text = "Email: jan@email.cz and info@test.cz"
        
        result = engine.mask(text)
        
        # Both emails should be masked
        assert "jan@email.cz" not in result
        assert "info@test.cz" not in result
        assert "*" in result


class TestFastPIIRemove:
    """Test suite for remove() method."""

    def test_remove_basic(self, engine):
        """Test basic PII removal."""
        text = "Email: jan@email.cz"
        
        result = engine.remove(text)
        
        assert result == "Email: "
        assert "jan@email.cz" not in result

    def test_remove_multiple_pii(self, engine):
        """Test removal of multiple PII."""
        text = "Email: jan@email.cz and RČ: 8001011238"
        
        result = engine.remove(text)
        
        assert "jan@email.cz" not in result
        assert "8001011238" not in result
        assert "and" in result

    def test_remove_preserves_structure(self, engine):
        """Test that removal preserves text structure."""
        text = "Contact: jan@email.cz, Phone: 8001011238"
        
        result = engine.remove(text)
        
        assert result.startswith("Contact:")
        assert result.endswith(", Phone: ")
        assert "jan@email.cz" not in result
        assert "8001011238" not in result


class TestFastPIIRedactionMethodsComparison:
    """Compare different redaction methods."""

    def test_all_methods_work_on_same_text(self, engine):
        """Test that all redaction methods work on same input."""
        text = "Email: jan@email.cz, RČ: 8001011238"
        
        anonymized = engine.anonymize(text)
        redacted = engine.redact(text)
        masked = engine.mask(text)
        removed = engine.remove(text)
        
        # All should remove PII
        assert "jan@email.cz" not in anonymized
        assert "jan@email.cz" not in redacted
        assert "jan@email.cz" not in masked
        assert "jan@email.cz" not in removed
        
        assert "8001011238" not in anonymized
        assert "8001011238" not in redacted
        assert "8001011238" not in masked
        assert "8001011238" not in removed
        
        # Redact should have type names
        assert "[EMAIL]" in redacted
        assert "[RODNE_CISLO]" in redacted
        
        # Anonymize should have generic placeholder
        assert "[REDACTED]" in anonymized

    def test_methods_with_czech_domain_email(self, engine):
        """Test redaction methods with Czech domain emails."""
        text = "Kontakt: novak@firma.cz"
        
        anonymized = engine.anonymize(text)
        redacted = engine.redact(text)
        masked = engine.mask(text)
        removed = engine.remove(text)
        
        assert "novak@firma.cz" not in anonymized
        assert "novak@firma.cz" not in redacted
        assert "novak@firma.cz" not in masked
        assert "novak@firma.cz" not in removed

    def test_methods_with_international_email(self, engine):
        """Test redaction methods with international domains."""
        text = "Email: user@gmail.com"
        
        anonymized = engine.anonymize(text)
        redacted = engine.redact(text)
        
        assert "user@gmail.com" not in anonymized
        assert "[EMAIL]" in redacted
