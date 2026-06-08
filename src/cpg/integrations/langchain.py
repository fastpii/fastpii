from typing import Any

from cpg import PrivacyGateway


class PIIAnonymizer:
    def __init__(self, regions: list[str] | None = None):
        self.gateway = PrivacyGateway(regions=regions or ["cz"])

    def anonymize(self, text: str, replacement: str = "[REDACTED]") -> str:
        result = self.gateway.detect(text)
        
        anonymized = list(text)
        
        for finding in reversed(result.findings):
            start = finding.start
            end = finding.end
            anonymized[start:end] = list(replacement)
        
        return "".join(anonymized)

    def __call__(self, text: str) -> str:
        return self.anonymize(text)


class PIIPreprocessor:
    def __init__(self, regions: list[str] | None = None):
        self.gateway = PrivacyGateway(regions=regions or ["cz"])

    def preprocess(self, text: str, action: str = "redact") -> str:
        if action not in ["redact", "mask", "remove"]:
            raise ValueError(f"Invalid action: {action}. Must be one of: redact, mask, remove")
        
        result = self.gateway.detect(text)
        
        processed = list(text)
        
        for finding in reversed(result.findings):
            start = finding.start
            end = finding.end
            
            if action == "redact":
                processed[start:end] = list(f"[{finding.type.upper()}]")
            elif action == "mask":
                processed[start:end] = list("*" * len(finding.value))
            elif action == "remove":
                processed[start:end] = []
        
        return "".join(processed)

    def __call__(self, text: str) -> str:
        return self.preprocess(text)


def create_pii_filter_tool():
    from langchain.tools import BaseTool
    from pydantic import Field

    class PIIFilterTool(BaseTool):
        name = "pii_filter"
        description = "Detect and redact PII (Personally Identifiable Information) from text. Use before sending user input to external services or LLMs."
        regions: list[str] = Field(default_factory=lambda: ["cz"])
        
        def _run(self, text: str) -> str:
            anonymizer = PIIAnonymizer(regions=self.regions)
            return anonymizer.anonymize(text)
        
        async def _arun(self, text: str) -> str:
            return self._run(text)

    return PIIFilterTool()