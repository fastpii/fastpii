"""Tests for PrivacyGuard redaction methods."""

from fastpii import PrivacyGuard


class TestPrivacyGuardAnonymize:
    """Test suite for anonymize() method."""

    def test_anonymize_basic(self):
        """Test basic anonymization."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Jan Novák, RČ: 8001011238, IČO: 25596641"
        
        result = guard.anonymize(text)
        
        assert "[REDACTED]" in result
        assert "8001011238" not in result
        assert "25596641" not in result

    def test_anonymize_with_custom_replacement(self):
        """Test anonymization with custom replacement."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Email: jan@email.cz"
        
        result = guard.anonymize(text, replacement="<PII>")
        
        assert result == "Email: <PII>"

    def test_anonymize_multiple_pii(self):
        """Test anonymization with multiple PII instances."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Email: jan@email.cz and RČ: 8001011238"
        
        result = guard.anonymize(text)
        
        # Both should be replaced
        assert "jan@email.cz" not in result
        assert "8001011238" not in result
        assert result.count("[REDACTED]") == 2

    def test_anonymize_no_pii(self):
        """Test anonymization with no PII."""
        guard = PrivacyGuard(regions=["cz"])
        text = "This is a normal text without PII"
        
        result = guard.anonymize(text)
        
        assert result == text

    def test_anonymize_empty_string(self):
        """Test anonymization with empty string."""
        guard = PrivacyGuard(regions=["cz"])
        
        result = guard.anonymize("")
        
        assert result == ""


class TestPrivacyGuardRedact:
    """Test suite for redact() method."""

    def test_redact_basic(self):
        """Test basic type-based redaction."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Email: jan@email.cz"
        
        result = guard.redact(text)
        
        assert result == "Email: [EMAIL]"
        assert "jan@email.cz" not in result

    def test_redact_multiple_types(self):
        """Test redaction with multiple PII types."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Email: jan@email.cz, RČ: 8001011238"
        
        result = guard.redact(text)
        
        assert "[EMAIL]" in result
        assert "[RODNE_CISLO]" in result
        assert "jan@email.cz" not in result
        assert "8001011238" not in result

    def test_redact_preserves_context(self):
        """Test that redaction preserves surrounding text."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Contact info at email: jan@email.cz for details"
        
        result = guard.redact(text)
        
        # Email should be replaced
        assert "jan@email.cz" not in result
        assert "[EMAIL]" in result
        
        # Surrounding text should be preserved
        assert result.endswith("for details")

    def test_redact_no_pii(self):
        """Test redaction with no PII."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Normal text without PII"
        
        result = guard.redact(text)
        
        assert result == text


class TestPrivacyGuardMask:
    """Test suite for mask() method."""

    def test_mask_basic(self):
        """Test basic masking with asterisks."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Email: jan@email.cz"
        
        result = guard.mask(text)
        
        # Should replace with asterisks
        assert "jan@email.cz" not in result
        assert result.startswith("Email: ")
        assert "*" in result
        # Length should match original PII length
        assert len(result) == len(text)

    def test_mask_preserves_length(self):
        """Test that masking preserves PII length."""
        guard = PrivacyGuard(regions=["cz"])
        text = "RČ: 8001011238"  # 10 digits
        
        result = guard.mask(text)
        
        # Count asterisks (should be 10 for rodné číslo)
        assert "*" * 10 in result
        assert "8001011238" not in result

    def test_mask_multiple_pii(self):
        """Test masking with multiple PII."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Email: jan@email.cz and info@test.cz"
        
        result = guard.mask(text)
        
        # Both emails should be masked
        assert "jan@email.cz" not in result
        assert "info@test.cz" not in result
        assert "*" in result


class TestPrivacyGuardRemove:
    """Test suite for remove() method."""

    def test_remove_basic(self):
        """Test basic PII removal."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Email: jan@email.cz"
        
        result = guard.remove(text)
        
        assert result == "Email: "
        assert "jan@email.cz" not in result

    def test_remove_multiple_pii(self):
        """Test removal of multiple PII."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Email: jan@email.cz and RČ: 8001011238"
        
        result = guard.remove(text)
        
        assert "jan@email.cz" not in result
        assert "8001011238" not in result
        assert "and" in result

    def test_remove_preserves_structure(self):
        """Test that removal preserves text structure."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Contact: jan@email.cz, Phone: 8001011238"
        
        result = guard.remove(text)
        
        assert result.startswith("Contact:")
        assert result.endswith(", Phone: ")
        assert "jan@email.cz" not in result
        assert "8001011238" not in result


class TestPrivacyGuardRedactionMethodsComparison:
    """Compare different redaction methods."""

    def test_all_methods_work_on_same_text(self):
        """Test that all redaction methods work on same input."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Email: jan@email.cz, RČ: 8001011238"
        
        anonymized = guard.anonymize(text)
        redacted = guard.redact(text)
        masked = guard.mask(text)
        removed = guard.remove(text)
        
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

    def test_methods_with_czech_domain_email(self):
        """Test redaction methods with Czech domain emails."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Kontakt: novak@firma.cz"
        
        anonymized = guard.anonymize(text)
        redacted = guard.redact(text)
        masked = guard.mask(text)
        removed = guard.remove(text)
        
        assert "novak@firma.cz" not in anonymized
        assert "novak@firma.cz" not in redacted
        assert "novak@firma.cz" not in masked
        assert "novak@firma.cz" not in removed

    def test_methods_with_international_email(self):
        """Test redaction methods with international domains."""
        guard = PrivacyGuard(regions=["cz"])
        text = "Email: user@gmail.com"
        
        anonymized = guard.anonymize(text)
        redacted = guard.redact(text)
        
        assert "user@gmail.com" not in anonymized
        assert "[EMAIL]" in redacted