from time import perf_counter
from typing import Any

from cpg.detectors.base import Detector
from cpg.detectors.registry import DetectorRegistry
from cpg.models import Finding, DetectionResult, ValidationResult


class PrivacyGateway:
    def __init__(self, regions: list[str] | None = None) -> None:
        self.registry = DetectorRegistry()
        self._regions = regions or []
        self._register_default_detectors()

    def _register_default_detectors(self) -> None:
        if "cz" in self._regions or not self._regions:
            from cpg.detectors.cz.rodne_cislo import RodneCisloDetector
            from cpg.detectors.cz.ico import ICODetector
            from cpg.detectors.cz.dic import DICDetector

            self.registry.register(RodneCisloDetector())
            self.registry.register(ICODetector())
            self.registry.register(DICDetector())

    def detect(self, text: str, detector_names: list[str] | None = None) -> DetectionResult:
        start_time = perf_counter()

        detectors = (
            [self.registry.get(name) for name in detector_names]
            if detector_names
            else list(self.registry.iter_enabled())
        )

        all_findings: list[Finding] = []
        detector_list = []

        for detector in detectors:
            findings = detector.detect(text)
            all_findings.extend(findings)
            if detector.name not in detector_list:
                detector_list.append(detector.name)

        processing_time_ms = int((perf_counter() - start_time) * 1000)

        return DetectionResult(
            text=text,
            findings=all_findings,
            detector_names=detector_list,
            processing_time_ms=processing_time_ms
        )

    def validate(self, value: str, detector_name: str) -> ValidationResult:
        detector = self.registry.get(detector_name)

        is_valid = detector.validate(value)

        metadata: dict[str, Any] = {}
        if hasattr(detector, '_extract_metadata'):
            metadata = detector._extract_metadata(value)

        return ValidationResult(
            detector=detector_name,
            value=value,
            is_valid=is_valid,
            metadata=metadata
        )

    def register_detector(self, detector: Detector) -> None:
        self.registry.register(detector)

    def get_detector(self, name: str) -> Detector:
        return self.registry.get(name)

    def list_detectors(self) -> list[Detector]:
        return self.registry.list()