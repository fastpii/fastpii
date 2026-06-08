import pytest

from cpg import PrivacyGateway, Finding


class TestPrivacyGateway:
    def test_gateway_creation_with_czech_region(self):
        gateway = PrivacyGateway(regions=["cz"])

        detectors = gateway.list_detectors()

        assert len(detectors) >= 1

    def test_gateway_creation_with_no_regions_loads_all(self):
        gateway = PrivacyGateway()

        detectors = gateway.list_detectors()

        assert len(detectors) >= 1

    def test_detect_czech_rodne_cislo(self):
        gateway = PrivacyGateway(regions=["cz"])
        text = "Jan Novák, RČ: 8001011234"

        result = gateway.detect(text)

        assert len(result.findings) >= 1
        assert result.text == text
        assert "rodne_cislo" in result.detector_names
        assert result.processing_time_ms >= 0

    def test_detect_czech_ico(self):
        gateway = PrivacyGateway(regions=["cz"])
        text = "Company IČO: 25596641"

        result = gateway.detect(text)

        assert len(result.findings) >= 1
        assert any(f.type == "ico" for f in result.findings)

    def test_detect_with_specific_detector(self):
        gateway = PrivacyGateway(regions=["cz"])
        text = "IČO: 25596641, RČ: 8001011234"

        result = gateway.detect(text, detector_names=["ico"])

        assert len(result.findings) >= 1
        assert all(f.type == "ico" for f in result.findings)

    def test_validate_czech_rodne_cislo(self):
        gateway = PrivacyGateway(regions=["cz"])

        result = gateway.validate("8001011234", "rodne_cislo")

        assert result.detector == "rodne_cislo"
        assert result.value == "8001011234"
        assert result.is_valid is True

    def test_validate_invalid_rodne_cislo(self):
        gateway = PrivacyGateway(regions=["cz"])

        result = gateway.validate("8001011235", "rodne_cislo")

        assert result.is_valid is False

    def test_validate_czech_ico(self):
        gateway = PrivacyGateway(regions=["cz"])

        result = gateway.validate("25596641", "ico")

        assert result.detector == "ico"
        assert result.is_valid is True

    def test_register_custom_detector(self):
        from cpg.detectors.base import Detector

        class CustomDetector(Detector):
            def __init__(self):
                super().__init__(name="custom", region="test")

            def detect(self, text: str) -> list[Finding]:
                return []

            def validate(self, value: str) -> bool:
                return value == "test"

        gateway = PrivacyGateway()
        custom_detector = CustomDetector()

        gateway.register_detector(custom_detector)

        retrieved = gateway.get_detector("custom")
        assert retrieved == custom_detector

    def test_detect_no_pii_in_clean_text(self):
        gateway = PrivacyGateway(regions=["cz"])
        text = "Hello world, no personal information here"

        result = gateway.detect(text)

        assert len(result.findings) == 0
        assert result.detector_names == []

    def test_detect_multiple_pii_types(self):
        gateway = PrivacyGateway(regions=["cz"])
        text = "IČO: 25596641, RČ: 8001011234"

        result = gateway.detect(text)

        assert len(result.findings) >= 2
        detector_types = {f.type for f in result.findings}
        assert "ico" in detector_types or "rodne_cislo" in detector_types