# FastPII

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![FastPII](https://img.shields.io/badge/FastPII-v0.2.4-orange)](https://github.com/fastpii/fastpii)

**Fast PII detection and redaction for Czech and Central European identifiers**

Leveraging the FastAPI ecosystem for modern Python PII protection

[Quick Start](#quick-start) • [Redaction API](#redaction-api) • [Detectors](#czech-identifiers) • [Benchmark](#benchmark) • [Documentation](#documentation) • [Integrations](#integrations)

</div>

---

## Why FastPII?

Czech identifiers — rodné číslo, IČO, DIČ, bank accounts — have structural checksums that generic PII tools ignore. FastPII uses these checksums plus semantic context rules to cut false positives that catch regex-only tools.

**What makes FastPII different:**

- **Checksum validation** — Rodné číslo (Mod 11), IČO (weighted Mod 11), bank accounts (two-part checksum) — rejects structurally invalid identifiers that regex-only tools accept
- **Context-aware detection** — Phone numbers require nearby context words or +420 prefix; postal codes require PSČ labels, city names, or address proximity; dates of birth need birth-related keywords nearby
- **Entity overlap resolution** — When address and postal code overlap, the higher-priority entity wins. No duplicate redactions.

## Features

- Region-specific detection (Czech Republic foundation)
- Checksum validation for all identifiers
- **4 redaction modes**: anonymize, redact, mask, remove
- Framework-independent core SDK
- FastAPI integration
- LangChain integration (LLM-ready)
- MCP server (Claude Desktop)
- CLI tool (fastpii detect)
- Zero dependencies in core

## Installation

```bash
pip install fastpii
```

## Quick Start

```python
from fastpii import PrivacyGuard

# Initialize
guard = PrivacyGuard(regions=["cz"])

# Detect PII
text = "Jan Novák, RČ: 800101/1238, IČO: 25596641"
result = guard.detect(text)

for finding in result.findings:
    print(f"{finding.type}: {finding.value}")
    print(f"  Confidence: {finding.confidence:.1%}")
    print(f"  Position: {finding.start}-{finding.end}")
    if finding.metadata:
        print(f"  Metadata: {finding.metadata}")

# Validate specific identifiers
validation = guard.validate("800101/1238", "rodne_cislo")
print(f"Valid: {validation.is_valid}")
if validation.metadata:
    print(f"Gender: {validation.metadata.get('gender')}")
    print(f"Birth date: {validation.metadata.get('birth_date')}")
```

## Redaction API

FastPII provides four redaction modes to handle detected PII:

### Anonymize — Replace with a placeholder

```python
guard = PrivacyGuard(regions=["cz"])
guard.anonymize("Email: jan@email.cz, RČ: 800101/1238")
# → "Email: [REDACTED], RČ: [REDACTED]"

# Custom placeholder
guard.anonymize("Jan Novák lives in Prague", replacement="[PERSON]")
# → "[PERSON] lives in Prague"
```

### Redact — Replace with PII type label

```python
guard.redact("Email: jan@email.cz, RČ: 800101/1238")
# → "Email: [EMAIL], RČ: [RODNE_CISLO]"
```

### Mask — Replace with asterisks matching original length

```python
guard.mask("Email: jan@email.cz")
# → "Email: *************"
```

### Remove — Delete PII entirely

```python
guard.remove("Email: jan@email.cz")
# → "Email: "
```

All redaction methods use position-based replacement (sorted by position descending) to maintain correct character indices when multiple PII items overlap.

## Czech Identifiers

| Identifier | Type | Features |
|------------|------|----------|
| Rodné číslo | Birth number | Mod 11 checksum, date extraction, gender |
| IČO | Company ID | Weighted Mod 11 checksum |
| DIČ | VAT number | Multi-format validation |
| Bank Account | Bank account | Two-part Mod 11 checksum |
| Postal Code (PSČ) | Postal code | Region mapping, context validation |
| Phone Number | Phone | Mobile/landline, operator, context-aware |
| Email | Email address | Czech TLD detection, markdown mailto handling |
| Name | Personal name | Czech name database, gender classification |
| Address | Street address | Component scoring (street/number/city/postal) |
| Date of Birth | Birth date | Context-aware (birth keywords, intervening date blocking) |
| Vehicle Plate | License plate | Regional code validation |

## Benchmark

Tested on Czech-focused evaluation datasets covering real-world documents (contracts, medical records, business registries, support tickets) and adversarial false-positive traps.

**v0.2.4 overall:**

| Metric | Score |
|--------|-------|
| Precision | **84.2%** |
| Recall | **80.0%** |
| F1 | **82.1%** |

**Per-detector highlights:**

| Detector | Precision | Recall | Notes |
|----------|-----------|--------|-------|
| IČO | 100% | 100% | Checksum-validated, no FPs |
| DIČ | 100% | 100% | Multi-format detection |
| Email | 100% | 100% | Markdown mailto handled |
| Date of Birth | 100% | 86% | Context-gated; rejects generic dates |
| Date | 100% | 100% | Non-birth dates detected separately |
| Phone | 100% | 100% | Context or +420 prefix required |
| Vehicle Plate | 100% | 100% | Regional code validation |
| Address | 71% | 63% | Component scoring; partial matches in structured layouts |
| Postal Code | 100% | 71% | Subsumed by address in overlaps; bare codes context-gated |
| Name | 80% | 100% | Dict-matched; "Novák Consulting" FP |
| Rodné číslo | 67% | 50% | Invalid checksums correctly rejected; context-ambiguous FPs |
| Bank Account | 100% | 0% | Requires labeled context (v0.2.5) |

**Adversarial false-positive trap (text7.txt):** 5 FPs from identifiers appearing in non-PII context ("code 25596641", "reference CZ25596641"). A planned "strict" mode will handle these.

## Roadmap

### v0.2.5 (Next)

- **Company-aware name detection** — Block corporate names like "Novák Consulting s.r.o." from name detector
- **Extended bank-account labels** — Support "Account Number:", "Secondary Account:", "Account:" as context triggers
- **Full-address span merging** — Merge street + number + city + postal into single address finding when adjacent
- **Optional "strict" mode** — For adversarial contexts (legal docs, support tickets). Higher precision, lower recall. Requires explicit PII labels or stronger context signals

### v0.3+ — Real-world integrations

- FastAPI middleware
- LangChain output parser
- RAG pipeline sanitization
- MCP server for Claude Desktop

## Integrations

### FastAPI

```python
from fastapi import FastAPI
from fastpii.integrations.fastapi import create_app

app = create_app()
# Run: uvicorn fastpii.integrations.fastapi:app --reload
```

### LangChain

```python
from fastpii.integrations.langchain import PIIAnonymizer

anonymizer = PIIAnonymizer(regions=["cz"])
safe_text = anonymizer("Jan Novák, RČ: 800101/1238")
# Output: "Jan Novák, [REDACTED]"

# Redaction modes available
result = anonymizer.anonymize("Email: jan@email.cz")
result = anonymizer.redact("RČ: 800101/1238")
result = anonymizer.mask("IČO: 25596641")
result = anonymizer.remove("Phone: +420 777 123 456")
```

### CLI

```bash
fastpii detect "Jan Novák, RČ: 800101/1238"
fastpii validate 8001011238 --detector rodne_cislo
fastpii list-detectors
```

## Documentation

Documentation is available at [fastpii.com](https://fastpii.com) and in the [fastpiifiles](https://github.com/fastpii/fastpiifiles) repository:

- [Detectors](https://github.com/fastpii/fastpiifiles/blob/main/docs/detectors.md) - All 11 detectors explained
- [API Reference](https://github.com/fastpii/fastpiifiles/blob/main/docs/api.md) - Core SDK docs
- [Usage Guide](https://github.com/fastpii/fastpiifiles/blob/main/docs/usage.md) - Complete usage examples

## Contributing

Contributions welcome! See [Contributing Guide](CONTRIBUTING.md).

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

---

<div align="center">

Built for the FastAPI ecosystem

</div>