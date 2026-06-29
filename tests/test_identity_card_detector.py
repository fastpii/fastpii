from fastpii.detectors.cz.identity_card import IdentityCardDetector


class TestIdentityCardDetector:
    def test_detector_creation(self):
        detector = IdentityCardDetector()

        assert detector.name == "identity_card"
        assert detector.region == "cz"
        assert "identity card" in detector.description.lower()

    def test_detect_new_format_with_context(self):
        detector = IdentityCardDetector()
        text = "občanský průkaz: 123456789"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].type == "identity_card"
        assert findings[0].value == "123456789"
        assert findings[0].metadata["format"] == "new"

    def test_detect_old_format_with_context(self):
        detector = IdentityCardDetector()
        text = "č. průkazu: 123456AB"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].value == "123456AB"
        assert findings[0].metadata["format"] == "old"
        assert findings[0].metadata["series"] == "AB"

    def test_detect_with_op_context(self):
        detector = IdentityCardDetector()
        text = "OP 123456789"

        findings = detector.detect(text)

        assert len(findings) >= 1

    def test_detect_without_context(self):
        detector = IdentityCardDetector()
        text = "123456789"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].confidence == 0.70

    def test_old_format_higher_confidence_without_context(self):
        detector = IdentityCardDetector()
        text = "123456AB"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].confidence == 0.85

    def test_rejects_leading_zero(self):
        detector = IdentityCardDetector()
        text = "občanský průkaz: 023456789"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_validate_valid_new_format(self):
        detector = IdentityCardDetector()

        assert detector.validate("123456789") is True

    def test_validate_valid_old_format(self):
        detector = IdentityCardDetector()

        assert detector.validate("123456AB") is True

    def test_validate_rejects_leading_zero(self):
        detector = IdentityCardDetector()

        assert detector.validate("023456789") is False

    def test_validate_rejects_invalid_format(self):
        detector = IdentityCardDetector()

        assert detector.validate("") is False
        assert detector.validate("abc") is False
        assert detector.validate("12345") is False
        assert detector.validate("12345678901") is False

    def test_no_detection_in_clean_text(self):
        detector = IdentityCardDetector()
        text = "No identity card numbers here"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_context_boosts_confidence(self):
        detector = IdentityCardDetector()
        text_with_context = "občanský průkaz 123456789"
        text_without_context = "123456789"

        findings_with = detector.detect(text_with_context)
        findings_without = detector.detect(text_without_context)

        assert len(findings_with) >= 1
        assert len(findings_without) >= 1
        assert findings_with[0].confidence > findings_without[0].confidence

    def test_metadata_new_format(self):
        detector = IdentityCardDetector()
        text = "občanský průkaz: 123456789"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].metadata["format"] == "new"
        assert findings[0].metadata["number"] == "123456789"

    def test_metadata_old_format(self):
        detector = IdentityCardDetector()
        text = "č. průkazu: 123456AB"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].metadata["format"] == "old"
        assert findings[0].metadata["series"] == "AB"

    def test_multiple_cards_in_text(self):
        detector = IdentityCardDetector()
        text = "OP: 123456789 a starý průkaz 654321CD"

        findings = detector.detect(text)

        assert len(findings) >= 2