"""
Transformation engine for PII text replacement.

Provides a strategy-based architecture for transforming detected PII
in text. Each strategy defines how an individual finding is replaced.

Strategies:
    AnonymizeStrategy — Replace with a fixed placeholder (default: [REDACTED])
    RedactStrategy     — Replace with the PII type label (e.g., [EMAIL])
    MaskStrategy       — Replace with asterisks preserving original span length
    RemoveStrategy     — Delete the PII span entirely

Custom strategies can be created by implementing the TransformationStrategy protocol.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from fastpii.models import DetectionResult, Finding


__all__ = [
    "AnonymizeStrategy",
    "RedactStrategy",
    "MaskStrategy",
    "RemoveStrategy",
    "TransformationEngine",
]


@runtime_checkable
class TransformationStrategy(Protocol):
    """Protocol for PII transformation strategies.

    A strategy receives a Finding and the original text, and returns
    the replacement string for that finding's span.
    """

    def replace(self, finding: Finding, text: str) -> str:
        """Return the replacement string for the given finding.

        Args:
            finding: The detected PII finding with start, end, type, etc.
            text: The original input text (for context if needed).

        Returns:
            The string to insert at text[start:end].
        """
        ...


class AnonymizeStrategy:
    """Replace PII with a fixed placeholder string."""

    def __init__(self, replacement: str = "[REDACTED]") -> None:
        self.replacement: str = replacement

    def replace(self, finding: Finding, text: str) -> str:
        _ = finding, text
        return self.replacement


class RedactStrategy:
    """Replace PII with its type label in brackets."""

    def replace(self, finding: Finding, text: str) -> str:
        _ = text
        return f"[{finding.type.upper()}]"


class MaskStrategy:
    """Replace PII with asterisks, preserving the original text span length."""

    def replace(self, finding: Finding, text: str) -> str:
        _ = text
        return "*" * max(0, finding.end - finding.start)


class RemoveStrategy:
    """Remove PII entirely from the text."""

    def replace(self, finding: Finding, text: str) -> str:
        _ = finding, text
        return ""


class TransformationEngine:
    """Engine that applies a transformation strategy to all findings in text.

    Processes findings in reverse order (by start position) so that
    replacements don't shift subsequent character positions.

    Usage:
        engine = FastPII(priority={...})
        engine.register(CzechPack())

        # Use convenience methods
        engine.anonymize(text)
        engine.redact(text)

        # Or apply a custom strategy
        from fastpii.core.transform import TransformationEngine, AnonymizeStrategy
        custom = AnonymizeStrategy(replacement="<PII>")
        TransformationEngine.apply(engine.detect(text), custom)
    """

    @staticmethod
    def apply(
        result: DetectionResult,
        strategy: TransformationStrategy,
    ) -> str:
        """Apply a transformation strategy to all findings in the detection result.

        Args:
            result: DetectionResult containing the original text and findings.
            strategy: The transformation strategy to apply.

        Returns:
            The transformed text with all findings replaced according to the strategy.
        """
        if not result.text or not result.findings:
            return result.text

        processed = list(result.text)
        text_length = len(result.text)

        for finding in sorted(result.findings, key=lambda f: f.start, reverse=True):
            start = finding.start
            end = finding.end

            if start < 0 or end < 0 or start >= text_length or start > end:
                continue

            end = min(end, text_length)
            if start == end:
                continue

            safe_finding = finding
            if end != finding.end:
                safe_finding = Finding(
                    type=finding.type,
                    value=result.text[start:end],
                    start=start,
                    end=end,
                    confidence=finding.confidence,
                    region=finding.region,
                    metadata=finding.metadata,
                )

            replacement = strategy.replace(safe_finding, result.text)
            processed[start:end] = list(replacement)
        return "".join(processed)
