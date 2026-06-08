from typing import Iterator

from fastpii.detectors.base import Detector


class DetectorRegistry:
    def __init__(self) -> None:
        self._detectors: dict[str, Detector] = {}

    def register(self, detector: Detector) -> None:
        self._detectors[detector.name] = detector

    def get(self, name: str) -> Detector:
        return self._detectors[name]

    def list(self) -> list[Detector]:
        return list(self._detectors.values())

    def count(self) -> int:
        return len(self._detectors)

    def iter_enabled(self) -> Iterator[Detector]:
        return iter(self._detectors.values())