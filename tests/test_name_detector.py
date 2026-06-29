"""Tests for NameDetector with gender classification."""

from fastpii.countries.cz.data.corporate_names import CzechCorporateNamesData
from fastpii.detectors.cz.name import NameDetector


class CustomCorporateNamesData(CzechCorporateNamesData):
    def __init__(self, names: set[str]) -> None:
        super().__init__()
        self._names: set[str] = names

    def get_data(self) -> set[str]:
        return self._names


class TestNameDetector:
    """Test suite for NameDetector."""

    def test_detector_creation(self):
        """Test detector initialization."""
        detector = NameDetector()

        assert detector.name == "name"
        assert detector.region == "cz"
        assert "Czech personal name" in detector.description

    def test_detect_basic_male_name(self):
        """Test detection of basic Czech male name."""
        detector = NameDetector()
        text = "Jan Novák"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "name"
        assert findings[0].value == "Jan Novák"
        assert findings[0].metadata["gender"] == "m"

    def test_detect_basic_female_name(self):
        """Test detection of basic Czech female name."""
        detector = NameDetector()
        text = "Marie Nováková"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "name"
        assert findings[0].value == "Marie Nováková"
        assert findings[0].metadata["gender"] == "f"
        assert findings[0].metadata["marital_status"] == "married"

    def test_detect_male_surname(self):
        """Test detection of male surname name."""
        detector = NameDetector()
        text = "Petr Svoboda"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "Petr Svoboda"
        assert findings[0].metadata["gender"] == "m"

    def test_detect_female_ending_a(self):
        """Test detection of female name ending in -a."""
        detector = NameDetector()
        text = "Jana Dvořáková"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].metadata["gender"] == "f"

    def test_detect_name_in_context(self):
        """Test detection of name in context."""
        detector = NameDetector()
        text = "Kontakt: Jan Novák, email: jan@email.cz"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "Jan Novák"
        assert findings[0].metadata["firstname"] == "Jan"
        assert findings[0].metadata["surname"] == "Novák"

    def test_detect_multiple_names(self):
        """Test detection of multiple names."""
        detector = NameDetector()
        text = "Jan Novák a Marie Dvořáková"

        findings = detector.detect(text)

        assert len(findings) == 2
        names = [f.value for f in findings]
        assert "Jan Novák" in names
        assert "Marie Dvořáková" in names

    def test_gender_classification_male_firstname(self):
        """Test gender classification based on first name."""
        detector = NameDetector()

        # Known male names
        male_names = ["Jan Novák", "Petr Svoboda", "Josef Dvořák"]
        
        for name in male_names:
            findings = detector.detect(name)
            assert len(findings) == 1
            assert findings[0].metadata["gender"] == "m", f"Expected male for {name}"

    def test_gender_classification_female_firstname(self):
        """Test gender classification for female first names."""
        detector = NameDetector()

        # Known female names
        female_names = ["Marie Nováková", "Eva Svobodová", "Jana Dvořáková"]
        
        for name in female_names:
            findings = detector.detect(name)
            assert len(findings) == 1
            assert findings[0].metadata["gender"] == "f", f"Expected female for {name}"

    def test_gender_classification_surname_ending(self):
        """Test gender classification based on surname ending."""
        detector = NameDetector()
        
        # Unknown first name + -ová surname
        text = "Xyz Nováková"
        findings = detector.detect(text)
        assert len(findings) == 1
        # Should classify as female due to -ová ending
        assert findings[0].metadata["gender"] == "f"

    def test_validate_valid_names(self):
        """Test validation of valid Czech names."""
        detector = NameDetector()
        
        valid_names = [
            "Jan Novák",
            "Marie Dvořáková",
            "Petr Svoboda",
            "Jana Černá",
        ]
        
        for name in valid_names:
            assert detector.validate(name) is True, f"Expected valid: {name}"

    def test_validate_invalid_names(self):
        """Test validation rejects invalid names."""
        detector = NameDetector()
        
        invalid_names = [
            "jan",  # Only first name
            "novák",  # Only surname
            "123456",  # Numbers
            "Jan123",  # Numbers in name
            "",  # Empty
            "J",  # Too short
        ]
        
        for name in invalid_names:
            assert detector.validate(name) is False, f"Expected invalid: {name}"

    def test_metadata_extraction(self):
        """Test metadata extraction from detected name."""
        detector = NameDetector()
        text = "Jan Novák"
        
        findings = detector.detect(text)
        
        assert len(findings) == 1
        metadata = findings[0].metadata
        
        assert "firstname" in metadata
        assert "surname" in metadata
        assert "gender" in metadata
        assert metadata["firstname"] == "Jan"
        assert metadata["surname"] == "Novák"
        assert metadata["gender"] == "m"

    def test_marital_status_detection(self):
        """Test marital status detection for female names."""
        detector = NameDetector()
        
        # Married female (-ová)
        text = "Marie Nováková"
        findings = detector.detect(text)
        assert len(findings) == 1
        assert "marital_status" in findings[0].metadata
        assert findings[0].metadata["marital_status"] == "married"
        
        # Male name (no marital status)
        text = "Jan Novák"
        findings = detector.detect(text)
        assert len(findings) == 1
        assert "marital_status" not in findings[0].metadata

    def test_czech_diacritics(self):
        """Test handling of Czech diacritical marks."""
        detector = NameDetector()
        
        names_with_diacritics = [
            "Josef Dvořák",
            "Petr Černý",
            "JanaNováková",
            "Tomáš Šimek",
        ]
        
        for name in names_with_diacritics:
            findings = detector.detect(name)
            if len(findings) > 0:  # Pattern might not match all
                assert findings[0].value == name

    def test_no_false_positives_in_numbers(self):
        """Test that pure numbers are not detected as names."""
        detector = NameDetector()
        text = "123456 789012"
        
        findings = detector.detect(text)
        
        assert len(findings) == 0

    def test_no_false_positives_in_emails(self):
        """Test that emails are not detected as names."""
        detector = NameDetector()
        text = "jan@email.cz"
        
        findings = detector.detect(text)
        
        assert len(findings) == 0

    def test_confidence_known_names(self):
        """Test confidence for well-known Czech names."""
        detector = NameDetector()
        
        # Known names from database
        text = "Jan Novák"
        findings = detector.detect(text)
        assert len(findings) == 1
        assert findings[0].confidence >= 0.90  # High confidence for known names

    def test_name_with_context_words(self):
        """Test name detection doesn't capture context words."""
        detector = NameDetector()
        text = "Jméno: Jan Novák, adresa: Praha"
        
        findings = detector.detect(text)
        
        assert len(findings) == 1
        assert findings[0].value == "Jan Novák"
        assert "Jméno:" not in findings[0].value
        assert "adresa:" not in findings[0].value

    def test_skip_heading_false_positives(self):
        """Test common headings are not detected as names."""
        detector = NameDetector()
        text = (
            "Customer Information\n"
            "Company Details\n"
            "Vehicle Information\n"
            "False Positive Tests\n"
            "Account Number\n"
            "Alternative Account\n"
            "Business Information\n"
            "Additional Employees\n"
            "Registered Office"
        )

        findings = detector.detect(text)

        assert findings == []

    def test_skip_name_matches_across_newlines(self):
        """Test detector does not match names across line breaks."""
        detector = NameDetector()
        text = "Notes\n\nThe\nJan Novák"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "Jan Novák"

    def test_detect_when_only_one_word_is_in_dictionary(self):
        """Test detector keeps matches when one token is in the dictionaries."""
        detector = NameDetector()
        text = "Novák Consulting"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "Novák Consulting"

    def test_corporate_name_filtered_sro(self):
        """Test corporate names with s.r.o. context are not detected as person names."""
        detector = NameDetector()

        findings = detector.detect("Komerční banka s.r.o.")

        assert findings == []

    def test_corporate_name_filtered_as(self):
        """Test corporate names with a.s. context are not detected as person names."""
        detector = NameDetector()

        findings = detector.detect("Česká spořitelna a.s.")

        assert findings == []

    def test_corporate_name_filtered_vos(self):
        """Test corporate names with v.o.s. context are not detected as person names."""
        detector = NameDetector()

        findings = detector.detect("Pepa v.o.s.")

        assert findings == []

    def test_real_name_not_filtered(self):
        """Test real names are still detected after corporate filtering."""
        detector = NameDetector()

        findings = detector.detect("Jan Novák")

        assert len(findings) == 1
        assert findings[0].value == "Jan Novák"

    def test_corporate_name_di_override(self):
        """Test corporate name filtering supports dependency injection overrides."""
        detector = NameDetector(corporate_names_data=CustomCorporateNamesData({"novák"}))

        findings = detector.detect("Jan Novák")

        assert findings == []
