from fastpii import PrivacyGuard
from fastpii.countries import get_country_pack
from fastpii.countries.de.pack import GERMAN_ENTITIES, GERMAN_METADATA, GermanPack
from fastpii.detectors.de.address import GermanAddressDetector
from fastpii.detectors.de.handelsregister import HandelsregisterDetector
from fastpii.detectors.de.phone import GermanPhoneDetector
from fastpii.detectors.de.postal_code import GermanPostalCodeDetector
from fastpii.detectors.de.steuer_id import SteuerIdDetector
from fastpii.detectors.de.ust_id import UStIdNrDetector


class TestSteuerIdDetector:
    def test_detector_creation(self):
        detector = SteuerIdDetector()

        assert detector.name == "steuer_id"
        assert detector.region == "de"
        assert "German tax ID" in detector.description

    def test_detect_valid(self):
        detector = SteuerIdDetector()
        text = "Steuer-ID: 86095742719"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "steuer_id"
        assert findings[0].value == "86095742719"
        assert findings[0].region == "de"
        assert findings[0].confidence >= 0.95
        assert findings[0].metadata["checksum_valid"] is True

    def test_validate_valid(self):
        detector = SteuerIdDetector()

        valid = detector.validate("86095742719")

        assert valid is True

    def test_validate_invalid_checksum(self):
        detector = SteuerIdDetector()

        valid = detector.validate("86095742710")

        assert valid is False

    def test_validate_starts_with_zero(self):
        detector = SteuerIdDetector()

        valid = detector.validate("06095742719")

        assert valid is False


class TestUStIdNrDetector:
    def test_detector_creation(self):
        detector = UStIdNrDetector()

        assert detector.name == "ust_id"
        assert detector.region == "de"
        assert "German VAT number" in detector.description

    def test_detect_valid(self):
        detector = UStIdNrDetector()
        text = "USt-IdNr: DE136695976"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "ust_id"
        assert findings[0].value == "DE136695976"
        assert findings[0].region == "de"
        assert findings[0].confidence >= 0.95
        assert findings[0].metadata["checksum_valid"] is True

    def test_validate_valid(self):
        detector = UStIdNrDetector()

        valid = detector.validate("DE136695976")

        assert valid is True

    def test_validate_invalid(self):
        detector = UStIdNrDetector()

        valid = detector.validate("DE123456789")

        assert valid is False

    def test_validate_without_de_prefix(self):
        detector = UStIdNrDetector()

        valid = detector.validate("136695976")

        assert valid is False


class TestHandelsregisterDetector:
    def test_detector_creation(self):
        detector = HandelsregisterDetector()

        assert detector.name == "handelsregister"
        assert detector.region == "de"
        assert "German commercial register" in detector.description

    def test_detect_hrb(self):
        detector = HandelsregisterDetector()
        text = "Handelsregister: München HRB 12345"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "handelsregister"
        assert findings[0].value == "München HRB 12345"
        assert findings[0].metadata["court"] == "München"
        assert findings[0].metadata["type"] == "HRB"
        assert findings[0].metadata["number"] == "12345"

    def test_detect_hra(self):
        detector = HandelsregisterDetector()
        text = "Registereintrag Berlin HRA 67890"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "Berlin HRA 67890"
        assert findings[0].metadata["court"] == "Berlin"
        assert findings[0].metadata["type"] == "HRA"
        assert findings[0].metadata["number"] == "67890"

    def test_validate_invalid(self):
        detector = HandelsregisterDetector()

        valid = detector.validate("XYZ")

        assert valid is False


class TestGermanPostalCodeDetector:
    def test_detector_creation(self):
        detector = GermanPostalCodeDetector()

        assert detector.name == "postal_code"
        assert detector.region == "de"
        assert "German postal code" in detector.description

    def test_detect_valid(self):
        detector = GermanPostalCodeDetector()
        text = "PLZ: 10115 Berlin und Postleitzahl: 80331 München"

        findings = detector.detect(text)

        assert len(findings) == 2
        assert findings[0].value == "10115"
        assert findings[0].metadata["zone"] == "1"
        assert findings[1].value == "80331"
        assert findings[1].metadata["zone"] == "8"


class TestGermanPhoneDetector:
    def test_detector_creation(self):
        detector = GermanPhoneDetector()

        assert detector.name == "phone"
        assert detector.region == "de"
        assert "German phone number" in detector.description

    def test_detect_with_prefix(self):
        detector = GermanPhoneDetector()
        text = "Sie erreichen uns unter +49 30 1234567."

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "phone"
        assert findings[0].value == "49301234567"
        assert findings[0].metadata["phone_type"] == "landline"


