"""
Czech (CZ) Pattern Loader.

Implements the Strategy pattern for loading Czech-specific PII patterns.
Follows industrial standards for plugin architectures.
"""

from fastpii.patterns.base import PatternDefinition


class CzechPatternLoader:
    """
    Czech pattern loader following the Strategy pattern.
    
    This loader encapsulates all Czech-specific pattern definitions,
    making it easy to maintain and extend Czech patterns independently
    from the core registry logic.
    
    Design Patterns Used:
    - Strategy Pattern: Each region implements its own loading strategy
    - Plugin Pattern: Auto-discovered by the registry
    - Configuration Pattern: Patterns defined declaratively
    
    Industry Standards:
    - ISO 3166-1 alpha-2 codes for region identification (CZ, SK, DE, PL)
    - ISO/IEC 5218 for gender codes (0=unknown, 1=male, 2=female, 9=not applicable)
    - ISO 8601 for date formats
    
    Usage:
        loader = CzechPatternLoader()
        patterns = loader.load()
        for pattern in patterns:
            registry.register(pattern)
    """
    
    REGION_CODE: str = "cz"
    REGION_NAME: str = "Czech Republic"
    LANGUAGE_CODES: list[str] = ["cs", "cs-CZ"]  # Czech language
    
    @staticmethod
    def load() -> list[PatternDefinition]:
        """
        Load all Czech patterns.
        
        Returns:
            List of PatternDefinition instances
            
        Design Pattern: Factory Method
        - Creates pattern objects without exposing creation logic
        - Allows easy testing and extension
        """
        patterns: list[PatternDefinition] = []
        
        # Rodné číslo (Birth Number) - Czech national ID
        # ISO 3166-1: CZ
        # Format: YYMMDD/XXXX or YYMMDDXXXX
        # Validation: MOD 11 checksum, date validation
        patterns.append(PatternDefinition(
            entity_type="rodne_cislo",
            name="standard",
            regex=r"\b(\d{6}[/\s]?\d{3,4})\b",
            region="cz",
            score=0.95,
            context_words=["rodné číslo", "RČ", "rod. č.", "birth number"],
            checksum_algo="validate_birth_number_format",
            validation_regex=r"^(\d{6}[/\s]?\d{3,4})$",
            extraction_regex=r"^(\d{2})(\d{2})(\d{2})[/\s]?(\d{3,4})$"
        ))
        
        # IČO (Identifikační číslo osoby) - Company Registration Number
        # Ministry of Justice assigned identifier
        # Validation: Weighted MOD 11 checksum
        patterns.append(PatternDefinition(
            entity_type="ico",
            name="standard",
            regex=r"\b(\d{8})\b",
            region="cz",
            score=1.0,
            context_words=["IČO", "IČ", "identiﬁkační číslo", "company ID"],
            checksum_algo="validate_ico",
            validation_regex=r"^\d{1,8}$"
        ))
        
        # DIČ (Daňové identifikační číslo) - Tax Identification Number
        # Format: CZ + 8-10 digits
        # CZ + 8 digits = company
        # CZ + 9 digits (starts with 6) = special
        # CZ + 10 digits = individual (rodné číslo)
        patterns.append(PatternDefinition(
            entity_type="dic",
            name="standard",
            regex=r"\bCZ(\d{8,10})\b",
            region="cz",
            score=0.95,
            context_words=["DIČ", "daňové číslo", "VAT", "tax ID"],
            checksum_algo="validate_dic",
            validation_regex=r"^\d{8,10}$",
            extraction_regex=r"^(\d{8,10})$"
        ))
        
        # Bank Account (Bankovní účet)
        # Format: prefix-base/bank_code or base/bank_code
        # Example: 123456-1234567890/0100
        # Validation: Two-part MOD 11 checksum
        patterns.append(PatternDefinition(
            entity_type="bank_account",
            name="standard",
            regex=r"\b(\d{1,6}-?\d{1,10})/(\d{4})\b",
            region="cz",
            score=1.0,
            context_words=["účet", "číslo účtu", "bankovní účet", "bank account"],
            checksum_algo="validate_bank_account",
            validation_regex=r"^(\d{1,6})?-(\d{2,10})/(\d{4})$|^(\d{2,10})/(\d{4})$",
            extraction_regex=r"^(\d{1,6})?(\d{1,10})/(\d{4})$"
        ))
        
        # PSČ (Poštovní směrovací číslo) - Postal Code
        # Format: XXX XX or XXXXX
        # Range: 100 00 - 999 99
        patterns.append(PatternDefinition(
            entity_type="postal_code",
            name="standard",
            regex=r"\b(\d{3})\s?(\d{2})\b",
            region="cz",
            score=0.95,
            context_words=["PSČ", "poštovní směrovací číslo", "postal code"],
            validation_regex=r"^\d{3}\s?\d{2}$",
            extraction_regex=r"^(\d{3})\s?(\d{2})$"
        ))
        
        # Phone - Mobile (Mobilní telefon)
        # Prefixes: 601-608, 702-799
        # Format: +420 XXX XXX XXX or XXX XXX XXX
        # Boundary checks: no adjacent digits. Context validation done in detector.
        patterns.append(PatternDefinition(
            entity_type="phone",
            name="mobile",
            regex=r"(?<!\d)(?:\+420[\s-]?)?(?:60[1-8]|7\d{2})[\s-]?\d{3}[\s-]?\d{3}(?!\d)",
            region="cz",
            score=0.95,
            context_words=["tel", "telefon", "mobil", "mobile", "phone", "contact", "number"],
            extraction_regex=r"(?:\+420[\s-]?)?(60[1-8]|7\d{2})[\s-]?(\d{3})[\s-]?(\d{3})"
        ))
        
        # Phone - Landline (Pevná linka)
        # Area codes: 2 (Prague), 3 (Pardubice/Hradec), 4 (Plzeň), 5 (Brno/Olomouc)
        # Format 1: +420 [2-5] XXXX XXXX (area code is 1 digit, then 4+4 digits)
        # Format 2: +420 [2-5]XX XXX XXX (Prague style: area+2digits, then 3+3)
        # Boundary checks: no adjacent digits. Context validation done in detector.
        patterns.append(PatternDefinition(
            entity_type="phone",
            name="landline",
            regex=r"(?<!\d)(?:\+420[\s-]?)?[2-5](?:[\s-]?\d{4}[\s-]?\d{4}|[\s-]?\d{2}[\s-]?\d{3}[\s-]?\d{3})(?!\d)",
            region="cz",
            score=0.90,
            context_words=["tel", "telefon", "pevná linka", "landline", "contact", "number"],
            extraction_regex=r"(?:\+420[\s-]?)?([2-5])[\s-]?(\d{4})[\s-]?(\d{4})"
        ))
        
        # Email Address
        # RFC 5322 simplified pattern
        # Czech domains: .cz, .sk prioritized
        # Allow Czech diacritical characters in local part
        patterns.append(PatternDefinition(
            entity_type="email",
            name="standard",
            regex=r"\b[A-Za-z0-9áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            region="cz",
            score=0.95,
            context_words=["email", "e-mail", "@"],
            validation_regex=r"^[A-Za-z0-9áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        ))
        
        return patterns
    
    @staticmethod
    def get_metadata() -> dict[str, object]:
        """
        Get metadata about Czech patterns.
        
        Returns:
            Dictionary with region information, pattern counts, etc.
        """
        return {
            "region_code": "cz",
            "region_name": "Czech Republic",
            "language_codes": ["cs", "cs-CZ"],
            "iso_3166_code": "CZ",
            "pattern_count": 8,
            "entity_types": [
                "rodne_cislo",
                "ico",
                "dic",
                "bank_account",
                "postal_code",
                "phone",  # has variants: mobile, landline
                "email"
            ],
            "has_checksum_validation": True,
            "checksum_algorithms": [
                "validate_birth_number_format",
                "validate_ico",
                "validate_dic",
                "validate_bank_account"
            ]
        }
