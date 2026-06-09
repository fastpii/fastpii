from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastpii.models import Finding


@dataclass
class DetectorMetadata:
    name: str
    region: str
    description: str


class Detector(ABC):
    name: str
    region: str
    description: str

    def __init__(
        self,
        name: str,
        region: str,
        description: str = ""
    ) -> None:
        self.name = name
        self.region = region
        self.description = description

    @abstractmethod
    def detect(self, text: str) -> list[Finding]:
        raise NotImplementedError

    @abstractmethod
    def validate(self, value: str) -> bool:
        raise NotImplementedError
