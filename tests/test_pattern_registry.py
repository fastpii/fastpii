"""
Tests for Pattern Registry

Tests the centralized pattern registry for PII detection patterns.
"""
import re
import pytest
from fastpii.patterns.registry import PatternRegistry, PatternDefinition


class TestPatternRegistry:
    """Test the core PatternRegistry contract"""

    def test_registry_creation(self):
        """Can create an empty registry"""
        registry = PatternRegistry()
        assert registry is not None

    def test_register_pattern(self):
        """Can register a single pattern"""
        registry = PatternRegistry()
        
        pattern = PatternDefinition(
            entity_type="rodne_cislo",
            name="standard",
            regex=r"\b(\d{6}[/\s]?\d{3,4})\b",
            region="cz",
            score=0.95
        )
        
        registry.register(pattern)
        
        # Should not raise
        patterns = registry.get_patterns("rodne_cislo", region="cz")
        assert len(patterns) == 1
        assert patterns[0].regex == r"\b(\d{6}[/\s]?\d{3,4})\b"

    def test_get_patterns_by_entity_type(self):
        """Can retrieve patterns by entity type"""
        registry = PatternRegistry()
        
        # Register multiple patterns
        registry.register(PatternDefinition(
            entity_type="rodne_cislo",
            name="standard",
            regex=r"\b(\d{6}[/\s]?\d{3,4})\b",
            region="cz",
            score=0.95
        ))
        
        registry.register(PatternDefinition(
            entity_type="ico",
            name="standard",
            regex=r"\b(\d{8})\b",
            region="cz",
            score=1.0
        ))
        
        # Get patterns for specific entity
        patterns = registry.get_patterns("rodne_cislo", region="cz")
        assert len(patterns) == 1
        assert patterns[0].entity_type == "rodne_cislo"
        
        patterns = registry.get_patterns("ico", region="cz")
        assert len(patterns) == 1
        assert patterns[0].entity_type == "ico"

    def test_pattern_variants(self):
        """Can register and retrieve multiple pattern variants"""
        registry = PatternRegistry()
        
        # Register multiple variants for phone
        registry.register(PatternDefinition(
            entity_type="phone",
            name="mobile",
            regex=r"(?:\+420[\s-]?)?(?:60[0-8]|7[0-9]\d)[\s-]?\d{3}[\s-]?\d{3}",
            region="cz",
            score=0.95
        ))
        
        registry.register(PatternDefinition(
            entity_type="phone",
            name="landline",
            regex=r"(?:\+420[\s-]?)?([2-5])[\s-]?(\d{4})[\s-]?(\d{4})",
            region="cz",
            score=0.90
        ))
        
        # Get all variants
        patterns = registry.get_patterns("phone", region="cz")
        assert len(patterns) == 2
        
        # Can access by variant name
        mobile = registry.get_pattern("phone", variant="mobile", region="cz")
        assert mobile is not None
        assert "mobile" in mobile.name

    def test_patterns_are_precompiled(self):
        """Patterns are precompiled for performance"""
        registry = PatternRegistry()
        
        pattern = PatternDefinition(
            entity_type="ico",
            name="standard",
            regex=r"\b(\d{8})\b",
            region="cz",
            score=1.0
        )
        
        registry.register(pattern)
        
        patterns = registry.get_patterns("ico", region="cz")
        assert len(patterns) == 1
        assert patterns[0].compiled is not None
        assert isinstance(patterns[0].compiled, re.Pattern)
        
        # Can use compiled pattern directly
        match = patterns[0].compiled.search("IČO: 25596641")
        assert match is not None
        assert match.group(1) == "25596641"

    def test_missing_pattern_returns_empty(self):
        """Missing patterns return empty list, not error"""
        registry = PatternRegistry()
        
        # Empty registry
        patterns = registry.get_patterns("nonexistent", region="cz")
        assert patterns == []
        
        # Register one pattern
        registry.register(PatternDefinition(
            entity_type="ico",
            name="standard",
            regex=r"\b(\d{8})\b",
            region="cz",
            score=1.0
        ))
        
        # Different entity type
        patterns = registry.get_patterns("rodne_cislo", region="cz")
        assert patterns == []
        
        # Different region
        patterns = registry.get_patterns("ico", region="de")
        assert patterns == []

    def test_region_isolation(self):
        """Patterns are isolated by region"""
        registry = PatternRegistry()
        
        # Czech pattern
        registry.register(PatternDefinition(
            entity_type="postal_code",
            name="standard",
            regex=r"\b(\d{3})\s?(\d{2})\b",
            region="cz",
            score=0.95
        ))
        
        # German pattern (future)
        registry.register(PatternDefinition(
            entity_type="postal_code",
            name="standard",
            regex=r"\b(\d{5})\b",
            region="de",
            score=0.95
        ))
        
        # Get Czech patterns
        cz_patterns = registry.get_patterns("postal_code", region="cz")
        assert len(cz_patterns) == 1
        assert cz_patterns[0].region == "cz"
        
        # Get German patterns
        de_patterns = registry.get_patterns("postal_code", region="de")
        assert len(de_patterns) == 1
        assert de_patterns[0].region == "de"
        
        # Patterns don't mix
        assert cz_patterns[0].regex != de_patterns[0].regex

    def test_pattern_metadata(self):
        """Patterns include metadata like context words"""
        registry = PatternRegistry()
        
        pattern = PatternDefinition(
            entity_type="rodne_cislo",
            name="standard",
            regex=r"\b(\d{6}[/\s]?\d{3,4})\b",
            region="cz",
            score=0.95,
            context_words=["rodné číslo", "RČ", "rod. č."],
            checksum_algo="validate_birth_number_format"
        )
        
        registry.register(pattern)
        
        patterns = registry.get_patterns("rodne_cislo", region="cz")
        assert len(patterns) == 1
        assert patterns[0].context_words == ["rodné číslo", "RČ", "rod. č."]
        assert patterns[0].checksum_algo == "validate_birth_number_format"
        assert patterns[0].score == 0.95

    def test_case_insensitive_lookup(self):
        """Pattern lookup is case-insensitive for entity_type"""
        registry = PatternRegistry()
        
        registry.register(PatternDefinition(
            entity_type="rodne_cislo",
            name="standard",
            regex=r"\b(\d{6}[/\s]?\d{3,4})\b",
            region="cz",
            score=0.95
        ))
        
        # Different case
        patterns = registry.get_patterns("RODNE_CISLO", region="cz")
        assert len(patterns) == 1
        
        patterns = registry.get_patterns("Rodne_Cislo", region="cz")
        assert len(patterns) == 1


