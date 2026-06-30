# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2026-06-28

### Fixed

- **Critical: `mask()` produced wrong-length output when detectors normalized values.** Phone numbers with formatting (`+420 777 888 999` → 12-char value but 16-char original span) and rodne cislo with slash (`800101/1238` → 10-char value but 11-char span) were masked with too few asterisks. `mask()` now uses `(finding.end - finding.start)` instead of `len(finding.value)` to preserve original text length in all cases.

### Added

- **TransformationEngine with strategy pattern** (`fastpii.core.transform`): Extracted transformation logic from `FastPII` into a `TransformationEngine` with pluggable strategies (`AnonymizeStrategy`, `RedactStrategy`, `MaskStrategy`, `RemoveStrategy`). Custom strategies can be created by implementing the `TransformationStrategy` protocol.
- **63 edge-case tests** for transformation methods covering value/span mismatches, formatted phone numbers across CZ/PL/DE/FR, rodne cislo with slash, mask length invariants, custom strategies, and mixed-language documents.

### Changed

- `FastPII.anonymize()`, `redact()`, `mask()`, `remove()` now delegate to `TransformationEngine.apply()` instead of inline list-conversion + reverse-sort + slice-assignment boilerplate.
- `TransformationStrategy`, `AnonymizeStrategy`, `RedactStrategy`, `MaskStrategy`, `RemoveStrategy`, `TransformationEngine` exported from top-level `fastpii` package.

## [0.5.0] - 2026-06-30

### Added

- **Modular data infrastructure** (`fastpii.data`): `CountryData[T]`, `CountryModule` ABC, `CountryMetadata`, `DataSource`, `CountryRegistry` — pluggable data layer for country-specific datasets
- **CZ data module** (complete): 5,344 cities, 15,500 postal codes, 26,954 streets, 48 bank codes, 7 insurance codes, 7,408 male + 8,287 female first names, 175 male + 175 female surnames
- **DE data module** (initial): 63 cities, 189 postal codes, 144 streets — empty stubs for bank_codes, insurance_codes, names, surnames
- **FR data module** (initial): 79 cities, 100 postal codes, 104 streets — empty stubs for bank_codes, insurance_codes, names, surnames
- **PL data module** (initial): 30 cities, 297 postal codes (DD-DDD format), 103 streets — empty stubs for bank_codes, insurance_codes, names, surnames
- **Pattern registry performance**: `@lru_cache(maxsize=1)` on `get_region_loaders()`, 7 benchmark tests
- **Multi-country integration tests** (MC-004): 13 tests across CZ/PL/DE/FR
- **Add-a-country guide** (MC-005): contributor documentation for new country packs
- **Data integrity tests** for DE/FR/PL: 52 tests (27 active, 25 skipped for empty modules)
- **VAL-001/003/004/005**: Benchmark corpus, redaction correctness (111 tests), overlap resolution (49 tests), performance benchmarks
- **ARCH-001/002/003/004**: Dual data layer, validator re-exports, `__all__` on 30+ modules, pyright 0 errors
- **CORE-001/002/003/004**: Transform round-trip (32 tests), overlap edge cases (23 tests), confidence calibration (22 tests), CLI round-trip
- **PR-001/002/003**: Pattern registry loader tests (23 tests), coverage audit (33/33 detectors), performance optimization
- **INT-001/002/003/004**: FastAPI, LangChain, MCP, CLI integration tests
- **CONTRIBUTING.md**: Contributor guide with setup, coding standards, and PR guidelines

### Changed

- `CountryPack` registration now uses `CountryRegistry` for data modules
- All country data uses lazy loading via `if self._data is None: from ... import X`
- ASCII transliteration for all DE/FR/PL data entries (no umlauts/accents)
- README updated for 0.5.0 release

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