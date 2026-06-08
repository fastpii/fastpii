import pytest

from cpg.models import Finding
from cpg.detectors.cz.phone import PhoneNumberDetector


class TestPhoneNumberDetector:
    def test_detector_creation(self):
        detector = PhoneNumberDetector()

        assert detector.name == "phone"
        assert detector.region == "cz"
        assert "Czech phone number" in detector.description

    def test_detect_mobile_with_country_code(self):
        detector = PhoneNumberDetector()
        text = "Call me at +420 777 123 456"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].type == "phone"
        assert findings[0].region == "cz"

    def test_detect_mobile_without_country_code(self):
        detector = PhoneNumberDetector()
        text = "Number: 777 123 456"

        findings = detector.detect(text)

        assert len(findings) >= 1

    def test_detect_landline_prague(self):
        detector = PhoneNumberDetector()
        text = "Office: +420 2 1234 5678"

        findings = detector.detect(text)

        assert len(findings) >= 1

    def test_validate_valid_mobile(self):
        detector = PhoneNumberDetector()

        assert detector.validate("+420777123456") is True
        assert detector.validate("+420 777 123 456") is True
        assert detector.validate("777123456") is True

    def test_validate_invalid_phone(self):
        detector = PhoneNumberDetector()

        assert detector.validate("+42012345") is False
        assert detector.validate("invalid") is False

    def test_detect_multiple_numbers(self):
        detector = PhoneNumberDetector()
        text = "Mobile: 777 123 456, Landline: 2 1234 5678"

        findings = detector.detect(text)

        assert len(findings) >= 2

    def test_no_detection_in_clean_text(self):
        detector = PhoneNumberDetector()
        text = "Just regular text"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_extracts_metadata_mobile(self):
        detector = PhoneNumberDetector()
        text = "Call: +420 777 123 456"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert "phone_type" in findings[0].metadata
        assert findings[0].metadata["phone_type"] == "mobile"

    def test_extracts_metadata_landline(self):
        detector = PhoneNumberDetector()
        text = "Office: +420 2 1234 5678"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert "phone_type" in findings[0].metadata
        assert findings[0].metadata["phone_type"] == "landline"

    def test_handles_various_formats(self):
        detector = PhoneNumberDetector()
        text = "Numbers: +420777123456, +420 777 123 456, 777 123 456"

        findings = detector.detect(text)

        assert len(findings) >= 3