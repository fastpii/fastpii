import pytest

from fastpii.detectors.cz.rodne_cislo import RodneCisloDetector


class TestRodneCisloDetector:
    def test_detector_creation(self):
        detector = RodneCisloDetector()

        assert detector.name == "rodne_cislo"
        assert detector.region == "cz"
        assert "Czech birth number" in detector.description

    def test_detect_10_digit_rodne_cislo(self):
        detector = RodneCisloDetector()
        text = "Jan Novák, RČ: 8001011238"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "rodne_cislo"
        assert findings[0].value == "8001011238"
        assert findings[0].region == "cz"
        assert findings[0].confidence >= 0.95

    def test_detect_9_digit_rodne_cislo(self):
        detector = RodneCisloDetector()
        text = "Born before 1954: 530201123"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "530201123"

    def test_detect_with_slash_separator(self):
        detector = RodneCisloDetector()
        text = "RČ: 800101/1238"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert "800101" in findings[0].value
        assert "1238" in findings[0].value

    def test_detect_near_valid_10_digit(self):
        """Near-valid: format matches, checksum fails, should still be detected with lower confidence."""
        detector = RodneCisloDetector()
        text = "RČ: 8001011235"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].confidence == pytest.approx(0.70)
        assert findings[0].metadata["checksum_valid"] is False

    def test_near_valid_without_context(self):
        """Near-valid without context words should still be detected."""
        detector = RodneCisloDetector()
        text = "8001011235"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].confidence == pytest.approx(0.65)

    def test_valid_with_context_boost(self):
        """Valid checksum + context words → confidence boosted."""
        detector = RodneCisloDetector()
        text = "RČ: 8001011238"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].confidence >= 0.95

    def test_near_valid_with_context_boost(self):
        """Near-valid + context words → confidence boosted."""
        detector = RodneCisloDetector()
        text = "rodné číslo: 8001011235"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].confidence == pytest.approx(0.70)

    def test_valid_without_context(self):
        """Valid checksum without context → base confidence."""
        detector = RodneCisloDetector()
        text = "8001011238"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].confidence == pytest.approx(0.90)

    def test_validate_valid_10_digit(self):
        detector = RodneCisloDetector()

        valid = detector.validate("8001011238")

        assert valid is True

    def test_validate_invalid_10_digit_checksum(self):
        detector = RodneCisloDetector()

        valid = detector.validate("8001011235")

        assert valid is False

    def test_validate_valid_9_digit(self):
        detector = RodneCisloDetector()

        valid = detector.validate("530201123")

        assert valid is True

    def test_extract_metadata_birth_date(self):
        detector = RodneCisloDetector()
        text = "RČ: 8001011238"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert "birth_date" in findings[0].metadata
        assert findings[0].metadata["birth_date"] == "1980-01-01"

    def test_extract_metadata_gender_male(self):
        detector = RodneCisloDetector()
        text = "RČ: 8001011238"

        findings = detector.detect(text)

        assert findings[0].metadata["gender"] == "male"

    def test_extract_metadata_gender_female(self):
        detector = RodneCisloDetector()
        text = "RČ: 8051011232"

        findings = detector.detect(text)

        assert findings[0].metadata["gender"] == "female"

    def test_extracts_article_nine_flag(self):
        detector = RodneCisloDetector()
        text = "RČ: 8001011238"

        findings = detector.detect(text)

        assert "article_9" in findings[0].metadata
        assert findings[0].metadata["article_9"] is True

    def test_checksum_valid_metadata_true(self):
        """Valid checksum should have checksum_valid=True in metadata."""
        detector = RodneCisloDetector()
        text = "RČ: 8001011238"

        findings = detector.detect(text)

        assert findings[0].metadata["checksum_valid"] is True

    def test_checksum_valid_metadata_false(self):
        """Invalid checksum should have checksum_valid=False in metadata."""
        detector = RodneCisloDetector()
        text = "RČ: 8001011235"

        findings = detector.detect(text)

        assert findings[0].metadata["checksum_valid"] is False

    def test_checksum_valid_metadata_none_for_9digit(self):
        """9-digit pre-1954 should have checksum_valid=None."""
        detector = RodneCisloDetector()
        text = "530201123"

        findings = detector.detect(text)

        assert findings[0].metadata["checksum_valid"] is None

    def test_invalid_date_not_detected(self):
        """Numbers with invalid dates should NOT be detected at all."""
        detector = RodneCisloDetector()
        text = "RČ: 9913450000"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_completely_invalid_not_detected(self):
        """Random digit sequences that aren't valid RC format should not be detected."""
        detector = RodneCisloDetector()
        text = "12345678"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_9_digit_with_context_boost(self):
        """9-digit with context words should get boosted confidence."""
        detector = RodneCisloDetector()
        text = "RČ: 530201123"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].confidence >= 0.90

    def test_no_detection_in_clean_text(self):
        detector = RodneCisloDetector()
        text = "Hello world, no PII here"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_multiple_rodne_cislo_in_text(self):
        detector = RodneCisloDetector()
        text = "First person: 8001011238, Second: 810201560"

        findings = detector.detect(text)

        assert len(findings) == 2
