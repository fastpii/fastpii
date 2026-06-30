# FastPII

**The open-source privacy engine for AI applications.**

Protect sensitive information before it reaches Large Language Models (LLMs), Retrieval-Augmented Generation (RAG) systems, AI agents, and enterprise AI workflows.

Apache 2.0 · Privacy First · European AI · Deterministic Detection

[Documentation](https://fastpii.com) · [Website](https://fastpii.com) · [PyPI](https://pypi.org/project/fastpii/) · [Secure Chat](https://fastpii.com) · [GitHub Discussions](https://github.com/fastpii/fastpii/discussions)

---

## Why FastPII?

AI is changing how we build software.

But every prompt sent to an AI model can contain personal, confidential, or regulated information.

FastPII helps developers build AI applications that protect sensitive data before it reaches external AI providers.

FastPII is built around one principle:

> **Privacy first. AI second.**

---

## What FastPII Does

FastPII helps you:

* Detect sensitive information
* Validate country-specific identifiers
* Anonymize, redact, mask or remove personal data
* Protect prompts before they reach AI
* Integrate privacy into LLM applications
* Build privacy-first AI systems

---

## Why FastPII?

Unlike generic PII libraries, FastPII is designed specifically for modern AI applications.

Built for:

* LLMs
* AI Agents
* RAG Systems
* MCP Servers
* Vector Databases
* AI APIs

---

## Features

* Deterministic detection — no LLM calls, no cloud dependency
* Country-specific validation — checksums for official identifiers
* Modular country packs — CZ, DE, FR, PL, community-contributed packs welcome
* Fast Python SDK — zero dependencies, <1ms per detection
* FastAPI integration — drop-in REST API for PII detection
* LangChain integration — anonymizer and preprocessor for LLM chains
* MCP server — Model Context Protocol for AI agents
* CLI — command-line detection, validation, and evaluation
* Plugin architecture — add countries without touching core
* Apache 2.0 — fully open source
* Self-hosted — no external API calls required

---

## European Privacy Intelligence

Supported today:

| Country | Pack | Detectors | Status |
|---------|------|-----------|--------|
| 🇨🇿 Czech Republic | `CzechPack` | 15 detectors with checksum validation | Stable |
| 🇵🇱 Poland | `PolishPack` | PESEL, NIP, REGON, phone, postal code, address | Beta |
| 🇩🇪 Germany | `GermanPack` | Steuer-ID, USt-IdNr, Handelsregister, phone, postal code, address | Beta |
| 🇫🇷 France | `FrenchPack` | SIREN, SIRET, INSEE/NIR, phone, postal code, address | Beta |

More countries are being added continuously.

---

## Quick Example

```bash
pip install fastpii
```

```python
from fastpii import FastPII, DEFAULT_PRIORITY
from fastpii.countries.cz import CzechPack

engine = FastPII(priority=DEFAULT_PRIORITY)
engine.register(CzechPack())

result = engine.detect("Jan Novák, RČ: 800101/1238, IČO: 25596641")
for f in result.findings:
    print(f"{f.type}: {f.value} (confidence: {f.confidence:.0%})")
```

CLI:

```bash
fastpii detect "Jan Novák, RČ: 800101/1238" -r cz
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
engine.anonymize(text)
engine.redact(text)
engine.mask(text)
engine.remove(text)
```

---

## Integrations

### FastAPI

```python
from fastpii.integrations.fastapi import create_app

app = create_app(engine=engine)
```

### LangChain

```python
from fastpii.integrations.langchain import PIIAnonymizer, create_pii_filter_tool

anonymizer = PIIAnonymizer(engine=engine)
safe_text = anonymizer("Send contract to jan.novak@email.cz")
```

### MCP Server

```python
from fastpii.integrations.mcp import MCPServer

server = MCPServer(engine=engine)
```

---

## Architecture

FastPII follows an explicit execution model: **you configure, it executes.**

* **Core** — deterministic detection, validation, transformation
* **Country Packs** — region-specific patterns, validators, data
* **Integrations** — FastAPI, LangChain, MCP, CLI

The OSS core is fully self-hostable, local-only, and explicit. You explicitly register the country packs you need. No implicit behavior, no hidden defaults, no auto-detection.

Auto-detection, multi-country routing, adaptive scoring, and privacy presets are part of the FastPII Intelligence Engine (commercial).

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

## Benchmarks

Evaluated on Czech-focused datasets containing contracts, medical records, business registries, support tickets, and adversarial false-positive scenarios.

**v0.4.1 overall:**

| Metric | Score |
|---|---|
| Precision | **98%** |
| Recall | **100%** |
| F1 | **99%** |

---

## Documentation

* [Explicit Engine Design](docs/EXPLICIT_ENGINE_API_DESIGN.md)
* [OSS Core Boundary](docs/ADR_0001_OSS_CORE_BOUNDARY.md)
* [Add a Country Pack](docs/ADD_A_COUNTRY_PACK.md)
* [Migration Guide](docs/MIGRATION_GUIDE.md)
* [Changelog](CHANGELOG.md)

---

## Ecosystem

FastPII is more than a Python package.

| Component | Description |
|-----------|-------------|
| **FastPII Core** | Open-source privacy engine. Detect, validate, anonymize, redact, mask, remove. |
| **FastPII Intelligence Engine** | Auto-detection, multi-country routing, adaptive scoring, privacy presets. Commercial. |
| **FastPII Secure Chat** | Hosted privacy-first AI chat. BYOK — protects outbound prompts, never proxies responses. |
| **FastPII Enterprise** | Governance, audit trails, compliance reporting for organizations. |

---

## Looking for a Hosted Experience?

If you don't want to manage infrastructure yourself, FastPII Secure Chat provides a managed experience built on FastPII Core.

Learn more at [https://fastpii.com](https://fastpii.com)

---

## Community

* [GitHub Discussions](https://github.com/fastpii/fastpii/discussions) — Ask questions, share ideas
* [GitHub Issues](https://github.com/fastpii/fastpii/issues) — Report bugs, request features
* [Contributing Guide](https://github.com/fastpii/fastpii/blob/main/CONTRIBUTING.md) — How to contribute
* [Code of Conduct](https://github.com/fastpii/fastpii/blob/main/CODE_OF_CONDUCT.md) — Community standards

---

## Roadmap

**Current**

* FastPII Core — deterministic detection and validation
* Country Packs — CZ, DE, FR, PL
* Secure Chat — privacy-first AI chat

**Coming Next**

* More European country packs
* Intelligence Engine — auto-detection, multi-country routing
* Enterprise Gateway
* Browser Extension
* Mobile SDK

---

## Contributing

Contributions are welcome.

Areas where help is especially valuable:

* Country Packs — add support for new European countries
* Validators — improve checksum and format validation
* Benchmarks — expand test coverage and accuracy measurement
* Performance — keep detection under 1ms per lookup
* Documentation — guides, examples, API reference
* Examples — real-world integration examples
* Testing — edge cases, false positive testing

See [CONTRIBUTING.md](https://github.com/fastpii/fastpii/blob/main/CONTRIBUTING.md) for setup instructions, coding standards, and PR guidelines.

---

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

---

FastPII is building the privacy layer for the next generation of AI applications.

If you are building with AI, privacy should not be an afterthought.

Help us build the future of privacy-first AI.
