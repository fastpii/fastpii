from dataclasses import asdict

import pytest

from fastpii.models import Finding, DetectionResult, ValidationResult


class TestFinding:

    def test_finding_creation_with_required_fields(self):
        finding = Finding(
            type="rodne_cislo",
            value="8001011234",
            start=0,
            end=10,
            confidence=0.95,
            region="cz"
        )

        assert finding.type == "rodne_cislo"
        assert finding.value == "8001011234"
        assert finding.start == 0
        assert finding.end == 10
        assert finding.confidence == 0.95
        assert finding.region == "cz"
        assert finding.metadata == {}

    def test_finding_with_metadata(self):
        metadata = {
            "checksum_valid": True,
            "birth_date": "1980-01-01",
            "gender": "male",
            "article_9": True
        }

        finding = Finding(
            type="rodne_cislo",
            value="8001011234",
            start=0,
            end=10,
            confidence=0.95,
            region="cz",
            metadata=metadata
        )

        assert finding.metadata == metadata
        assert finding.metadata["checksum_valid"] is True
        assert finding.metadata["article_9"] is True

    def test_finding_to_dict(self):
        finding = Finding(
            type="ico",
            value="25596641",
            start=5,
            end=13,
            confidence=1.0,
            region="cz",
            metadata={"checksum_valid": True}
        )

        result = asdict(finding)

        assert result["type"] == "ico"
        assert result["value"] == "25596641"
        assert result["checksum_valid"] is True


class TestDetectionResult:
    def test_detection_result_creation(self):
        findings = [
            Finding(type="ico", value="25596641", start=5, end=13, confidence=1.0, region="cz")
        ]

        result = DetectionResult(
            text="My ICO is 25596641",
            findings=findings,
            detector_names=["ico"],
            processing_time_ms=15
        )

        assert result.text == "My ICO is 25596641"
        assert len(result.findings) == 1
        assert result.findings[0].type == "ico"
        assert result.detector_names == ["ico"]
        assert result.processing_time_ms == 15

    def test_empty_detection_result(self):
        result = DetectionResult(
            text="No PII here",
            findings=[],
            detector_names=[],
            processing_time_ms=5
        )

        assert result.text == "No PII here"
        assert len(result.findings) == 0
        assert result.detector_names == []

    def test_detection_result_to_dict(self):
        findings = [
            Finding(type="rodne_cislo", value="8001011234", start=0, end=10, confidence=0.95, region="cz")
        ]

        result = DetectionResult(
            text="Test text",
            findings=findings,
            detector_names=["rodne_cislo"],
            processing_time_ms=10
        )

        result_dict = asdict(result)

        assert result_dict["text"] == "Test text"
        assert len(result_dict["findings"]) == 1
        assert result_dict["processing_time_ms"] == 10


class TestValidationResult:
    def test_validation_result_valid(self):
        result = ValidationResult(
            detector="ico",
            value="25596641",
            is_valid=True,
            metadata={"checksum_valid": True}
        )

        assert result.detector == "ico"
        assert result.value == "25596641"
        assert result.is_valid is True
        assert result.metadata["checksum_valid"] is True

    def test_validation_result_invalid(self):
        result = ValidationResult(
            detector="ico",
            value="12345678",
            is_valid=False,
            metadata={"checksum_valid": False, "error": "Invalid checksum"}
        )

        assert result.is_valid is False
        assert result.metadata["error"] == "Invalid checksum"

    def test_validation_result_without_metadata(self):
        result = ValidationResult(
            detector="rodne_cislo",
            value="8001011234",
            is_valid=True
        )

        assert result.metadata == {}

    def test_validation_result_to_dict(self):
        result = ValidationResult(
            detector="rodne_cislo",
            value="8001011234",
            is_valid=True,
            metadata={"birth_date": "1980-01-01"}
        )

        result_dict = asdict(result)

        assert result_dict["detector"] == "rodne_cislo"
        assert result_dict["is_valid"] is True
        assert result_dict["metadata"]["birth_date"] == "1980-01-01"


class TestFindingEqualityAndHashing:
    def test_finding_equality(self):
        finding1 = Finding(
            type="ico",
            value="25596641",
            start=5,
            end=13,
            confidence=1.0,
            region="cz"
        )

        finding2 = Finding(
            type="ico",
            value="25596641",
            start=5,
            end=13,
            confidence=1.0,
            region="cz"
        )

        assert finding1 == finding2

    def test_finding_inequality_different_values(self):
        finding1 = Finding(
            type="ico",
            value="25596641",
            start=5,
            end=13,
            confidence=1.0,
            region="cz"
        )

        finding2 = Finding(
            type="rodne_cislo",
            value="8001011234",
            start=0,
            end=10,
            confidence=0.95,
            region="cz"
        )

        assert finding1 != finding2

    def test_finding_immutability(self):
        finding = Finding(
            type="ico",
            value="25596641",
            start=5,
            end=13,
            confidence=1.0,
            region="cz"
        )

        with pytest.raises(AttributeError):
            finding.value = "12345678"