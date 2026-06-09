"""Tests for EmailDetector."""

from fastpii.models import Finding
from fastpii.detectors.cz.email import EmailDetector


class TestEmailDetector:
    """Test suite for EmailDetector."""

    def test_detector_creation(self):
        """Test detector initialization."""
        detector = EmailDetector()

        assert detector.name == "email"
        assert detector.region == "cz"
        assert "Czech domain awareness" in detector.description

    def test_detect_basic_email(self):
        """Test detection of basic email address."""
        detector = EmailDetector()
        text = "Contact: john@example.com"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "email"
        assert findings[0].value == "john@example.com"
        assert findings[0].confidence >= 0.85

    def test_detect_czech_domain_cz(self):
        """Test detection of Czech .cz domain."""
        detector = EmailDetector()
        text = "Email: novak@firma.cz"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "novak@firma.cz"
        assert findings[0].region == "cz"
        assert findings[0].confidence >= 0.95
        assert findings[0].metadata["is_czech_domain"] is True

    def test_detect_czech_domain_sk(self):
        """Test detection of Slovak .sk domain."""
        detector = EmailDetector()
        text = "Email: jan@spolecnost.sk"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "jan@spolecnost.sk"
        assert findings[0].region == "cz"
        assert findings[0].confidence >= 0.95
        assert findings[0].metadata["is_czech_domain"] is True

    def test_detect_generic_domain(self):
        """Test detection of generic domain."""
        detector = EmailDetector()
        text = "Contact: user@gmail.com"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "user@gmail.com"
        assert findings[0].region == "generic"
        assert findings[0].confidence >= 0.85

    def test_detect_multiple_emails(self):
        """Test detection of multiple emails in text."""
        detector = EmailDetector()
        text = "Contact: jan@email.cz or support@firma.cz or info@gmail.com"

        findings = detector.detect(text)

        assert len(findings) == 3
        emails = [f.value for f in findings]
        assert "jan@email.cz" in emails
        assert "support@firma.cz" in emails
        assert "info@gmail.com" in emails

    def test_metadata_gmail_provider(self):
        """Test provider detection for Gmail."""
        detector = EmailDetector()
        text = "user@gmail.com"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].metadata["provider"] == "gmail"
        assert findings[0].metadata["domain"] == "gmail.com"
        assert findings[0].metadata["local_part"] == "user"

    def test_metadata_seznam_provider(self):
        """Test provider detection for Seznam."""
        detector = EmailDetector()
        text = "novak@seznam.cz"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].metadata["provider"] == "seznam"

    def test_metadata_centrum_provider(self):
        """Test provider detection for Centrum."""
        detector = EmailDetector()
        text = "user@centrum.cz"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].metadata["provider"] == "centrum"

    def test_metadata_email_cz_provider(self):
        """Test provider detection for Email.cz."""
        detector = EmailDetector()
        text = "user@email.cz"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].metadata["provider"] == "email"

    def test_metadata_microsoft_provider(self):
        """Test provider detection for Microsoft."""
        detector = EmailDetector()
        
        # Test Outlook
        findings = detector.detect("user@outlook.com")
        assert len(findings) == 1
        assert findings[0].metadata["provider"] == "microsoft"
        
        # Test Hotmail
        findings = detector.detect("user@hotmail.com")
        assert len(findings) == 1
        assert findings[0].metadata["provider"] == "microsoft"
        
        # Test Live
        findings = detector.detect("user@live.com")
        assert len(findings) == 1
        assert findings[0].metadata["provider"] == "microsoft"

    def test_metadata_yahoo_provider(self):
        """Test provider detection for Yahoo."""
        detector = EmailDetector()
        text = "user@yahoo.com"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].metadata["provider"] == "yahoo"

    def test_metadata_unknown_provider(self):
        """Test metadata for unknown provider."""
        detector = EmailDetector()
        text = "user@unknown-domain.cz"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert "provider" not in findings[0].metadata

    def test_validate_valid_email(self):
        """Test validation of valid email."""
        detector = EmailDetector()

        assert detector.validate("user@example.com") is True
        assert detector.validate("test@domain.cz") is True
        assert detector.validate("user.name@company.sk") is True

    def test_validate_invalid_email_no_at(self):
        """Test validation of email without @."""
        detector = EmailDetector()

        assert detector.validate("userexample.com") is False

    def test_validate_invalid_email_double_at(self):
        """Test validation of email with double @."""
        detector = EmailDetector()

        assert detector.validate("user@@example.com") is False

    def test_validate_invalid_email_empty_local(self):
        """Test validation of email with empty local part."""
        detector = EmailDetector()

        assert detector.validate("@example.com") is False

    def test_validate_invalid_email_empty_domain(self):
        """Test validation of email with empty domain."""
        detector = EmailDetector()

        assert detector.validate("user@") is False

    def test_validate_invalid_email_no_dot(self):
        """Test validation of email without dot in domain."""
        detector = EmailDetector()

        assert detector.validate("user@example") is False

    def test_validate_invalid_email_consecutive_dots(self):
        """Test validation of email with consecutive dots."""
        detector = EmailDetector()

        assert detector.validate("user@ex..ample.com") is False

    def test_validate_invalid_email_too_long_local(self):
        """Test validation of email with too long local part."""
        detector = EmailDetector()
        long_local = "a" * 65  # 65 chars, max is 64
        email = f"{long_local}@example.com"

        assert detector.validate(email) is False

    def test_validate_invalid_email_too_long_domain(self):
        """Test validation of email with too long domain."""
        detector = EmailDetector()
        long_domain = "a" * 256  # 256 chars, max is 255
        email = f"user@{long_domain}.com"

        assert detector.validate(email) is False

    def test_detect_with_special_characters(self):
        """Test detection with valid special characters."""
        detector = EmailDetector()
        text = "Emails: user+tag@example.com, first.last@domain.cz"

        findings = detector.detect(text)

        assert len(findings) == 2
        emails = [f.value for f in findings]
        assert "user+tag@example.com" in emails
        assert "first.last@domain.cz" in emails

    def test_detect_in_complex_text(self):
        """Test detection in complex text with other PII."""
        detector = EmailDetector()
        text = """
        Contact Jan Novák at jan.novak@firma.cz
        Personal ID: 8001011238
        Phone: +420777888999
        Alternative: novak@seznam.cz
        """

        findings = detector.detect(text)

        assert len(findings) == 2
        emails = [f.value for f in findings]
        assert "jan.novak@firma.cz" in emails
        assert "novak@seznam.cz" in emails

    def test_detect_case_insensitive(self):
        """Test case-insensitive detection."""
        detector = EmailDetector()
        text = "Email: User@Example.COM"

        findings = detector.detect(text)

        assert len(findings) == 1
        # The detector should preserve original case
        assert "User@Example.COM" in findings[0].value

    def test_metadata_domain_lowercased(self):
        """Test that domain in metadata is lowercased."""
        detector = EmailDetector()
        text = "User@Example.COM"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].metadata["domain"] == "example.com"

    def test_no_false_positives_urls(self):
        """Test that URLs are not detected as emails."""
        detector = EmailDetector()
        text = "Visit https://example.com/page"

        findings = detector.detect(text)

        # Should not detect anything (URL is not email)
        assert len(findings) == 0

    def test_no_false_positives_text(self):
        """Test that regular text doesn't trigger false positives."""
        detector = EmailDetector()
        text = "This is not an email but has at sign @ and dot . but no match"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_edge_case_email_with_numbers(self):
        """Test email with numbers in local part and domain."""
        detector = EmailDetector()
        text = "user123@domain456.cz"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "user123@domain456.cz"

    def test_edge_case_subdomain(self):
        """Test email with subdomain."""
        detector = EmailDetector()
        text = "user@mail.company.cz"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "user@mail.company.cz"
        assert findings[0].metadata["is_czech_domain"] is True