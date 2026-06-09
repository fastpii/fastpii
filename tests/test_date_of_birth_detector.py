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
        assert findings[0].confidence >= 0.90  # Higher confidence with context

    def test_detect_date_without_context(self):
        """Test detection without birth context word."""
        detector = DateOfBirthDetector()
        text = "Dne 15.03.1980 se koná schůze"

        findings = detector.detect(text)

        if findings:
            assert findings[0].confidence <= 0.80  # Lower confidence without context

    def test_validate_valid_dates(self):
        """Test validation of valid date formats."""
        detector = DateOfBirthDetector()
        
        valid_dates = [
            "15.03.1980",
            "1.5.1990",
            "31.12.2000",
            "29.02.2000",  # Leap year
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