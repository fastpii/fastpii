import pytest

from fastpii.detectors.base import Detector
from fastpii.models import Finding


class MockDetector(Detector):
    def __init__(self):
        super().__init__(
            name="mock",
            region="test",
            description="Mock detector for testing"
        )

    def detect(self, text: str) -> list[Finding]:
        return [
            Finding(
                type="mock_id",
                value="12345",
                start=0,
                end=5,
                confidence=1.0,
                region="test"
            )
        ]

    def validate(self, value: str) -> bool:
        return value == "12345"


class TestDetectorBase:
    def test_detector_creation(self):
        detector = MockDetector()

        assert detector.name == "mock"
        assert detector.region == "test"
        assert detector.description == "Mock detector for testing"

    def test_detector_detect_returns_findings(self):
        detector = MockDetector()
        findings = detector.detect("12345 test string")

        assert len(findings) == 1
        assert findings[0].type == "mock_id"
        assert findings[0].value == "12345"

    def test_detector_validate(self):
        detector = MockDetector()

        assert detector.validate("12345") is True
        assert detector.validate("54321") is False


class TestDetectorRegistry:
    def test_registry_creation(self):
        from fastpii.detectors.registry import DetectorRegistry

        registry = DetectorRegistry()

        assert registry.count() == 0

    def test_registry_register_detector(self):
        from fastpii.detectors.registry import DetectorRegistry

        registry = DetectorRegistry()
        detector = MockDetector()

        registry.register(detector)

        assert registry.count() == 1
        assert registry.get("mock") == detector

    def test_registry_get_detector(self):
        from fastpii.detectors.registry import DetectorRegistry

        registry = DetectorRegistry()
        detector = MockDetector()
        registry.register(detector)

        retrieved = registry.get("mock")

        assert retrieved == detector

    def test_registry_list_detectors(self):
        from fastpii.detectors.registry import DetectorRegistry

        registry = DetectorRegistry()
        detector = MockDetector()
        registry.register(detector)

        detectors = registry.list()

        assert len(detectors) == 1
        assert detectors[0] == detector

    def test_registry_get_nonexistent_detector(self):
        from fastpii.detectors.registry import DetectorRegistry

        registry = DetectorRegistry()

        with pytest.raises(KeyError):
            registry.get("nonexistent")

    def test_registry_iter_enabled(self):
        from fastpii.detectors.registry import DetectorRegistry

        registry = DetectorRegistry()
        detector = MockDetector()
        registry.register(detector)

        enabled_detectors = list(registry.iter_enabled())

        assert len(enabled_detectors) == 1
        assert enabled_detectors[0] == detector