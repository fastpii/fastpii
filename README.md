# FastPII

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/fastpii.svg)](https://pypi.org/project/fastpii/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

**Privacy infrastructure for AI applications handling European data**

FastPII detects, validates, anonymizes, and protects sensitive data before it reaches LLMs, RAG systems, vector databases, AI agents, or third-party AI providers.

Built for AI-native applications. Designed for privacy-first architectures.

[Quick Start](#quick-start) · [Explicit Engine](#explicit-engine-api) · [Privacy Modes](#privacy-modes) · [AI Use Cases](#ai-use-cases) · [Benchmarks](#benchmarks) · [Documentation](#documentation)

</div>

---

## Why FastPII

Most PII tools are built for generic text processing. FastPII is built for AI workflows.

Modern applications increasingly send documents, prompts, support tickets, contracts, medical records, and business data directly into LLMs and AI systems. FastPII acts as the privacy layer between your data and your AI.

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

### Built for AI Workflows

FastPII integrates directly into RAG pipelines, LangChain applications, MCP servers, AI agents, FastAPI applications, and enterprise AI systems.

---

## Features

| | |
|---|---|
| **Detection** | Identify sensitive Czech and European data |
| **Validation** | Validate identifiers using official checksum rules |
| **Privacy Protection** | Four modes: anonymize, redact, mask, remove |
| **Explicit Engine** | No implicit behavior — you configure, it executes |
| **Framework-Independent SDK** | Use as a standalone Python package |
| **Integrations** | FastAPI, LangChain, MCP, CLI |
| **Local First** | No cloud, no LLM, no external API calls required |

---

## Installation

```bash
pip install fastpii
```

---

## Quick Start

### Explicit Engine API (Recommended)

```python
from fastpii import FastPII
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.cz import CzechPack
from fastpii.countries.pl import PolishPack

priority = {"rodne_cislo": 100, "pesel": 100, "email": 70, "name": 50, "phone": 20}

engine = FastPII(
    priority=priority,
    confidence_scorer=ConfidenceScorer(
        base_scores={"checksum_validated": 1.0, "context_match": 0.95, "pattern_match": 0.85},
        context_boost=0.10,
    ),
)
engine.register(CzechPack())
engine.register(PolishPack())

text = "Jan Novák, RČ: 800101/1238, IČO: 25596641"
result = engine.detect(text)

for finding in result.findings:
    print(f"{finding.type}: {finding.value}")
```

### Convenience API (PrivacyGuard)

```python
from fastpii import PrivacyGuard

# Single-region detection
guard = PrivacyGuard(regions=["cz"])
result = guard.detect("Jan Novák, RČ: 800101/1238, IČO: 25596641")

# Multi-region detection
guard = PrivacyGuard(regions=["cz", "pl", "de", "fr"])
```

> **Note:** `PrivacyGuard()` without `regions` emits a `DeprecationWarning`. Explicit region specification is recommended.

### Region Quick Start

```python
# Poland
guard = PrivacyGuard(regions=["pl"])
result = guard.detect("PESEL: 44051401458, NIP: 5260250274")

# Germany
guard = PrivacyGuard(regions=["de"])
result = guard.detect("Steuer-ID: 86095742719, USt-IdNr: DE136695976")

# France
guard = PrivacyGuard(regions=["fr"])
result = guard.detect("SIREN: 552120222, SIRET: 73282932000074")
```

---

## Explicit Engine API

FastPII follows an explicit execution model: **Core executes, Platform decides**. The engine never makes implicit choices.

### Required Configuration

- **`priority`** — Overlap resolution order (required, no default)
- **`confidence_scorer`** — Confidence scoring configuration (optional, no hidden defaults)

```python
from fastpii import FastPII
from fastpii.countries.cz import CzechPack

# Minimal setup — define your own priority dict
priority = {"rodne_cislo": 100, "email": 70, "name": 50, "phone": 20}
engine = FastPII(priority=priority)
engine.register(CzechPack())
result = engine.detect(text)
```

### Overridable Detector Values

Every detector exposes class-level attributes for all configurable values:

```python
from fastpii.detectors.cz.address import CzechAddressDetector

# Override scoring thresholds
class CustomAddressDetector(CzechAddressDetector):
    MIN_ADDRESS_SCORE = 0.3
    SCORE_STREET = 0.4
    SCORE_NUMBER = 0.3
    SCORE_POSTAL = 0.2
    SCORE_CITY = 0.1

# Override context words
class CustomPhoneDetector(CzechPhoneDetector):
    CONTEXT_WORDS = {"tel", "phone", "call"}
    CONTEXT_WINDOW_SIZE = 50
```

### Convenience Defaults

For backward compatibility, `PrivacyGuard` provides built-in convenience defaults for overlap priority and confidence scoring. These are used internally by `PrivacyGuard` — for production use with `FastPII`, define your own priority and scoring configuration based on your domain requirements.

---

## Privacy Modes

**Anonymize** — Replace with `[REDACTED]`

```python
engine.anonymize("Jan Novák, RČ: 800101/1238")
# → "[REDACTED], RČ: [REDACTED]"
```

**Redact** — Replace with PII type label

```python
engine.redact("Jan Novák, RČ: 800101/1238")
# → "[NAME], RČ: [RODNE_CISLO]"
```

**Mask** — Replace with asterisks

```python
engine.mask("Jan Novák")
# → "*********"
```

**Remove** — Delete PII entirely

```python
engine.remove("Jan Novák")
# → ""
```

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

---

## Supported Entities

### Czech Republic (CZ)

| Entity | Detection Method | Checksum |
|---|---|---|
| Rodné číslo | Mod 11 checksum + date validation | ✓ |
| IČO | Weighted Mod 11 checksum | ✓ |
| DIČ | Multi-format + IČO validation | ✓ |
| Bank Account | Two-part Mod 11 checksum | ✓ |
| Postal Code | Context-gated (PSČ label, city, address proximity) | — |
| Phone Number | Context-gated (+420 prefix or context words) | — |
| Date of Birth | Context-gated (birth keywords, intervening date blocking) | — |
| Address | Component scoring (street + number + city + postal) | — |
| Name | Czech name dictionary + gender classification | — |
| Email | Czech TLD detection, markdown mailto handling | — |
| Vehicle Plate | Regional code validation | — |

### Poland (PL)

| Entity | Detection Method | Checksum |
|---|---|---|
| PESEL | Mod 10 checksum + date/gender extraction | ✓ |
| NIP | Weighted Mod 11 checksum | ✓ |
| REGON | Weighted Mod 11 checksum (9-digit and 14-digit) | ✓ |
| Postal Code | Context-gated (DD-DDD format) | — |
| Phone Number | Context-gated (+48 prefix or context words) | — |
| Address | Component scoring (street + number + city + postal) | — |

### Germany (DE)

| Entity | Detection Method | Checksum |
|---|---|---|
| Steuer-ID | ISO 7064 MOD 11,10 checksum | ✓ |
| USt-IdNr | MOD 11,10 checksum (DE + 9 digits) | ✓ |
| Handelsregister | Format validation (Court + HRA/HRB/PR + number) | — |
| Postal Code | Context-gated (5-digit PLZ) | — |
| Phone Number | Context-gated (+49 prefix or context words) | — |
| Address | Component scoring (Straße + number + PLZ + city) | — |

### France (FR)

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

FastPII follows an Open Core architecture with a strict separation of concerns:

- **Core executes** — deterministic detection, validation, redaction
- **Platform decides** — auto-detection, pack selection, privacy presets
- **Enterprise governs** — org-level policy, audit, compliance

The OSS core is fully self-hostable, local-only, and explicit. No implicit behavior, no hidden defaults, no auto-detection.

See [ADR 0001](docs/ADR_0001_OSS_CORE_BOUNDARY.md) for the full boundary definition.

---

## Benchmarks

Evaluated on Czech-focused datasets containing contracts, medical records, business registries, support tickets, and adversarial false-positive scenarios.

**v0.4.0 overall:**

| Metric | Score |
|---|---|
| Precision | **84.2%** |
| Recall | **80.0%** |
| F1 | **82.1%** |

**Per-detector:**

| Detector | Precision | Recall | Notes |
|---|---|---|---|
| IČO | 100% | 100% | Checksum-validated, no FPs |
| DIČ | 100% | 100% | Multi-format detection |
| Email | 100% | 100% | Markdown mailto handled |
| Date | 100% | 100% | Non-birth dates detected separately |
| Phone | 100% | 100% | Context or +420 prefix required |
| Vehicle Plate | 100% | 100% | Regional code validation |
| Date of Birth | 100% | 86% | Context-gated; rejects generic dates |
| Postal Code | 100% | 71% | Subsumed by address in overlaps |
| Name | 80% | 100% | Dict-matched; corporate name FPs |
| Address | 71% | 63% | Component scoring; partial matches |
| Rodné číslo | 67% | 50% | Invalid checksums correctly rejected |
| Bank Account | 100% | 0% | Requires labeled context (v0.2.5) |

---

## Roadmap

**Current** — Explicit Engine API, Configurable Detectors, CZ/PL/DE/FR Country Packs, Validation Engine, CLI, FastAPI Integration, LangChain Integration

**Next** — Strict Mode, MCP Integration, RAG Middleware, Improved Address & Bank Account Detection, Additional European Regions


---

## Documentation

* [Quick Start](#quick-start)
* [Explicit Engine API Design](docs/EXPLICIT_ENGINE_API_DESIGN.md)
* [OSS Core Boundary ADR](docs/ADR_0001_OSS_CORE_BOUNDARY.md)
* [OSS / Platform Split Plan](docs/OSS_PLATFORM_SPLIT_PLAN.md)
* [Migration Roadmap](docs/OSS_PLATFORM_MIGRATION_ROADMAP.md)
* [Implementation Backlog](docs/IMPLEMENTATION_BACKLOG.md)
* [Repo Split Checklist](docs/REPO_SPLIT_CHECKLIST.md)

---

## Contributing

Contributions welcome! See [Contributing Guide](CONTRIBUTING.md).

Before contributing, review the [OSS Core Boundary](docs/ADR_0001_OSS_CORE_BOUNDARY.md) to ensure your change belongs in the OSS core. The core executes — it does not decide.

---

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

---

<div align="center">

Built for privacy-first AI applications

</div>