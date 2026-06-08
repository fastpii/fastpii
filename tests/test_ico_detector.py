from fastpii.models import Finding
from fastpii.detectors.cz.ico import ICODetector


class TestICODetector:
    def test_detector_creation(self):
        detector = ICODetector()

        assert detector.name == "ico"
        assert detector.region == "cz"
        assert "Czech company ID" in detector.description

    def test_detect_valid_ico(self):
        detector = ICODetector()
        text = "Company IČO: 25596641"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "ico"
        assert findings[0].value == "25596641"
        assert findings[0].region == "cz"
        assert findings[0].confidence >= 0.95

    def test_detect_ico_with_leading_zeros(self):
        detector = ICODetector()
        text = "IČO: 00123456"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "00123456"

    def test_detect_multiple_icos(self):
        detector = ICODetector()
        text = "First: 25596641, Second: 12345678"

        findings = detector.detect(text)

        assert len(findings) == 1  
        assert findings[0].value == "25596641"

    def test_validate_valid_ico(self):
        detector = ICODetector()

        valid = detector.validate("25596641")

        assert valid is True

    def test_validate_invalid_checksum(self):
        detector = ICODetector()

        valid = detector.validate("12345678")

        assert valid is False

    def test_validate_invalid_length(self):
        detector = ICODetector()

        valid = detector.validate("123456")

        assert valid is False

    def test_validate_edge_case_25596641(self):
        detector = ICODetector()

        valid = detector.validate("25596641")

        assert valid is True

    def test_no_detection_in_clean_text(self):
        detector = ICODetector()
        text = "No PII identifiers here"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_extracts_checksum_metadata(self):
        detector = ICODetector()
        text = "IČO: 25596641"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert "checksum_valid" in findings[0].metadata
        assert findings[0].metadata["checksum_valid"] is True