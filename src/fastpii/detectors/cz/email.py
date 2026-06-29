import re
from typing import ClassVar

from fastpii.core._compat import override
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class EmailDetector(Detector):

    CZECH_TLDS: set[str] = {'.cz', '.sk'}
    CZECH_DOMAIN_CONFIDENCE: float = 0.95
    OTHER_DOMAIN_CONFIDENCE: float = 0.85
    registry: PatternRegistry

    MARKDOWN_MAILTO_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        (
            r'\[([A-Za-z0-9áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\]'
            + r'\(mailto:([A-Za-z0-9áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\)'
        )
    )

    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="email",
            region="cz",
            description="Email address detector with Czech domain awareness"
        )
        self.registry = registry or get_shared_registry()

    @override
    def detect(self, text: str) -> list[Finding]:
        patterns = self.registry.get_patterns("email", "cz")
        if not patterns:
            return []

        pattern_def = patterns[0]
        findings: list[Finding] = []

        mailto_spans: list[tuple[int, int]] = []
        for m in self.MARKDOWN_MAILTO_PATTERN.finditer(text):
            mailto_start = m.start(2) - len("mailto:")
            mailto_end = m.end(2) + 1
            mailto_spans.append((mailto_start, mailto_end))

        for match in pattern_def.compiled.finditer(text):
            email = match.group(0)
            match_start = match.start()
            match_end = match.end()

            in_mailto = False
            for ms, me in mailto_spans:
                if match_start >= ms and match_end <= me:
                    in_mailto = True
                    break

            if in_mailto:
                continue

            if self._is_valid_email(email):
                metadata = self._extract_metadata(email)
                is_czech = self._is_czech_domain(email)

                findings.append(Finding(
                    type="email",
                    value=email,
                    start=match_start,
                    end=match_end,
                    confidence=self.CZECH_DOMAIN_CONFIDENCE if is_czech else self.OTHER_DOMAIN_CONFIDENCE,
                    region="cz" if is_czech else "generic",
                    metadata=metadata
                ))

        return findings

    @override
    def validate(self, value: str) -> bool:
        return self._is_valid_email(value)

    def _is_valid_email(self, email: str) -> bool:
        if '@' not in email:
            return False

        parts = email.split('@')
        if len(parts) != 2:
            return False

        local_part, domain = parts

        if len(local_part) == 0 or len(local_part) > 64:
            return False

        if len(domain) == 0 or len(domain) > 255:
            return False

        if '.' not in domain:
            return False

        if '..' in email:
            return False

        return True

    def _is_czech_domain(self, email: str) -> bool:
        email_lower = email.lower()
        return any(email_lower.endswith(tld) for tld in self.CZECH_TLDS)

    def _extract_metadata(self, email: str) -> dict[str, object]:
        metadata: dict[str, object] = {}

        local_part, domain = email.split('@')

        metadata['local_part'] = local_part
        metadata['domain'] = domain.lower()
        metadata['is_czech_domain'] = self._is_czech_domain(email)

        domain_lower = domain.lower()
        if 'gmail' in domain_lower:
            metadata['provider'] = 'gmail'
        elif 'seznam' in domain_lower:
            metadata['provider'] = 'seznam'
        elif 'centrum' in domain_lower or 'centrum.cz' in domain_lower:
            metadata['provider'] = 'centrum'
        elif 'email' in domain_lower or 'email.cz' in domain_lower:
            metadata['provider'] = 'email'
        elif 'outlook' in domain_lower or 'hotmail' in domain_lower or 'live' in domain_lower:
            metadata['provider'] = 'microsoft'
        elif 'yahoo' in domain_lower:
            metadata['provider'] = 'yahoo'

        return metadata
