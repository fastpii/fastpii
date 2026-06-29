from time import perf_counter
from typing import Any, cast

from fastpii.countries import CountryPack
from fastpii.core.confidence import ConfidenceScorer
from fastpii.core.overlap import deduplicate_findings
from fastpii.core.transform import (
    AnonymizeStrategy,
    RedactStrategy,
    MaskStrategy,
    RemoveStrategy,
    TransformationEngine,
)
from fastpii.detectors.base import Detector
from fastpii.detectors.registry import DetectorRegistry
from fastpii.models import Finding, DetectionResult, ValidationResult


__all__ = [
    "FastPII",
    "DEFAULT_PRIORITY",
    "DEFAULT_CONFIDENCE_SCORES",
    "DEFAULT_CONTEXT_BOOST",
]


class FastPII:
    registry: DetectorRegistry
    _priority: dict[str, int]
    _scorer: ConfidenceScorer | None

    def __init__(
        self,
        *,
        priority: dict[str, int] | None = None,
        confidence_scorer: ConfidenceScorer | None = None,
    ) -> None:
        self.registry = DetectorRegistry()
        if priority is None:
            raise ValueError(
                "Overlap priority is required. "
                "Pass a dict mapping detector type names to integer priorities. "
                "Higher priority types win when findings overlap. "
                "Example: {'rodne_cislo': 100, 'ico': 95, 'address': 80, 'phone': 20}"
            )
        self._priority = priority
        self._scorer = confidence_scorer

    def register(self, pack: CountryPack) -> None:
        from fastpii.patterns.registry import get_shared_registry

        pattern_registry = get_shared_registry()
        pack.register_patterns(pattern_registry)
        pack.register_detectors(self.registry)

    def register_many(self, packs: list[CountryPack]) -> None:
        for pack in packs:
            self.register(pack)

    def detect(self, text: str, detector_names: list[str] | None = None) -> DetectionResult:
        start_time = perf_counter()

        detectors = (
            [self.registry.get(name) for name in detector_names]
            if detector_names
            else list(self.registry.iter_enabled())
        )

        all_findings: list[Finding] = []

        for detector in detectors:
            findings = detector.detect(text)
            if findings:
                all_findings.extend(findings)

        all_findings = deduplicate_findings(all_findings, priority=self._priority)

        detector_list = list(dict.fromkeys(f.type for f in all_findings))

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

        metadata: dict[str, object] = {}
        metadata_getter: Any = getattr(detector, "_extract_metadata", None)
        if callable(metadata_getter):
            metadata = cast(dict[str, object], metadata_getter(value))

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

    def anonymize(self, text: str, replacement: str = "[REDACTED]") -> str:
        result = self.detect(text)
        return TransformationEngine.apply(result, AnonymizeStrategy(replacement))

    def redact(self, text: str) -> str:
        result = self.detect(text)
        return TransformationEngine.apply(result, RedactStrategy())

    def mask(self, text: str) -> str:
        result = self.detect(text)
        return TransformationEngine.apply(result, MaskStrategy())

    def remove(self, text: str) -> str:
        result = self.detect(text)
        return TransformationEngine.apply(result, RemoveStrategy())


DEFAULT_PRIORITY: dict[str, int] = {
    "rodne_cislo": 100, "pesel": 100, "steuer_id": 100, "siren": 100, "insee": 100,
    "ico": 95, "nip": 95, "ust_id": 95, "siret": 95,
    "dic": 90, "regon": 90, "handelsregister": 90,
    "bank_account": 85,
    "address": 80,
    "email": 70,
    "date_of_birth": 60, "date": 60,
    "name": 50,
    "postal_code": 40,
    "vehicle_plate": 30,
    "phone": 20,
}

DEFAULT_CONFIDENCE_SCORES: dict[str, float] = {
    "checksum_validated": 1.0,
    "context_match": 0.95,
    "pattern_match": 0.85,
    "no_context": 0.70,
}

DEFAULT_CONTEXT_BOOST: float = 0.10
