from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Finding:
    type: str
    value: str
    start: int
    end: int
    confidence: float
    region: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DetectionResult:
    text: str
    findings: list[Finding]
    detector_names: list[str]
    processing_time_ms: int


@dataclass
class ValidationResult:
    detector: str
    value: str
    is_valid: bool
    metadata: dict[str, Any] = field(default_factory=dict)