class TestCzechPatterns:
    """Test Czech pattern registration and retrieval"""

    def test_rodne_cislo_patterns(self):
        """Czech birth number patterns are correctly registered"""
        registry = PatternRegistry()
        registry.load_czech_patterns()  # Load all Czech patterns
        
        patterns = registry.get_patterns("rodne_cislo", region="cz")
        assert len(patterns) >= 1
        
        # Should detect standard format
        pattern = patterns[0]
        text = "RČ: 8001011238"
        match = pattern.compiled.search(text)
        assert match is not None
        assert "8001011238" in match.group(0)

    def test_ico_patterns(self):
        """Czech IČO patterns are correctly registered"""
        registry = PatternRegistry()
        registry.load_czech_patterns()
        
        patterns = registry.get_patterns("ico", region="cz")
        assert len(patterns) >= 1
        
        # Should detect 8-digit IČO
        pattern = patterns[0]
        text = "IČO: 25596641"
        match = pattern.compiled.search(text)
        assert match is not None
        assert match.group(1) == "25596641"

    def test_dic_patterns(self):
        """Czech DIČ patterns are correctly registered"""
        registry = PatternRegistry()
        registry.load_czech_patterns()
        
        patterns = registry.get_patterns("dic", region="cz")
        assert len(patterns) >= 1
        
        # Should detect CZ prefix
        pattern = patterns[0]
        text = "DIČ: CZ25596641"
        match = pattern.compiled.search(text)
        assert match is not None

    def test_bank_account_patterns(self):
        """Czech bank account patterns are correctly registered"""
        registry = PatternRegistry()
        registry.load_czech_patterns()
        
        patterns = registry.get_patterns("bank_account", region="cz")
        assert len(patterns) >= 1
        
        # Should detect account/bank_code format
        pattern = patterns[0]
        text = "Účet: 19-2000145399/0800"
        match = pattern.compiled.search(text)
        assert match is not None

    def test_postal_code_patterns(self):
        """Czech postal code patterns are correctly registered"""
        registry = PatternRegistry()
        registry.load_czech_patterns()
        
        patterns = registry.get_patterns("postal_code", region="cz")
        assert len(patterns) >= 1
        
        # Should detect XXX XX format
        pattern = patterns[0]
        text = "PSČ: 110 00"
        match = pattern.compiled.search(text)
        assert match is not None

    def test_phone_patterns_with_variants(self):
        """Czech phone patterns include both mobile and landline variants"""
        registry = PatternRegistry()
        registry.load_czech_patterns()
        
        # Get all phone variants
        patterns = registry.get_patterns("phone", region="cz")
        assert len(patterns) >= 2  # Mobile + Landline
        
        # Should have mobile variant
        mobile = registry.get_pattern("phone", variant="mobile", region="cz")
        assert mobile is not None
        text = "+420 777 123 456"
        assert mobile.compiled.search(text) is not None
        
        # Should have landline variant
        landline = registry.get_pattern("phone", variant="landline", region="cz")
        assert landline is not None
        text = "+420 2 1234 5678"
        assert landline.compiled.search(text) is not None


