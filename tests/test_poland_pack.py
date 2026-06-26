from fastpii import PrivacyGuard
from fastpii.countries import get_country_pack
from fastpii.countries.pl.pack import PolishPack
from fastpii.detectors.pl import (
    NIPDetector,
    PeseleDetector,
    PolishAddressDetector,
    PolishPhoneDetector,
    PolishPostalCodeDetector,
    REGONDetector,
)


class TestPESELDetector:
    def test_detector_creation(self):
        detector = PeseleDetector()

        assert detector.name == "pesel"
        assert detector.region == "pl"
        assert "Polish national ID" in detector.description

    def test_detect_valid_pesel(self):
        detector = PeseleDetector()
        text = "44051401458"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "pesel"
        assert findings[0].value == "44051401458"
        assert findings[0].region == "pl"
        assert findings[0].confidence == 0.80

    def test_detect_with_context(self):
        detector = PeseleDetector()
        text = "PESEL: 44051401458"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "44051401458"
        assert findings[0].confidence >= 0.95

    def test_detect_without_context(self):
        detector = PeseleDetector()
        text = "Identifier 44051401458 belongs to the customer"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].confidence == 0.80

    def test_detect_with_slash_separator(self):
        detector = PeseleDetector()
        text = "PESEL: 440514/01458"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_validate_valid(self):
        detector = PeseleDetector()

        valid = detector.validate("44051401458")

        assert valid is True

    def test_validate_invalid_checksum(self):
        detector = PeseleDetector()

        valid = detector.validate("44051401450")

        assert valid is False

    def test_detect_invalid_checksum(self):
        detector = PeseleDetector()
        text = "PESEL: 44051401450"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_extract_metadata(self):
        detector = PeseleDetector()
        text = "PESEL: 44051401458"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].metadata["birth_date"] == "1944-05-14"
        assert findings[0].metadata["gender"] == "male"
        assert findings[0].metadata["checksum_valid"] is True


class TestNIPDetector:
    def test_detector_creation(self):
        detector = NIPDetector()

        assert detector.name == "nip"
        assert detector.region == "pl"
        assert "Polish tax ID" in detector.description

    def test_detect_valid_nip(self):
        detector = NIPDetector()
        text = "NIP: 5260250274"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "nip"
        assert findings[0].value == "5260250274"
        assert findings[0].region == "pl"
        assert findings[0].confidence >= 0.90

    def test_validate_valid(self):
        detector = NIPDetector()

        valid = detector.validate("5260250274")

        assert valid is True

    def test_validate_invalid(self):
        detector = NIPDetector()

        assert detector.validate("5260250275") is False
        assert detector.validate("1234567890") is False

    def test_validate_formatting_variants(self):
        detector = NIPDetector()

        assert detector.validate("526 025 02 74") is True
        assert detector.validate("526-025-02-74") is True

    def test_detect_invalid_checksum(self):
        detector = NIPDetector()
        text = "NIP: 5260250275"

        findings = detector.detect(text)

        assert len(findings) == 0


class TestREGONDetector:
    def test_detector_creation(self):
        detector = REGONDetector()

        assert detector.name == "regon"
        assert detector.region == "pl"
        assert "Polish business registry" in detector.description

    def test_detect_valid_9digit(self):
        detector = REGONDetector()
        text = "REGON: 123456785"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "regon"
        assert findings[0].value == "123456785"
        assert findings[0].metadata["format"] == "9-digit"

    def test_detect_valid_14digit(self):
        detector = REGONDetector()
        text = "REGON: 12345678512347"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "12345678512347"
        assert findings[0].metadata["format"] == "14-digit"

    def test_validate_valid(self):
        detector = REGONDetector()

        assert detector.validate("123456785") is True
        assert detector.validate("12345678512347") is True

    def test_validate_invalid(self):
        detector = REGONDetector()

        assert detector.validate("123456789") is False

    def test_detect_invalid_checksum(self):
        detector = REGONDetector()
        text = "REGON: 123456789"

        findings = detector.detect(text)

        assert len(findings) == 0


class TestPolishPostalCodeDetector:
    def test_detector_creation(self):
        detector = PolishPostalCodeDetector()

        assert detector.name == "postal_code"
        assert detector.region == "pl"
        assert "Polish postal code" in detector.description

    def test_detect_postal_code(self):
        detector = PolishPostalCodeDetector()
        text = "Kod pocztowy: 00-001"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "postal_code"
        assert findings[0].value == "00-001"
        assert findings[0].region == "pl"

    def test_validate_valid(self):
        detector = PolishPostalCodeDetector()

        assert detector.validate("00-001") is True

    def test_validate_invalid(self):
        detector = PolishPostalCodeDetector()

        assert detector.validate("00-00") is False


