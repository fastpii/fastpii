from cpg.models import Finding
from cpg.detectors.cz.rodne_cislo import RodneCisloDetector


class TestRodneCisloDetector:
    def test_detector_creation(self):
        detector = RodneCisloDetector()

        assert detector.name == "rodne_cislo"
        assert detector.region == "cz"
        assert "Czech birth number" in detector.description

    def test_detect_10_digit_rodne_cislo(self):
        detector = RodneCisloDetector()
        text = "Jan Novák, RČ: 8001011234"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "rodne_cislo"
        assert findings[0].value == "8001011234"
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
        text = "RČ: 800101/1234"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert "800101" in findings[0].value
        assert "1234" in findings[0].value

    def test_validate_valid_10_digit(self):
        detector = RodneCisloDetector()

        valid = detector.validate("8001011234")

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
        text = "RČ: 8001011234"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert "birth_date" in findings[0].metadata
        assert findings[0].metadata["birth_date"] == "1980-01-01"

    def test_extract_metadata_gender_male(self):
        detector = RodneCisloDetector()
        text = "RČ: 8001011234"

        findings = detector.detect(text)

        assert findings[0].metadata["gender"] == "male"

    def test_extract_metadata_gender_female(self):
        detector = RodneCisloDetector()
        text = "RČ: 8051011234"

        findings = detector.detect(text)

        assert findings[0].metadata["gender"] == "female"

    def test_extracts_article_nine_flag(self):
        detector = RodneCisloDetector()
        text = "RČ: 8001011234"

        findings = detector.detect(text)

        assert "article_9" in findings[0].metadata
        assert findings[0].metadata["article_9"] is True

    def test_no_detection_in_clean_text(self):
        detector = RodneCisloDetector()
        text = "Hello world, no PII here"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_multiple_rodne_cislo_in_text(self):
        detector = RodneCisloDetector()
        text = "First person: 8001011234, Second: 8102015678"

        findings = detector.detect(text)

        assert len(findings) == 2