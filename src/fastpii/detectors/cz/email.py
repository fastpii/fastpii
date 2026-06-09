"""Email Address Detector.

Detects email addresses with Czech domain prioritization and basic validation.
"""

from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., object])

try:
    from typing_extensions import override
except ImportError:
    def override(method: F, /) -> F:
        return method

from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns import PatternRegistry, get_shared_registry


class EmailDetector(Detector):
    """Email address detector with validation."""
    
    # Czech domain TLDs
    CZECH_TLDS: set[str] = {'.cz', '.sk'}
    registry: PatternRegistry
    
    def __init__(self, registry: PatternRegistry | None = None) -> None:
        super().__init__(
            name="email",
            region="cz",  # Generic but Czech context-aware
            description="Email address detector with Czech domain awareness"
        )
        # Use shared registry if none provided (singleton pattern)
        self.registry = registry or get_shared_registry()
    
    @override
    def detect(self, text: str) -> list[Finding]:
        """Detect email addresses in text."""
        patterns = self.registry.get_patterns("email", "cz")
        if not patterns:
            return []
        
        pattern_def = patterns[0]  # Use the standard pattern
        findings: list[Finding] = []
        
        for match in pattern_def.compiled.finditer(text):
            email = match.group(0)
            
            # Validate email format
            if self._is_valid_email(email):
                metadata = self._extract_metadata(email)
                
                findings.append(Finding(
                    type="email",
                    value=email,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95 if self._is_czech_domain(email) else 0.85,
                    region="cz" if self._is_czech_domain(email) else "generic",
                    metadata=metadata
                ))
        
        return findings
    
    @override
    def validate(self, value: str) -> bool:
        """Validate email address format."""
        return self._is_valid_email(value)
    
    def _is_valid_email(self, email: str) -> bool:
        """Check if email has valid format."""
        # Basic checks
        if '@' not in email:
            return False
        
        parts = email.split('@')
        if len(parts) != 2:
            return False
        
        local_part, domain = parts
        
        # Local part checks
        if len(local_part) == 0 or len(local_part) > 64:
            return False
        
        # Domain checks
        if len(domain) == 0 or len(domain) > 255:
            return False
        
        # Domain must have at least one dot
        if '.' not in domain:
            return False
        
        # No consecutive dots
        if '..' in email:
            return False
        
        return True
    
    def _is_czech_domain(self, email: str) -> bool:
        """Check if email has Czech domain."""
        email_lower = email.lower()
        return any(email_lower.endswith(tld) for tld in self.CZECH_TLDS)
    
    def _extract_metadata(self, email: str) -> dict[str, object]:
        """Extract metadata from email."""
        metadata: dict[str, object] = {}
        
        local_part, domain = email.split('@')
        
        metadata['local_part'] = local_part
        metadata['domain'] = domain.lower()
        metadata['is_czech_domain'] = self._is_czech_domain(email)
        
        # Detect common email providers
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
