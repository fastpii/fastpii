from fastpii import (
    FastPII,
    Finding,
    DEFAULT_PRIORITY,
    DEFAULT_CONFIDENCE_SCORES,
    DEFAULT_CONTEXT_BOOST,
)
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.cz import CzechPack
from fastpii.countries.pl import PolishPack


def make_engine(*packs):
    engine = FastPII(
        priority=DEFAULT_PRIORITY,
        confidence_scorer=ConfidenceScorer(
            base_scores=DEFAULT_CONFIDENCE_SCORES,
            context_boost=DEFAULT_CONTEXT_BOOST,
        ),
    )
    if packs:
        engine.register_many(list(packs))
    return engine


class TestFastPIIEngine:
    def test_explicit_engine_starts_empty(self):
        engine = FastPII(priority=DEFAULT_PRIORITY)

        assert engine.list_detectors() == []

    def test_explicit_engine_registers_single_pack(self):
        engine = make_engine(CzechPack())

        detectors = engine.list_detectors()

        assert len(detectors) >= 1
        assert all(detector.region == "cz" for detector in detectors)

    def test_explicit_engine_registers_multiple_packs(self):
        engine = make_engine(CzechPack(), PolishPack())

        regions = {detector.region for detector in engine.list_detectors()}

        assert "cz" in regions
        assert "pl" in regions

    def test_explicit_engine_detects_only_registered_regions(self):
        engine = make_engine(PolishPack())

        result = engine.detect("PESEL: 44051401458")

        assert any(f.type == "pesel" for f in result.findings)
        assert all(f.region == "pl" for f in result.findings)

    def test_engine_creation_with_czech_region(self):
        gateway = make_engine(CzechPack())

        detectors = gateway.list_detectors()

        assert len(detectors) >= 1

    def test_engine_creation_with_no_regions_starts_empty(self):
        gateway = FastPII(priority=DEFAULT_PRIORITY)

        detectors = gateway.list_detectors()

        assert detectors == []

    def test_detect_czech_rodne_cislo(self):
        gateway = make_engine(CzechPack())
        text = "Jan Novák, RČ: 8001011238"

        result = gateway.detect(text)

        assert len(result.findings) >= 1
        assert result.text == text
        assert "rodne_cislo" in result.detector_names
        assert result.processing_time_ms >= 0

    def test_detect_czech_ico(self):
        gateway = make_engine(CzechPack())
        text = "Company IČO: 25596641"

        result = gateway.detect(text)

        assert len(result.findings) >= 1
        assert any(f.type == "ico" for f in result.findings)

    def test_detect_with_specific_detector(self):
        gateway = make_engine(CzechPack())
        text = "IČO: 25596641, RČ: 8001011238"

        result = gateway.detect(text, detector_names=["ico"])

        assert len(result.findings) >= 1
        assert all(f.type == "ico" for f in result.findings)

    def test_validate_czech_rodne_cislo(self):
        gateway = make_engine(CzechPack())

        result = gateway.validate("8001011238", "rodne_cislo")

        assert result.detector == "rodne_cislo"
        assert result.value == "8001011238"
        assert result.is_valid is True

    def test_validate_invalid_rodne_cislo(self):
        gateway = make_engine(CzechPack())

        result = gateway.validate("8001011235", "rodne_cislo")

        assert result.is_valid is False

    def test_validate_czech_ico(self):
        gateway = make_engine(CzechPack())

        result = gateway.validate("25596641", "ico")

        assert result.detector == "ico"
        assert result.is_valid is True

    def test_register_custom_detector(self):
        from fastpii.detectors.base import Detector

        class CustomDetector(Detector):
            def __init__(self):
                super().__init__(name="custom", region="test")

            def detect(self, text: str) -> list[Finding]:
                return []

            def validate(self, value: str) -> bool:
                return value == "test"

        gateway = FastPII(priority=DEFAULT_PRIORITY)
        custom_detector = CustomDetector()

        gateway.register_detector(custom_detector)

        retrieved = gateway.get_detector("custom")
        assert retrieved == custom_detector

    def test_detect_no_pii_in_clean_text(self):
        gateway = make_engine(CzechPack())
        text = "Hello world, no personal information here"

        result = gateway.detect(text)

        assert len(result.findings) == 0
        assert result.detector_names == []

    def test_detect_multiple_pii_types(self):
        gateway = make_engine(CzechPack())
        text = "IČO: 25596641, RČ: 8001011238"

        result = gateway.detect(text)

        assert len(result.findings) >= 2
        detector_types = {f.type for f in result.findings}
        assert "ico" in detector_types or "rodne_cislo" in detector_types
