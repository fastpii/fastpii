from fastpii.detectors.cz.iban import IBANDetector


class TestIBANDetector:
    VALID_CZECH_IBAN = "CZ2908000000000192000145"

    def test_detector_creation(self):
        detector = IBANDetector()

        assert detector.name == "iban"
        assert detector.region == "cz"
        assert "IBAN" in detector.description

    def test_detect_czech_iban_compact(self):
        detector = IBANDetector()
        text = f"IBAN: {self.VALID_CZECH_IBAN}"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].type == "iban"

    def test_detect_czech_iban_with_spaces(self):
        detector = IBANDetector()
        text = "IBAN: CZ29 0800 0000 0001 9200 0145"

        findings = detector.detect(text)

        assert len(findings) >= 1

    def test_validate_valid_czech_iban(self):
        detector = IBANDetector()

        assert detector.validate(self.VALID_CZECH_IBAN) is True

    def test_validate_invalid_check_digits(self):
        detector = IBANDetector()

        assert detector.validate("CZ0710000000000123456789") is False

    def test_validate_rejects_wrong_length(self):
        detector = IBANDetector()

        assert detector.validate("CZ071000") is False

    def test_validate_rejects_non_numeric(self):
        detector = IBANDetector()

        assert detector.validate("CZ07XXXX00000000123456789") is False

    def test_metadata_extraction(self):
        detector = IBANDetector()
        text = f"IBAN: {self.VALID_CZECH_IBAN}"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].metadata["country_code"] == "CZ"
        assert findings[0].metadata["bank_code"] == "0800"

    def test_context_boosts_confidence(self):
        detector = IBANDetector()
        text_with_context = f"IBAN: {self.VALID_CZECH_IBAN}"

        findings_with = detector.detect(text_with_context)

        assert len(findings_with) >= 1
        assert findings_with[0].confidence == 0.95

    def test_validated_without_context_has_high_confidence(self):
        detector = IBANDetector()
        text = self.VALID_CZECH_IBAN

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].confidence == 1.0

    def test_no_detection_in_clean_text(self):
        detector = IBANDetector()
        text = "No IBAN numbers here"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_validate_with_spaces(self):
        detector = IBANDetector()

        assert detector.validate("CZ29 0800 0000 0001 9200 0145") is True