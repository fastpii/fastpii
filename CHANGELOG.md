# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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