class TestPolishPhoneDetector:
    def test_detector_creation(self):
        detector = PolishPhoneDetector()

        assert detector.name == "phone"
        assert detector.region == "pl"
        assert "Polish phone number" in detector.description

    def test_detect_with_plus48_prefix(self):
        detector = PolishPhoneDetector()
        text = "Call me at +48 512 345 678"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "phone"
        assert findings[0].value == "48512345678"
        assert findings[0].metadata["phone_type"] == "mobile"

    def test_detect_with_context_words(self):
        detector = PolishPhoneDetector()
        text = "Telefon: 512 345 678"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "48512345678"

    def test_validate_valid(self):
        detector = PolishPhoneDetector()

        assert detector.validate("+48 512 345 678") is True

    def test_validate_invalid(self):
        detector = PolishPhoneDetector()

        assert detector.validate("123") is False


class TestPolishAddressDetector:
    def test_detector_creation(self):
        detector = PolishAddressDetector()

        assert detector.name == "address"
        assert detector.region == "pl"
        assert "Polish address" in detector.description

    def test_detect_full_address(self):
        detector = PolishAddressDetector()
        text = "Adres: Długa 15 Warszawa"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].type == "address"
        assert findings[0].value == "Długa 15 Warszawa"
        assert findings[0].metadata["street"] == "Długa"
        assert findings[0].metadata["house_number"] == "15"
        assert findings[0].metadata["score"] == 100
        assert findings[0].confidence == 1.0

    def test_detect_simple_address(self):
        detector = PolishAddressDetector()
        text = "Adres do odbioru: Marszałkowska 10"

        findings = detector.detect(text)

        assert len(findings) == 1
        assert findings[0].value == "Marszałkowska 10"
        assert findings[0].confidence == 0.60

    def test_validate_valid(self):
        detector = PolishAddressDetector()

        assert detector.validate("Długa 15") is True

    def test_validate_invalid(self):
        detector = PolishAddressDetector()

        assert detector.validate("123") is False


class TestPolishPack:
    def test_registration(self):
        pack_cls = get_country_pack("pl")

        assert pack_cls == PolishPack

    def test_code(self):
        pack = PolishPack()

        assert pack.code == "pl"

    def test_name(self):
        pack = PolishPack()

        assert pack.name == "Poland"

    def test_metadata(self):
        pack = PolishPack()
        metadata = pack.metadata

        assert metadata.code == "pl"
        assert metadata.name == "Poland"
        assert metadata.official_name == "Rzeczpospolita Polska"
        assert metadata.language_codes == ("pl", "pl-PL")
        assert metadata.iso_3166_alpha2 == "PL"
        assert metadata.iso_3166_alpha3 == "POL"
        assert metadata.currency_code == "PLN"

    def test_detector_count(self):
        pack = PolishPack()

        assert len(pack.detectors) == 6

    def test_entities(self):
        pack = PolishPack()
        entity_types = {entity.entity_type for entity in pack.entities}

        assert len(pack.entities) == 6
        assert entity_types == {"pesel", "nip", "regon", "postal_code", "phone", "address"}
        assert pack.entities[0].examples == ("44051401458",)
        assert pack.entities[0].invalid_examples == ("44051401459",)


class TestPolandIntegration:
    def test_detect_all_pl_entities(self):
        gateway = PrivacyGuard(regions=["pl"])
        text = (
            "PESEL: 44051401458, NIP: 5260250274, REGON: 123456785, "
            "kod pocztowy: 00-001, tel: +48 512 345 678, adres: Długa 15"
        )

        result = gateway.detect(text)

        assert len(result.findings) == 6
        assert result.text == text
        assert set(result.detector_names) == {"pesel", "nip", "regon", "postal_code", "phone", "address"}
        assert result.processing_time_ms >= 0

    def test_validate_pl_entities(self):
        gateway = PrivacyGuard(regions=["pl"])

        pesel_result = gateway.validate("44051401458", "pesel")
        nip_result = gateway.validate("5260250274", "nip")
        regon_result = gateway.validate("123456785", "regon")

        assert pesel_result.is_valid is True
        assert pesel_result.metadata["birth_date"] == "1944-05-14"
        assert pesel_result.metadata["gender"] == "male"
        assert nip_result.is_valid is True
        assert nip_result.metadata["checksum_valid"] is True
        assert regon_result.is_valid is True
        assert regon_result.metadata["checksum_valid"] is True

    def test_anonymize_pl_entities(self):
        gateway = PrivacyGuard(regions=["pl"])
        text = "PESEL: 44051401458, NIP: 5260250274, REGON: 123456785"

        anonymized = gateway.anonymize(text)

        assert anonymized == "PESEL: [REDACTED], NIP: [REDACTED], REGON: [REDACTED]"

    def test_redact_pl_entities(self):
        gateway = PrivacyGuard(regions=["pl"])
        text = "PESEL: 44051401458, NIP: 5260250274, REGON: 123456785"

        redacted = gateway.redact(text)

        assert redacted == "PESEL: [PESEL], NIP: [NIP], REGON: [REGON]"

    def test_mask_pl_entities(self):
        gateway = PrivacyGuard(regions=["pl"])
        text = "PESEL: 44051401458, NIP: 5260250274, REGON: 123456785"

        masked = gateway.mask(text)

        assert "44051401458" not in masked
        assert "5260250274" not in masked
        assert "123456785" not in masked
        assert masked == "PESEL: ***********, NIP: **********, REGON: *********"
