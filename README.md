# FastPII

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![FastPII](https://img.shields.io/badge/FastPII-v0.2.4-orange)](https://github.com/fastpii/fastpii)

</div>

Privacy infrastructure for AI applications handling Czech and European data.

FastPII helps developers detect, validate, anonymize, and protect sensitive data before it reaches LLMs, RAG systems, vector databases, AI agents, or third-party AI providers.

Built for AI-native applications. Designed for privacy-first architectures.

---

## Why FastPII?

Most PII tools are built for generic text processing.

FastPII is built for AI workflows.

Modern applications increasingly send documents, prompts, support tickets, contracts, medical records, and business data directly into:

* OpenAI
* Claude
* Gemini
* Ollama
* LangChain
* LlamaIndex
* Vector Databases
* AI Agents

FastPII acts as the privacy layer between your data and your AI systems.

```text
Without FastPII

Document
↓
LLM

Sensitive data exposed
```

```text
With FastPII

Document
↓
FastPII
↓
LLM

Sensitive data protected
```

---

## Why FastPII Is Different

### Czech-Native Detection

Unlike generic PII tools, FastPII understands Czech identifiers and validation rules.

Supported entities include:

* Rodné číslo
* IČO
* DIČ
* Bank Accounts
* Phone Numbers
* Postal Codes (PSČ)
* Addresses
* Personal Names
* Vehicle Plates
* Dates of Birth
* Email Addresses

---

### Checksum Validation

FastPII validates identifiers instead of relying solely on pattern matching.

Examples:

* Rodné číslo (Mod 11)
* IČO (Weighted Mod 11)
* Czech Bank Accounts
* DIČ Formats

Invalid identifiers are rejected before classification.

---

### Context-Aware Detection

Detection is not based on regex alone.

Examples:

* Phone numbers require context or valid Czech formats
* Postal codes require address context
* Dates of birth require birth-related keywords
* Addresses use component scoring

This significantly reduces false positives.

---

### Built for AI Workflows

FastPII is designed to integrate directly into:

* RAG Pipelines
* LangChain Applications
* MCP Servers
* AI Agents
* FastAPI Applications
* Enterprise AI Systems

---

## Features

### Detection

Identify sensitive Czech and European data.

### Validation

Validate identifiers using official checksum rules.

### Privacy Protection

Four privacy modes:

* Anonymize
* Redact
* Mask
* Remove

### Framework-Independent SDK

Use FastPII as a standalone Python package.

### Integrations

* FastAPI
* LangChain
* MCP
* CLI

### Local First

No cloud services required.

No LLM required.

No external API calls required.

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

text = """
Jan Novák
RČ: 800101/1238
IČO: 25596641
"""

result = guard.detect(text)

for finding in result.findings:
    print(f"{finding.type}: {finding.value}")
```

---

## Privacy Modes

### Anonymize

```python
guard.anonymize(
    "Jan Novák, RČ: 800101/1238"
)
```

Output:

```text
[REDACTED], [REDACTED]
```

---

### Redact

```python
guard.redact(
    "Jan Novák, RČ: 800101/1238"
)
```

Output:

```text
[NAME], [RODNE_CISLO]
```

---

### Mask

```python
guard.mask(
    "Jan Novák"
)
```

Output:

```text
*********
```

---

### Remove

```python
guard.remove(
    "Jan Novák"
)
```

Output:

```text

```

---

## AI Use Cases

### Protect RAG Pipelines

```python
safe_document = guard.anonymize(document)

embeddings = embed_model.embed(
    safe_document
)
```

---

### Protect LLM Prompts

```python
safe_prompt = guard.anonymize(prompt)

response = llm.invoke(
    safe_prompt
)
```

---

### Protect MCP Tools

```python
safe_input = guard.anonymize(user_input)

result = tool.execute(
    safe_input
)
```

---

## Supported Czech Entities

| Entity        | Validation |
| ------------- | ---------- |
| Rodné číslo   | ✓          |
| IČO           | ✓          |
| DIČ           | ✓          |
| Bank Account  | ✓          |
| Postal Code   | ✓          |
| Phone Number  | ✓          |
| Email         | ✓          |
| Address       | ✓          |
| Name          | ✓          |
| Vehicle Plate | ✓          |
| Date of Birth | ✓          |

---

## Benchmarks

FastPII is evaluated using Czech-focused datasets containing:

* Contracts
* Medical Records
* Business Registries
* Support Tickets
* Adversarial False-Positive Scenarios

Current Results (v0.2.4)

| Metric    | Score |
| --------- | ----- |
| Precision | 84.2% |
| Recall    | 80.0% |
| F1 Score  | 82.1% |

---

## Roadmap

### Current

* Core SDK
* Czech Detectors
* Validation Engine
* CLI
* FastAPI Integration
* LangChain Integration

### Next

* MCP Integration
* RAG Middleware
* Strict Mode
* Improved Address Detection
* Improved Bank Account Detection

### Future

* FastPII Gateway
* Policy Engine
* Audit Logging
* Enterprise Features
* Additional European Regions

---

## Vision

FastPII is evolving from a Czech PII detection library into privacy infrastructure for AI systems.

Our long-term goal is to become the privacy layer between sensitive data and AI.

```text
Data
↓
FastPII
↓
LLM
```

---

## Documentation

* Quick Start
* API Reference
* Detector Documentation
* Integration Guides
* Contributing Guide

---

## License

Apache 2.0

---

Built for privacy-first AI applications.