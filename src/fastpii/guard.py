from time import perf_counter
from typing import Protocol, cast

from fastpii.detectors.base import Detector
from fastpii.detectors.registry import DetectorRegistry
from fastpii.models import Finding, DetectionResult, ValidationResult


class _MetadataExtractor(Protocol):
    def _extract_metadata(self, value: str) -> dict[str, object]: ...


class PrivacyGuard:
    registry: DetectorRegistry
    _regions: list[str]

    def __init__(self, regions: list[str] | None = None) -> None:
        self.registry = DetectorRegistry()
        self._regions = regions or []
        self._register_default_detectors()

    def _register_default_detectors(self) -> None:
        if "cz" in self._regions or not self._regions:
            from fastpii.detectors.cz.rodne_cislo import RodneCisloDetector
            from fastpii.detectors.cz.ico import ICODetector
            from fastpii.detectors.cz.dic import DICDetector
            from fastpii.detectors.cz.bank_account import BankAccountDetector
            from fastpii.detectors.cz.postal_code import PostalCodeDetector
            from fastpii.detectors.cz.phone import PhoneNumberDetector
            from fastpii.detectors.cz.email import EmailDetector
            from fastpii.detectors.cz.name import NameDetector
            from fastpii.detectors.cz.address import AddressDetector
            from fastpii.detectors.cz.date_of_birth import DateOfBirthDetector
            from fastpii.detectors.cz.vehicle_plate import VehiclePlateDetector

            self.registry.register(RodneCisloDetector())
            self.registry.register(ICODetector())
            self.registry.register(DICDetector())
            self.registry.register(BankAccountDetector())
            self.registry.register(PostalCodeDetector())
            self.registry.register(PhoneNumberDetector())
            self.registry.register(EmailDetector())
            self.registry.register(NameDetector())
            self.registry.register(AddressDetector())
            self.registry.register(DateOfBirthDetector())
            self.registry.register(VehiclePlateDetector())

    def detect(self, text: str, detector_names: list[str] | None = None) -> DetectionResult:
        start_time = perf_counter()

        detectors = (
            [self.registry.get(name) for name in detector_names]
            if detector_names
            else list(self.registry.iter_enabled())
        )

        all_findings: list[Finding] = []
        detector_list: list[str] = []

        for detector in detectors:
            findings = detector.detect(text)
            if findings:
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

        metadata: dict[str, object] = {}
        if hasattr(detector, '_extract_metadata'):
            metadata = cast(_MetadataExtractor, cast(object, detector))._extract_metadata(value)

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
        """
        Replace all detected PII with a placeholder.
        
        Args:
            text: Input text containing PII
            replacement: Custom replacement string (default: "[REDACTED]")
        
        Returns:
            Text with PII replaced by placeholder
            
        Example:
            >>> guard = PrivacyGuard(regions=["cz"])
            >>> guard.anonymize("Email: jan@email.cz")
            'Email: [REDACTED]'
        """
        result = self.detect(text)
        
        anonymized = list(text)
        
        # Sort by position (descending) and process in reverse to maintain correct indices
        for finding in sorted(result.findings, key=lambda f: f.start, reverse=True):
            anonymized[finding.start:finding.end] = list(replacement)
        
        return "".join(anonymized)
    
    def redact(self, text: str) -> str:
        """
        Replace detected PII with type-based placeholders.
        
        Args:
            text: Input text containing PII
        
        Returns:
            Text with PII replaced by type (e.g., [EMAIL], [RODNE_CISLO])
            
        Example:
            >>> guard = PrivacyGuard(regions=["cz"])
            >>> guard.redact("Email: jan@email.cz, RČ: 8001011238")
            'Email: [EMAIL], RČ: [RODNE_CISLO]'
        """
        result = self.detect(text)
        
        processed = list(text)
        
        # Sort by position (descending) and process in reverse to maintain correct indices
        for finding in sorted(result.findings, key=lambda f: f.start, reverse=True):
            processed[finding.start:finding.end] = list(f"[{finding.type.upper()}]")
        
        return "".join(processed)
    
    def mask(self, text: str) -> str:
        """
        Replace detected PII with asterisks matching original length.
        
        Args:
            text: Input text containing PII
        
        Returns:
            Text with PII replaced by asterisks
            
        Example:
            >>> guard = PrivacyGuard(regions=["cz"])
            >>> guard.mask("Email: jan@email.cz")
            'Email: *************'
        """
        result = self.detect(text)
        
        processed = list(text)
        
        # Sort by position (descending) and process in reverse to maintain correct indices
        for finding in sorted(result.findings, key=lambda f: f.start, reverse=True):
            processed[finding.start:finding.end] = list("*" * len(finding.value))
        
        return "".join(processed)
    
    def remove(self, text: str) -> str:
        """
        Remove all detected PII from text.
        
        Args:
            text: Input text containing PII
        
        Returns:
            Text with PII removed entirely
            
        Example:
            >>> guard = PrivacyGuard(regions=["cz"])
            >>> guard.remove("Email: jan@email.cz")
            'Email: '
        """
        result = self.detect(text)
        
        processed = list(text)
        
        # Sort by position (descending) and process in reverse to maintain correct indices
        for finding in sorted(result.findings, key=lambda f: f.start, reverse=True):
            processed[finding.start:finding.end] = []
        
        return "".join(processed)
