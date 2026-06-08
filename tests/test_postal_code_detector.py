import pytest

from fastpii.models import Finding
from fastpii.detectors.cz.postal_code import PostalCodeDetector


class TestPostalCodeDetector:
    def test_detector_creation(self):
        detector = PostalCodeDetector()

        assert detector.name == "postal_code"
        assert detector.region == "cz"
        assert "Czech postal code" in detector.description

    def test_detect_postal_code_with_space(self):
        detector = PostalCodeDetector()
        text = "Praha 1, PSČ: 110 00"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "postal_code"
        assert findings[0].value == "110 00"
        assert findings[0].region == "cz"
        assert findings[0].confidence >= 0.95

    def test_detect_postal_code_without_space(self):
        detector = PostalCodeDetector()
        text = "PSČ: 11000"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "11000"

    def test_validate_valid_postal_code(self):
        detector = PostalCodeDetector()

        assert detector.validate("110 00") is True
        assert detector.validate("11000") is True
        assert detector.validate("186 00") is True

    def test_validate_invalid_postal_code(self):
        detector = PostalCodeDetector()

        assert detector.validate("12345") is False
        assert detector.validate("1234") is False
        assert detector.validate("123456") is False

    def test_detect_multiple_postal_codes(self):
        detector = PostalCodeDetector()
        text = "Contact us at 110 00 Praha or 602 00 Brno"

        findings = detector.detect(text)

        assert len(findings) == 2

    def test_no_detection_in_clean_text(self):
        detector = PostalCodeDetector()
        text = "No postal codes here"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_postal_code_range_validation(self):
        detector = PostalCodeDetector()

        assert detector.validate("100 00") is True
        assert detector.validate("999 99") is True
        assert detector.validate("099 99") is False

    def test_extracts_metadata(self):
        detector = PostalCodeDetector()
        text = "PSČ: 110 00"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert "region" in findings[0].metadata
        assert findings[0].metadata["region"] in ["Praha", "Středočeský", "other"]