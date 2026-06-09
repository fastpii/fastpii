import importlib

from fastpii import PrivacyGuard


class PIIAnonymizer:
    """
    LangChain integration wrapper for PrivacyGuard anonymization.
    
    This class provides backwards compatibility with existing LangChain integrations
    while delegating to the core PrivacyGuard.anonymize() method.
    
    Note: For new code, prefer using PrivacyGuard directly:
        >>> from fastpii import PrivacyGuard
        >>> guard = PrivacyGuard(regions=["cz"])
        >>> guard.anonymize(text)
    """
    gateway: PrivacyGuard

    def __init__(self, regions: list[str] | None = None) -> None:
        self.gateway = PrivacyGuard(regions=regions or ["cz"])

    def anonymize(self, text: str, replacement: str = "[REDACTED]") -> str:
        """
        Alias for PrivacyGuard.anonymize() for backwards compatibility.
        
        Args:
            text: Input text containing PII
            replacement: Custom replacement string (default: "[REDACTED]")
        
        Returns:
            Text with PII replaced by placeholder
        """
        return self.gateway.anonymize(text, replacement)

    def __call__(self, text: str) -> str:
        return self.anonymize(text)


class PIIPreprocessor:
    """
    LangChain integration wrapper for PrivacyGuard preprocessing.
    
    This class provides backwards compatibility with existing LangChain integrations
    while delegating to core PrivacyGuard methods.
    
    Note: For new code, prefer using PrivacyGuard directly:
        >>> from fastpii import PrivacyGuard
        >>> guard = PrivacyGuard(regions=["cz"])
        >>> guard.redact(text)   # Type-based placeholders
        >>> guard.mask(text)     # Asterisks
        >>> guard.remove(text)   # Remove PII
    """
    gateway: PrivacyGuard

    def __init__(self, regions: list[str] | None = None) -> None:
        self.gateway = PrivacyGuard(regions=regions or ["cz"])

    def preprocess(self, text: str, action: str = "redact") -> str:
        """
        Preprocess text with specified action.
        
        Args:
            text: Input text containing PII
            action: One of "redact", "mask", or "remove"
        
        Returns:
            Text with PII processed according to action
            
        Raises:
            ValueError: If action is not one of the allowed values
        """
        if action == "redact":
            return self.gateway.redact(text)
        elif action == "mask":
            return self.gateway.mask(text)
        elif action == "remove":
            return self.gateway.remove(text)
        else:
            raise ValueError(f"Invalid action: {action}. Must be one of: redact, mask, remove")

    def __call__(self, text: str) -> str:
        return self.preprocess(text)


def create_pii_filter_tool() -> object:
    base_tool_module = importlib.import_module("langchain.tools")
    BaseTool = base_tool_module.BaseTool
    from pydantic import Field

    class PIIFilterTool(BaseTool):
        name: str = "pii_filter"
        description: str = "Detect and redact PII (Personally Identifiable Information) from text. Use before sending user input to external services or LLMs."
        regions: list[str] = Field(default_factory=lambda: ["cz"])
        
        def _run(self, text: str) -> str:
            anonymizer = PIIAnonymizer(regions=self.regions)
            return anonymizer.anonymize(text)
        
        async def _arun(self, text: str) -> str:
            return self._run(text)

    return PIIFilterTool()
