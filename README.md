# FastPII

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/fastpii.svg)](https://pypi.org/project/fastpii/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

**The open-source privacy engine for AI applications.**

Protect sensitive information before it reaches LLMs, RAG systems, AI agents, and enterprise AI workflows.

[Quick Start](#quick-start) · [Privacy Modes](#privacy-modes) · [Country Packs](#country-packs) · [AI Use Cases](#ai-use-cases) · [Benchmarks](#benchmarks)

</div>

---

## Why FastPII

Every prompt sent to an AI model can contain personal, confidential, or regulated information. FastPII acts as the privacy layer between your data and your AI.

> **Privacy first. AI second.**

```text
Without FastPII          With FastPII

Document                 Document
  ↓                        ↓
LLM                      FastPII
                           ↓
                         LLM

Sensitive data exposed   Sensitive data protected
```

### European-Native Detection

FastPII understands European identifiers and validation rules across 4 countries:

* **Czech Republic**: Rodné číslo · IČO · DIČ · Bank Accounts · Phone · PSČ · Addresses · Names · Vehicle Plates · Dates of Birth · Email
* **Poland**: PESEL · NIP · REGON · Postal Codes · Phone · Addresses
* **Germany**: Steuer-ID · USt-IdNr · Handelsregister · PLZ · Phone · Addresses
* **France**: SIREN · SIRET · INSEE/NIR · Code Postal · Phone · Addresses

### Checksum Validation

FastPII validates identifiers instead of relying solely on pattern matching. Rodné číslo (Mod 11), IČO (weighted Mod 11), PESEL (Mod 10), NIP (weighted Mod 11), REGON (weighted Mod 11), Steuer-ID (ISO 7064 MOD 11,10), USt-IdNr (MOD 11,10), SIREN/SIRET (Luhn), INSEE/NIR (Mod-97), and DIČ formats all require valid checksums — structurally invalid identifiers are rejected before classification.

### Context-Aware Detection

Detection is not based on regex alone. Phone numbers require context words or a country-specific prefix (+420, +48, +49, +33). Postal codes require address proximity or labels. Dates of birth need birth-related keywords nearby. Addresses use component scoring. This significantly reduces false positives.

### Fully Configurable

Every detector value is a class-level attribute. Confidence thresholds, scoring weights, context words, city lists, and overlap priority are all explicit and overridable — no hidden defaults in the core engine.

---

## Installation

```bash
pip install fastpii
```

---

## Quick Start

```python
from fastpii import FastPII, DEFAULT_PRIORITY
from fastpii.countries.cz import CzechPack

engine = FastPII(priority=DEFAULT_PRIORITY)
engine.register(CzechPack())

result = engine.detect("Jan Novák, RČ: 800101/1238, IČO: 25596641")
for f in result.findings:
    print(f"{f.type}: {f.value} (confidence: {f.confidence:.0%})")
```

Multiple country packs:

```python
from fastpii import FastPII, DEFAULT_PRIORITY
from fastpii.countries.cz import CzechPack
from fastpii.countries.pl import PolishPack

engine = FastPII(priority=DEFAULT_PRIORITY)
engine.register(CzechPack())
engine.register(PolishPack())
```

CLI:

```bash
pip install fastpii
fastpii detect "Jan Novák, RČ: 800101/1238" -r cz
```

---

## Explicit Engine

FastPII follows an explicit execution model: **you configure, it executes.** The engine never makes implicit choices.

### Required Configuration

- **`priority`** — Overlap resolution order (required, no default). Higher values win when findings overlap.

```python
from fastpii import FastPII, DEFAULT_PRIORITY, ConfidenceScorer
from fastpii.countries.cz import CzechPack

engine = FastPII(priority=DEFAULT_PRIORITY)
engine.register(CzechPack())
```

Custom priority:

```python
engine = FastPII(priority={"rodne_cislo": 100, "email": 70, "name": 50, "phone": 20})
```

Custom confidence scoring:

```python
engine = FastPII(
    priority=DEFAULT_PRIORITY,
    confidence_scorer=ConfidenceScorer(
        base_scores={"checksum_validated": 1.0, "context_match": 0.95, "pattern_match": 0.85},
        context_boost=0.10,
    ),
)
```

### Overridable Detector Values

Every detector exposes class-level attributes for all configurable values:

```python
from fastpii.detectors.cz.address import CzechAddressDetector

class CustomAddressDetector(CzechAddressDetector):
    MIN_ADDRESS_SCORE = 0.3
    SCORE_STREET = 0.4
    SCORE_NUMBER = 0.3
    SCORE_POSTAL = 0.2
    SCORE_CITY = 0.1
```

---

## Privacy Modes

| Mode | Example Input | Example Output |
|------|--------------|----------------|
| **Anonymize** | `RČ: 800101/1238` | `RČ: [REDACTED]` |
| **Redact** | `RČ: 800101/1238` | `RČ: [RODNE_CISLO]` |
| **Mask** | `800101/1238` | `*************` |
| **Remove** | `RČ: 800101/1238` | `RČ: ` |

```python
engine.anonymize(text)  # Replace with [REDACTED]
engine.redact(text)     # Replace with PII type label
engine.mask(text)       # Replace with asterisks
engine.remove(text)     # Delete PII entirely
```

---

## Validation

Validate individual identifiers directly:

```python
from fastpii.countries.cz import validate_ico, is_valid_birth_number

result = engine.validate("25596641", "ico")
# → ValidationResult(detector="ico", value="25596641", is_valid=True, metadata={...})

# Standalone validators
is_valid_ico("25596641")  # True
is_valid_birth_number("800101/1238")  # True
```

---

## Country Packs

| Country | Pack | Detectors | Status |
|---------|------|-----------|--------|
| Czech Republic | `CzechPack` | 15 detectors with checksum validation | Stable |
| Poland | `PolishPack` | PESEL, NIP, REGON, phone, postal code, address | Beta |
| Germany | `GermanPack` | Steuer-ID, USt-IdNr, Handelsregister, phone, postal code, address | Beta |
| France | `FrenchPack` | SIREN, SIRET, INSEE/NIR, phone, postal code, address | Beta |

Community-contributed country packs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a new country pack.

---

## AI Use Cases

### Protect RAG Pipelines

```python
safe_document = engine.anonymize(document)
embeddings = embed_model.embed(safe_document)
```

### Protect LLM Prompts

```python
safe_prompt = engine.anonymize(prompt)
response = llm.invoke(safe_prompt)
```

### Protect MCP Tools

```python
safe_input = engine.anonymize(user_input)
result = tool.execute(safe_input)
```

### FastAPI Integration

```python
from fastpii.integrations.fastapi import create_app

app = create_app(engine=engine)
```

### LangChain Integration

```python
from fastpii.integrations.langchain import PIIAnonymizer, create_pii_filter_tool

anonymizer = PIIAnonymizer(engine=engine)
safe_text = anonymizer("Jan Novák, RČ: 800101/1238")

# Or as a LangChain tool
tool = create_pii_filter_tool(engine=engine)
```

---

## Supported Entities

### Czech Republic (CZ) — 15 Detectors

| Entity | Detection Method | Checksum |
|---|---|---|
| Rodné číslo | Mod 11 checksum + date validation | ✓ |
| IČO | Weighted Mod 11 checksum | ✓ |
| DIČ | Multi-format + IČO validation | ✓ |
| Bank Account | Two-part Mod 11 checksum + bank code validation | ✓ |
| Identity Card | New 9-digit + old 6+2 letter formats, context-gated | — |
| Health Insurance | 7 insurance codes, slash/plain formats, context-gated | — |
| IBAN | MOD97 checksum, CZ country code, context-gated | ✓ |
| Credit Card | Luhn validation, Visa/MC/Amex BIN prefixes, context-gated | ✓ |
| Postal Code | Context-gated (PSČ label, city, address proximity) | — |
| Phone Number | Context-gated (+420 prefix or context words) | — |
| Date of Birth | Context-gated (birth keywords, intervening date blocking) | — |
| Address | Component scoring (street + number + city + postal) | — |
| Name | Czech name dictionary + corporate name filtering | — |
| Email | Czech TLD detection, markdown mailto handling | — |
| Vehicle Plate | Regional code validation | — |

### Poland (PL) — 6 Detectors

| Entity | Detection Method | Checksum |
|---|---|---|
| PESEL | Mod 10 checksum + date/gender extraction | ✓ |
| NIP | Weighted Mod 11 checksum | ✓ |
| REGON | Weighted Mod 11 checksum (9-digit and 14-digit) | ✓ |
| Postal Code | Context-gated (DD-DDD format) | — |
| Phone Number | Context-gated (+48 prefix or context words) | — |
| Address | Component scoring (street + number + city + postal) | — |

### Germany (DE) — 6 Detectors

| Entity | Detection Method | Checksum |
|---|---|---|
| Steuer-ID | ISO 7064 MOD 11,10 checksum | ✓ |
| USt-IdNr | MOD 11,10 checksum (DE + 9 digits) | ✓ |
| Handelsregister | Format validation (Court + HRA/HRB/PR + number) | — |
| Postal Code | Context-gated (5-digit PLZ) | — |
| Phone Number | Context-gated (+49 prefix or context words) | — |
| Address | Component scoring (Straße + number + PLZ + city) | — |

### France (FR) — 6 Detectors

| Entity | Detection Method | Checksum |
|---|---|---|
| SIREN | Luhn checksum (9-digit) | ✓ |
| SIRET | Luhn checksum (14-digit, embeds SIREN) | ✓ |
| INSEE/NIR | Mod-97 checksum (15-char, Corsica 2A/2B handling) | ✓ |
| Postal Code | Context-gated (5-digit code postal) | — |
| Phone Number | Context-gated (+33 prefix or context words) | — |
| Address | Component scoring (number + Rue/Avenue/Boulevard + city) | — |

---

## Architecture

FastPII follows an explicit execution model: **Core executes, Intelligence Engine decides.**

* **Core** — deterministic detection, validation, transformation
* **Country Packs** — region-specific patterns, validators, data
* **Integrations** — FastAPI, LangChain, MCP, CLI

The OSS core is fully self-hostable, local-only, and explicit. You explicitly register the country packs you need. No implicit behavior, no hidden defaults, no auto-detection.

Auto-detection of PII across countries, adaptive scoring, and intelligent routing are part of the FastPII Intelligence Engine (commercial). Privacy presets, multi-country routing, and compliance mapping are Intelligence Engine features.

---

## Benchmarks

Evaluated on Czech-focused datasets containing contracts, medical records, business registries, support tickets, and adversarial false-positive scenarios.

**v0.4.1 overall:**

| Metric | Score |
|---|---|
| Precision | **98%** |
| Recall | **100%** |
| F1 | **99%** |

**Per-detector:**

| Detector | Precision | Recall | Notes |
|---|---|---|---|
| IČO | 100% | 100% | Checksum-validated, no FPs |
| DIČ | 100% | 100% | Multi-format detection |
| Email | 100% | 100% | Markdown mailto handled |
| Date | 100% | 100% | Non-birth dates detected separately |
| Phone | 100% | 100% | Context or +420 prefix required |
| Vehicle Plate | 100% | 100% | Regional code validation |
| Bank Account | 100% | 100% | Two-part Mod 11, context-gated |
| Address | 97% | 100% | Component scoring; DI data |
| Postal Code | 100% | 100% | Context-gated; Česká pošta data |
| Name | 80% | 100% | Dict-matched; corporate name FPs |
| Date of Birth | 100% | 86% | Context-gated; rejects generic dates |
| Rodné číslo | 67% | 50% | Invalid checksums correctly rejected |
| Identity Card | 100% | 100% | New 9-digit + old 6+2 letter formats |
| Health Insurance | 100% | 100% | 7 insurance codes; slash/plain formats |
| IBAN | 100% | 100% | MOD97 checksum; CZ country code |
| Credit Card | 100% | 100% | Luhn validation; Visa/MC/Amex BIN |

---

## Products

| Component | Description |
|-----------|-------------|
| **FastPII Core** | Open-source privacy engine. Detect, validate, anonymize, redact, mask, remove. |
| **FastPII Intelligence Engine** | Auto-detection, multi-country routing, adaptive scoring, privacy presets. Commercial. |
| **FastPII Detection API** | Hosted REST API. Same detection, no infrastructure. |
| **FastPII Secure Chat** | Privacy-first AI chat. BYOK — we protect outbound prompts, never proxy responses. |
| **FastPII Enterprise** | Governance, audit trails, compliance reporting for organizations. |

Learn more at [https://fastpii.com](https://fastpii.com)

---

## Documentation

* [API Reference](https://docs.fastpii.com/api)
* [Explicit Engine Design](docs/EXPLICIT_ENGINE_API_DESIGN.md)
* [OSS Core Boundary](docs/ADR_0001_OSS_CORE_BOUNDARY.md)
* [Add a Country Pack](docs/ADD_A_COUNTRY_PACK.md)
* [Migration Guide](docs/MIGRATION_GUIDE.md)
* [Changelog](CHANGELOG.md)

---

## Roadmap

**Current** — Explicit Engine API, Configurable Detectors, CZ/PL/DE/FR Country Packs, Validation Engine, CLI, FastAPI Integration, LangChain Integration

**Next** — Strict Mode, MCP Integration, RAG Middleware, Improved Address & Bank Account Detection, Additional European Country Packs

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, coding standards, and PR guidelines.

Areas where help is especially valuable:

* Country Packs — add support for new European countries
* Validators — improve checksum and format validation
* Benchmarks — expand test coverage and accuracy measurement
* Performance — keep detection under 1ms per lookup
* Documentation — guides, examples, API reference

Before contributing, review the [OSS Core Boundary](docs/ADR_0001_OSS_CORE_BOUNDARY.md) to ensure your change belongs in the OSS core. The core executes — it does not decide.

---

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

---

<div align="center">

Built for privacy-first AI applications

</div>
