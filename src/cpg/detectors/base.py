from abc import ABC, abstractmethod
from dataclasses import dataclass

from cpg.models import Finding


@dataclass
class DetectorMetadata:
    name: str
    region: str
    description: str


class Detector(ABC):
    def __init__(
        self,
        name: str,
        region: str,
        description: str = ""
    ):
        self.name = name
        self.region = region
        self.description = description

    @abstractmethod
    def detect(self, text: str) -> list[Finding]:
        raise NotImplementedError

    @abstractmethod
    def validate(self, value: str) -> bool:
        raise NotImplementedError