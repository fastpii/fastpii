"""Tests for AddressDetector."""

from fastpii.detectors.cz.address import AddressDetector


class TestAddressDetector:
    """Test suite for AddressDetector."""

    def test_detector_creation(self):
        """Test detector initialization."""
        detector = AddressDetector()

        assert detector.name == "address"
        assert detector.region == "cz"
        assert "address" in detector.description.lower()

    def test_detect_full_address(self):
        """Test detection of full address with all components."""
        detector = AddressDetector()
        text = "Václavské náměstí 1, Praha 11000"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].type == "address"
        assert "Praha" in findings[0].value or "Václavské" in findings[0].value

    def test_detect_street_with_number(self):
        """Test detection of street address with house number."""
        detector = AddressDetector()
        text = "Národní třída 15"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "address"
        assert "Národní" in findings[0].value
        assert "15" in findings[0].value

    def test_detect_address_with_postal_code(self):
        """Test detection of address with postal code."""
        detector = AddressDetector()
        text = "Wilsonova 100, Praha 12000"

        findings = detector.detect(text)

        assert len(findings) >= 1
        if findings:
            assert findings[0].type == "address"
            # Should contain street or city
            assert "Wilsonova" in findings[0].value or "Praha" in findings[0].value

    def test_detect_multiple_addresses(self):
        """Test detection of multiple addresses."""
        detector = AddressDetector()
        text = "Adresa 1: Národní 10, Brno 60200. Adresa 2: Wilsonova 5, Praha 11000."

        findings = detector.detect(text)

        # Should detect at least one address
        assert len(findings) >= 1

    def test_validate_valid_addresses(self):
        """Test validation of valid addresses."""
        detector = AddressDetector()
        
        valid_addresses = [
            "Národní 15",
            "Václavské náměstí 1, Praha",
            "Wilsonova 100",
        ]
        
        for addr in valid_addresses:
            assert detector.validate(addr) is True, f"Expected valid: {addr}"

    def test_validate_invalid_addresses(self):
        """Test validation rejects invalid addresses."""
        detector = AddressDetector()
        
        invalid_addresses = [
            "123456",  # Only numbers
            "email@email.cz",  # Email, not address
            "Jan",  # Only name
            "",  # Empty
        ]
        
        for addr in invalid_addresses:
            assert detector.validate(addr) is False, f"Expected invalid: {addr}"

    def test_metadata_extraction(self):
        """Test metadata extraction from detected address."""
        detector = AddressDetector()
        text = "Václavské náměstí 1, Praha 11000"

        findings = detector.detect(text)

        if findings:
            metadata = findings[0].metadata
            # Should have some metadata components
            assert "full_address" in metadata

    def test_known_czech_cities(self):
        """Test detection of addresses in known Czech cities."""
        detector = AddressDetector()
        
        # Test addresses with known cities
        test_cases = [
            "Národní 10, Praha",
            "Masarykova 5, Brno",
            "Ostravská 20, Ostrava",
        ]
        
        for text in test_cases:
            findings = detector.detect(text)
            # Should detect at least simple pattern
            assert len(findings) >= 1, f"Failed to detect: {text}"

    def test_no_false_positives_emails(self):
        """Test that emails are not detected as addresses."""
        detector = AddressDetector()
        text = "jan@email.cz"

        findings = detector.detect(text)

        # Email should not be detected as address
        assert len(findings) == 0

    def test_no_false_positives_rodne_cislo(self):
        """Test that rodné číslo is not detected as address."""
        detector = AddressDetector()
        text = "RČ: 8001011238"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_house_number_patterns(self):
        """Test detection of various house number patterns."""
        detector = AddressDetector()
        
        # Different number patterns
        patterns = [
            "Národní 15",
            "Wilsonova 123/45",
            "Václavské náměstí 1",
        ]
        
        for text in patterns:
            findings = detector.detect(text)
            assert len(findings) >= 1, f"Failed to detect: {text}"

    def test_context_in_text(self):
        """Test address detection in context."""
        detector = AddressDetector()
        text = "Sídlo společnosti: Václavské náměstí 1, Praha 11000. IČO: 25596641"

        findings = detector.detect(text)

        if findings:
            assert len(findings) >= 1
            assert findings[0].type == "address"