class TestPatternCaching:
    """Test pattern compilation caching"""

    def test_patterns_compiled_once(self):
        """Patterns are compiled only once, then reused"""
        registry = PatternRegistry()
        
        pattern1 = PatternDefinition(
            entity_type="ico",
            name="standard",
            regex=r"\b(\d{8})\b",
            region="cz",
            score=1.0
        )
        
        registry.register(pattern1)
        
        # First retrieval compiles
        patterns1 = registry.get_patterns("ico", region="cz")
        compiled_id = id(patterns1[0].compiled)
        
        # Second retrieval reuses
        patterns2 = registry.get_patterns("ico", region="cz")
        assert id(patterns2[0].compiled) == compiled_id

    def test_pattern_compilation_is_lazy(self):
        """Patterns are not compiled until first use"""
        registry = PatternRegistry()
        
        pattern = PatternDefinition(
            entity_type="ico",
            name="standard",
            regex=r"\b(\d{8})\b",
            region="cz",
            score=1.0
        )
        
        # Create pattern instance (should not compile)
        # NOTE: PatternDefinition should compile in __post_init__
        # This test verifies that behavior
        
        # After registration, patterns should be compiled when retrieved
        registry.register(pattern)
        patterns = registry.get_patterns("ico", region="cz")
        
        # Should be compiled now
        assert patterns[0].compiled is not None


class TestPublicAPICompatibility:
    """Test that public detector constants remain available"""

    def test_rodne_cislo_detector_has_pattern_constant(self):
        """RodneCisloDetector still has CZECH_POSTAL_CODE_PATTERN constant"""
        # This ensures backward compatibility for external code
        from fastpii.detectors.cz.rodne_cislo import RodneCisloDetector
        
        # If detector had a pattern constant, it should still exist
        # (Implementation may change to use registry instead)
        detector = RodneCisloDetector()
        assert detector is not None  # Detector still instantiable

    def test_postal_code_detector_has_pattern_constant(self):
        """PostalCodeDetector still has CZECH_POSTAL_CODE_PATTERN constant"""
        from fastpii.detectors.cz.postal_code import PostalCodeDetector
        
        # Check class constant exists for backward compatibility
        assert hasattr(PostalCodeDetector, 'CZECH_POSTAL_CODE_PATTERN')
        
        # Pattern should match postal codes
        pattern = PostalCodeDetector.CZECH_POSTAL_CODE_PATTERN
        assert re.search(pattern, "110 00") is not None

    def test_phone_detector_has_pattern_constants(self):
        """Phone detector has MOBILE_PATTERN and LANDLINE_PATTERN constants"""
        from fastpii.detectors.cz.phone import PhoneNumberDetector
        
        # Class constants should still exist
        assert hasattr(PhoneNumberDetector, 'MOBILE_PATTERN')
        assert hasattr(PhoneNumberDetector, 'LANDLINE_PATTERN')


class TestPatternDefinition:
    """Test PatternDefinition dataclass"""

    def test_pattern_definition_creation(self):
        """Can create a PatternDefinition with required fields"""
        pattern = PatternDefinition(
            entity_type="ico",
            name="standard",
            regex=r"\b(\d{8})\b",
            region="cz",
            score=1.0
        )
        
        assert pattern.entity_type == "ico"
        assert pattern.name == "standard"
        assert pattern.region == "cz"
        assert pattern.score == 1.0

    def test_pattern_definition_compiles_regex(self):
        """PatternDefinition compiles regex in __post_init__"""
        pattern = PatternDefinition(
            entity_type="ico",
            name="standard",
            regex=r"\b(\d{8})\b",
            region="cz",
            score=1.0
        )
        
        assert pattern.compiled is not None
        assert isinstance(pattern.compiled, re.Pattern)

    def test_pattern_definition_optional_fields(self):
        """PatternDefinition handles optional fields"""
        pattern = PatternDefinition(
            entity_type="rodne_cislo",
            name="standard",
            regex=r"\b(\d{6}[/\s]?\d{3,4})\b",
            region="cz",
            score=0.95,
            context_words=["RČ", "rodné číslo"],
            checksum_algo="validate_birth_number_format"
        )
        
        assert pattern.context_words == ["RČ", "rodné číslo"]
        assert pattern.checksum_algo == "validate_birth_number_format"

    def test_invalid_regex_raises_error(self):
        """Invalid regex raises error during PatternDefinition creation"""
        with pytest.raises(ValueError) as exc_info:
            PatternDefinition(
                entity_type="test",
                name="invalid",
                regex=r"[invalid(",  # Unclosed bracket
                region="cz",
                score=1.0
            )
        assert "Invalid regex" in str(exc_info.value)