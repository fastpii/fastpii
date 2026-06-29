"""Tests for DateOfBirthDetector."""

from fastpii.detectors.cz.date_of_birth import DateOfBirthDetector


class TestDateOfBirthDetector:
    """Test suite for DateOfBirthDetector."""

    def test_detector_creation(self):
        """Test detector initialization."""
        detector = DateOfBirthDetector()
        assert detector.name == "date_of_birth"
        assert detector.region == "cz"

    def test_detect_standard_date(self):
        """Test detection of standard Czech date format."""
        detector = DateOfBirthDetector()
        text = "Datum narození: 15.03.1980"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "date_of_birth"
        assert "15.03.1980" in findings[0].value

    def test_detect_date_with_context(self):
        """Test detection with birth context word."""
        detector = DateOfBirthDetector()
        text = "Narozen 1.5.1990"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].type == "date_of_birth"
        assert findings[0].confidence >= 0.90  # Higher confidence with context

    def test_detect_date_without_context(self):
        """Test detection without birth context word."""
        detector = DateOfBirthDetector()
        text = "Dne 15.03.1980 se koná schůze"

        findings = detector.detect(text)

        if findings:
            assert findings[0].type == "date"
            assert findings[0].confidence <= 0.80  # Lower confidence without context

    def test_birth_context_is_local_to_each_date(self):
        """Only dates with nearby birth context should be tagged as DOB."""
        detector = DateOfBirthDetector()
        text = "Date: 12.05.2026\nDate of Birth: 15.03.1988\nPlease respond before 30.09.2026\n22.07.1979"

        findings = detector.detect(text)

        assert [finding.type for finding in findings] == [
            "date",
            "date_of_birth",
            "date",
            "date",
        ]
        assert [round(finding.confidence, 2) for finding in findings] == [0.70, 0.95, 0.70, 0.70]

    def test_detect_english_textual_birth_date(self):
        """English month names should still respect nearby birth context."""
        detector = DateOfBirthDetector()
        text = "born on 1 January 1980"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "1 January 1980"
        assert findings[0].type == "date_of_birth"
        assert findings[0].confidence == 0.95

    def test_detect_iso_format(self):
        """ISO dates should be detected."""
        detector = DateOfBirthDetector()
        text = "Datum narození: 1980-01-01"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "1980-01-01"
        assert findings[0].type == "date_of_birth"

    def test_detect_czech_text_month(self):
        """Czech textual month dates should be detected."""
        detector = DateOfBirthDetector()
        text = "Datum narození: 1. ledna 1980"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "1. ledna 1980"
        assert findings[0].type == "date_of_birth"

    def test_detect_czech_text_month_female(self):
        """Czech inflected month names should be detected."""
        detector = DateOfBirthDetector()
        text = "Narozena 5. května 1990"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "5. května 1990"
        assert findings[0].type == "date_of_birth"

    def test_detect_us_format(self):
        """Slash-separated US dates should be detected when day disambiguates them."""
        detector = DateOfBirthDetector()
        text = "DOB: 01/15/1980"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "01/15/1980"
        assert findings[0].metadata["iso_date"] == "1980-01-15"

    def test_detect_eu_format(self):
        """Slash-separated European dates should be detected."""
        detector = DateOfBirthDetector()
        text = "Datum narození: 15/01/1980"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "15/01/1980"
        assert findings[0].metadata["iso_date"] == "1980-01-15"

    def test_iso_format_metadata(self):
        """ISO-format dates should produce normalized metadata."""
        detector = DateOfBirthDetector()
        text = "Narozen 1980-01-01"

        findings = detector.detect(text)

        assert len(findings) == 1
        metadata = findings[0].metadata
        assert metadata["day"] == 1
        assert metadata["month"] == 1
        assert metadata["year"] == 1980
        assert metadata["iso_date"] == "1980-01-01"
        assert isinstance(metadata["age"], int)

    def test_context_boost_iso(self):
        """ISO dates should still get a context confidence boost."""
        detector = DateOfBirthDetector()
        text = "Datum narození: 1980-01-01"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].confidence == 0.95

    def test_no_duplicate_findings(self):
        """Overlapping date formats should only emit one finding."""
        detector = DateOfBirthDetector()
        text = "Datum narození: 1. 1. 1980"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "1. 1. 1980"

    def test_validate_valid_dates(self):
        """Test validation of valid date formats."""
        detector = DateOfBirthDetector()
        
        valid_dates = [
            "15.03.1980",
            "1.5.1990",
            "31.12.2000",
            "29.02.2000",  # Leap year
            "1980-01-01",
            "15/01/1980",
            "01/15/1980",
            "1. ledna 1980",
        ]
        
        for date in valid_dates:
            assert detector.validate(date) is True, f"Expected valid: {date}"

    def test_validate_invalid_dates(self):
        """Test validation rejects invalid dates."""
        detector = DateOfBirthDetector()
        
        invalid_dates = [
            "32.01.2000",  # Invalid day
            "15.13.2000",  # Invalid month
            "15.03.1800",  # Year too far in past
            "29.02.2001",  # Not a leap year
            "1980-15-01",  # Invalid ISO month
            "15/15/1980",  # Invalid slash date
            "1. foo 1980",  # Invalid textual month
            "abc",         # Not a date
        ]
        
        for date in invalid_dates:
            assert detector.validate(date) is False, f"Expected invalid: {date}"

    def test_metadata_extraction(self):
        """Test metadata extraction from date."""
        detector = DateOfBirthDetector()
        text = "Narozen 15.03.1980"

        findings = detector.detect(text)

        if findings:
            metadata = findings[0].metadata
            assert "day" in metadata
            assert "month" in metadata
            assert "year" in metadata
            assert "iso_date" in metadata
            assert metadata["day"] == 15
            assert metadata["month"] == 3
            assert metadata["year"] == 1980
            assert metadata["iso_date"] == "1980-03-15"

    def test_zodiac_sign_extraction(self):
        """Test zodiac sign extraction."""
        detector = DateOfBirthDetector()
        text = "Narozen 21.03.1980"  # Aries starts March 21

        findings = detector.detect(text)

        if findings:
            assert findings[0].metadata["zodiac_sign"] == "aries"

    def test_multiple_dates(self):
        """Test detection of multiple dates."""
        detector = DateOfBirthDetector()
        text = "Narozen 15.03.1980, úmrtí 01.01.2020"

        findings = detector.detect(text)

        assert len(findings) >= 1  # At least one date detected

    def test_no_false_positives_numbers(self):
        """Test that standalone numbers are not detected."""
        detector = DateOfBirthDetector()
        text = "12345 67890"

        findings = detector.detect(text)

        assert len(findings) == 0
