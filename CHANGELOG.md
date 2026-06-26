# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Country Pack SDK** (`fastpii.countries`): Formal `CountryPack` ABC with `@register_country` decorator for auto-discovery. New countries are registered by implementing the ABC and importing the module — `PrivacyGuard` discovers them automatically.
- **Core shared utilities** (`fastpii.core`): `_compat` (override shim), `context` (ContextWindowMatcher), `confidence` (ConfidenceScorer), `checksum` (weighted_mod11, luhn), `normalization` (whitespace, phone)
- **Poland (PL) country pack**: 6 detectors — PESEL, NIP, REGON, Postal Code, Phone, Address
  - PESEL: 11-digit national ID, Mod 10 checksum, birth date + gender extraction
  - NIP: 10-digit tax ID, weighted Mod 11 checksum
  - REGON: 9-digit and 14-digit business registry, weighted Mod 11 checksum
- **Germany (DE) country pack**: 6 detectors — Steuer-ID, USt-IdNr, Handelsregister, Postal Code, Phone, Address
  - Steuer-ID: 11-digit tax ID, ISO 7064 MOD 11,10 checksum, consecutive-digit rejection
  - USt-IdNr: DE + 9-digit VAT number, MOD 11,10 checksum
  - Handelsregister: Commercial register format (Court + HRA/HRB/PR + number)
- **France (FR) country pack**: 6 detectors — SIREN, SIRET, INSEE/NIR, Postal Code, Phone, Address
  - SIREN: 9-digit business ID, Luhn checksum
  - SIRET: 14-digit establishment ID, embeds SIREN + Luhn on full number
  - INSEE/NIR: 15-character national ID, Mod-97 checksum with Corsica 2A/2B department handling
- **Pattern loaders** for Poland, Germany, and France (`patterns/regions/`)
- **46 Poland tests**, **30 Germany tests**, **32 France tests**

### Changed

- `PrivacyGuard` refactored: detector registration now uses auto-discovery via country packs instead of hardcoded CZ imports. Calling `pack.register_patterns()` + `pack.register_detectors()` on initialization.
- `CountryPack.code` must be a class attribute (not a property) for correct registration key derivation
- README updated to reflect 4-country coverage with per-country entity tables

### Fixed

- INSEE/NIR regex: `2[AB]` department code was incorrectly placed in the month group — moved to the department position in both validator and pattern loader
- CountryPack registration: `@register_country` was reading `pack_cls.code` as a property descriptor instead of a string — fixed by changing `code` to a class attribute

## [0.2.0] - 2025-06-09

### Added

- **Name detector** (`name`): Czech personal name detection with gender classification using surname patterns and first name database
- **Email detector** (`email`): Email address detection with Czech TLD awareness and domain validation
- **Address detector** (`address`): Czech street address detection with house number patterns
- **Date of birth detector** (`date_of_birth`): Context-aware birth date detection using Czech context words
- **Vehicle plate detector** (`vehicle_plate`): Czech vehicle license plate detection with regional code validation
- **Redaction API**: Four new methods on `PrivacyGuard`:
  - `anonymize(text, replacement="[REDACTED]")` — Replace PII with uniform placeholder
  - `redact(text)` — Replace PII with type-based labels (`[EMAIL]`, `[RODNE_CISLO]`, etc.)
  - `mask(text)` — Replace PII with asterisks matching original length
  - `remove(text)` — Remove PII entirely from text
- **LangChain integration** now delegates to core redaction methods (anonymize, redact, mask, remove)
- **Czech name database** (`data/czech_names.py`) with male/female first names and surnames for detection
- **Data package** (`data/__init__.py`) for name database access

### Fixed

- Critical bug in redaction methods: findings are now sorted by position descending to maintain correct character indices
- Removed duplicate `_extract_metadata` method from `name.py` detector
- Cleaned up duplicate entries in Czech name database (`czech_names.py`)
- Fixed suspicious entries in Czech surname data (typos: `aAnna`, `vjtová`, `žžížalová`, `šilhouová`)
- Removed unused imports across detector files (`import re`, `import Any`)

### Changed

- Version bumped from 0.1.0 to 0.2.0
- Updated module exports in `__init__.py` to include new detectors
- Updated `detectors/cz/__init__.py` to register all 11 detectors

## [0.1.0] - 2025-06-01

### Added

- Initial release
- Core detection and validation for 6 Czech identifiers:
  - Rodné číslo (birth number)
  - IČO (company ID)
  - DIČ (VAT number)
  - Bank account number
  - Postal code (PSČ)
  - Phone number
- Pattern Registry for extensible pattern management
- PrivacyGuard as main entry point
- FastAPI integration
- LangChain integration (anonymization)
- MCP server integration
- CLI tool (`fastpii detect`, `fastpii validate`, `fastpii list-detectors`)
- Models: `Finding`, `DetectionResult`, `ValidationResult`
- Checksum validation for rodné číslo, IČO, DIČ, bank account
- GitHub Actions CI/CD pipeline
- Comprehensive test suite (303+ tests)