class TestGermanAddressDetector:
    def test_detector_creation(self):
        detector = GermanAddressDetector()

        assert detector.name == "address"
        assert detector.region == "de"
        assert "German address" in detector.description

    def test_detect_full_address(self):
        detector = GermanAddressDetector()
        text = "Unsere Anschrift ist Hauptstraße 12, 10115 Berlin."

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "address"
        assert findings[0].value == "Hauptstraße 12, 10115 Berlin"
        assert findings[0].confidence >= 0.8
        assert findings[0].metadata["street"] == "Hauptstraße"
        assert findings[0].metadata["house_number"] == "12"
        assert findings[0].metadata["postal_code"] == "10115"
        assert findings[0].metadata["city"] == "Berlin"
        assert detector.validate(findings[0].value) is True


class TestGermanPack:
    def test_code(self):
        pack = GermanPack()

        assert pack.code == "de"
        assert get_country_pack("de") is GermanPack

    def test_name(self):
        pack = GermanPack()

        assert pack.name == "Germany"

    def test_metadata(self):
        pack = GermanPack()

        assert pack.metadata == GERMAN_METADATA
        assert pack.metadata.code == "de"
        assert pack.metadata.name == "Germany"
        assert pack.metadata.official_name == "Bundesrepublik Deutschland"
        assert pack.metadata.language_codes == ("de", "de-DE")
        assert pack.metadata.iso_3166_alpha2 == "DE"
        assert pack.metadata.iso_3166_alpha3 == "DEU"
        assert pack.metadata.currency_code == "EUR"

    def test_detector_count(self):
        pack = GermanPack()
        detector_names = [detector.name for detector in pack.detectors]

        assert len(pack.detectors) == 6
        assert detector_names == [
            "steuer_id",
            "ust_id",
            "handelsregister",
            "postal_code",
            "phone",
            "address",
        ]

    def test_entities(self):
        pack = GermanPack()
        entity_types = [entity.entity_type for entity in pack.entities]

        assert pack.entities == GERMAN_ENTITIES
        assert len(pack.entities) == 6
        assert entity_types == [
            "steuer_id",
            "ust_id",
            "handelsregister",
            "postal_code",
            "phone",
            "address",
        ]
        assert pack.entities[0].examples == ("86095742719",)
        assert pack.entities[1].examples == ("DE136695976",)
        assert pack.entities[2].examples == ("München HRB 12345",)


class TestGermanyIntegration:
    def test_detect_all_de_entities(self):
        gateway = PrivacyGuard(regions=["de"])
        text = (
            "Steuer-ID: 86095742719\n"
            "USt-IdNr: DE136695976\n"
            "Handelsregister: München HRB 1234 A\n"
            "PLZ: 80331 München\n"
            "Telefon: +49 30 1234567\n"
            "Adresse: Hauptstraße 12\n"
        )

        result = gateway.detect(text)

        assert len(result.findings) >= 6
        assert result.text == text
        assert result.processing_time_ms >= 0
        assert set(result.detector_names) == {
            "steuer_id",
            "ust_id",
            "handelsregister",
            "postal_code",
            "phone",
            "address",
        }

    def test_validate(self):
        gateway = PrivacyGuard(regions=["de"])

        steuer_result = gateway.validate("86095742719", "steuer_id")
        ust_result = gateway.validate("DE136695976", "ust_id")
        address_result = gateway.validate("Hauptstraße 12, 10115 Berlin", "address")

        assert steuer_result.is_valid is True
        assert steuer_result.metadata["checksum_valid"] is True
        assert ust_result.is_valid is True
        assert ust_result.metadata["checksum_valid"] is True
        assert address_result.is_valid is True

    def test_anonymize(self):
        gateway = PrivacyGuard(regions=["de"])
        text = "Steuer-ID: 86095742719, USt-IdNr: DE136695976"

        anonymized = gateway.anonymize(text)

        assert "86095742719" not in anonymized
        assert "DE136695976" not in anonymized
        assert anonymized.count("[REDACTED]") == 2

    def test_redact(self):
        gateway = PrivacyGuard(regions=["de"])
        text = "Steuer-ID: 86095742719, USt-IdNr: DE136695976"

        redacted = gateway.redact(text)

        assert "[STEUER_ID]" in redacted
        assert "[UST_ID]" in redacted

    def test_mask(self):
        gateway = PrivacyGuard(regions=["de"])
        text = "Telefon: +49 30 1234567"

        masked = gateway.mask(text)

        assert "+49 30 1234567" not in masked
        assert "*******" in masked
