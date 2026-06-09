# FastPII

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/fastpii.svg)](https://pypi.org/project/fastpii/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![FastPII](https://img.shields.io/badge/FastPII-v0.2.4-orange)](https://github.com/fastpii/fastpii)

**Privacy infrastructure for AI applications handling Czech and European data**

FastPII detects, validates, anonymizes, and protects sensitive data before it reaches LLMs, RAG systems, vector databases, AI agents, or third-party AI providers.

Built for AI-native applications. Designed for privacy-first architectures.

[Quick Start](#quick-start) · [Privacy Modes](#privacy-modes) · [AI Use Cases](#ai-use-cases) · [Benchmarks](#benchmarks) · [Documentation](#documentation)

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

### Czech-Native Detection

Unlike generic PII tools, FastPII understands Czech identifiers and validation rules:

* Rodné číslo · IČO · DIČ · Bank Accounts
* Phone Numbers · Postal Codes (PSČ) · Addresses
* Personal Names · Vehicle Plates · Dates of Birth · Email Addresses

### Checksum Validation

FastPII validates identifiers instead of relying solely on pattern matching. Rodné číslo (Mod 11), IČO (weighted Mod 11), Czech bank accounts, and DIČ formats all require valid checksums — structurally invalid identifiers are rejected before classification.

### Context-Aware Detection

Detection is not based on regex alone. Phone numbers require context words or a +420 prefix. Postal codes require address proximity. Dates of birth need birth-related keywords nearby. Addresses use component scoring. This significantly reduces false positives.

### Built for AI Workflows

FastPII integrates directly into RAG pipelines, LangChain applications, MCP servers, AI agents, FastAPI applications, and enterprise AI systems.

---

## Features

| | |
|---|---|
| **Detection** | Identify sensitive Czech and European data |
| **Validation** | Validate identifiers using official checksum rules |
| **Privacy Protection** | Four modes: anonymize, redact, mask, remove |
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

```python
from fastpii import PrivacyGuard

guard = PrivacyGuard(regions=["cz"])

text = "Jan Novák, RČ: 800101/1238, IČO: 25596641"
result = guard.detect(text)

for finding in result.findings:
    print(f"{finding.type}: {finding.value}")
    # name: Jan Novák
    # rodne_cislo: 8001011238
    # ico: 25596641
```

---

## Privacy Modes

**Anonymize** — Replace with `[REDACTED]`

```python
guard.anonymize("Jan Novák, RČ: 800101/1238")
# → "[REDACTED], RČ: [REDACTED]"
```

**Redact** — Replace with PII type label

```python
guard.redact("Jan Novák, RČ: 800101/1238")
# → "[NAME], RČ: [RODNE_CISLO]"
```

**Mask** — Replace with asterisks

```python
guard.mask("Jan Novák")
# → "*********"
```

**Remove** — Delete PII entirely

```python
guard.remove("Jan Novák")
# → ""
```

---

## AI Use Cases

### Protect RAG Pipelines

```python
safe_document = guard.anonymize(document)
embeddings = embed_model.embed(safe_document)
```

### Protect LLM Prompts

```python
safe_prompt = guard.anonymize(prompt)
response = llm.invoke(safe_prompt)
```

### Protect MCP Tools

```python
safe_input = guard.anonymize(user_input)
result = tool.execute(safe_input)
```

---

## Supported Czech Entities

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

---

## Benchmarks

Evaluated on Czech-focused datasets containing contracts, medical records, business registries, support tickets, and adversarial false-positive scenarios.

**v0.2.4 overall:**

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

**Current** — Core SDK, Czech Detectors, Validation Engine, CLI, FastAPI Integration, LangChain Integration

**Next (v0.2.5)** — Strict Mode, MCP Integration, RAG Middleware, Improved Address & Bank Account Detection

**Future** — FastPII Gateway, Policy Engine, Audit Logging, Enterprise Features, Additional European Regions

---

## Documentation

* [Quick Start](#quick-start)
* [API Reference](https://github.com/fastpii/fastpiifiles/blob/main/docs/api.md)
* [Detector Documentation](https://github.com/fastpii/fastpiifiles/blob/main/docs/detectors.md)
* [Integration Guides](https://github.com/fastpii/fastpiifiles/blob/main/docs/usage.md)
* [fastpii.com](https://fastpii.com)

---

## Contributing

Contributions welcome! See [Contributing Guide](CONTRIBUTING.md).

---

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

---

<div align="center">

Built for privacy-first AI applications

</div>