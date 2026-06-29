from fastpii.detectors.cz.credit_card import CreditCardDetector


class TestCreditCardDetector:
    def test_detector_creation(self):
        detector = CreditCardDetector()

        assert detector.name == "credit_card"
        assert detector.region == "cz"
        assert "credit card" in detector.description.lower()

    def test_detect_visa_with_context(self):
        detector = CreditCardDetector()
        text = "Credit card: 4111111111111111"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].type == "credit_card"
        assert findings[0].metadata["card_type"] == "visa"

    def test_detect_mastercard_with_context(self):
        detector = CreditCardDetector()
        text = "Card number: 5500000000000004"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].metadata["card_type"] == "mastercard"

    def test_detect_amex_with_context(self):
        detector = CreditCardDetector()
        text = "Amex: 378282246310005"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].metadata["card_type"] == "amex"

    def test_validate_valid_visa(self):
        detector = CreditCardDetector()

        assert detector.validate("4111111111111111") is True

    def test_validate_valid_mastercard(self):
        detector = CreditCardDetector()

        assert detector.validate("5500000000000004") is True

    def test_validate_valid_amex(self):
        detector = CreditCardDetector()

        assert detector.validate("378282246310005") is True

    def test_validate_rejects_invalid_luhn(self):
        detector = CreditCardDetector()

        assert detector.validate("4111111111111112") is False

    def test_validate_rejects_invalid_format(self):
        detector = CreditCardDetector()

        assert detector.validate("not a card") is False
        assert detector.validate("") is False

    def test_validate_with_spaces_and_dashes(self):
        detector = CreditCardDetector()

        assert detector.validate("4111 1111 1111 1111") is True
        assert detector.validate("4111-1111-1111-1111") is True

    def test_luhn_check(self):
        assert CreditCardDetector._luhn_check("4111111111111111") is True
        assert CreditCardDetector._luhn_check("5500000000000004") is True
        assert CreditCardDetector._luhn_check("378282246310005") is True
        assert CreditCardDetector._luhn_check("4111111111111112") is False

    def test_no_detection_without_context(self):
        detector = CreditCardDetector()
        text = "4111111111111111"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].confidence == 0.60

    def test_no_detection_in_clean_text(self):
        detector = CreditCardDetector()
        text = "No credit cards here"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_context_confidence(self):
        detector = CreditCardDetector()
        text_with_context = "credit card 4111111111111111"
        text_with_cvv = "Card# 4111111111111111 CVV 123"

        findings = detector.detect(text_with_context)
        assert len(findings) >= 1
        assert findings[0].confidence == 0.95

        findings = detector.detect(text_with_cvv)
        assert len(findings) >= 1

    def test_metadata_card_type(self):
        detector = CreditCardDetector()
        text = "visa card 4111111111111111"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].metadata["card_type"] == "visa"
        assert findings[0].metadata["length"] == 16

    def test_rejects_unknown_prefix(self):
        detector = CreditCardDetector()
        text = "card: 0000000000000000"

        findings = detector.detect(text)

        assert len(findings) == 0