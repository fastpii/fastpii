# FastPII

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![FastPII](https://img.shields.io/badge/FastPII-v0.2.2-orange)](https://github.com/fastpii/fastpii)

**Fast PII detection and redaction for Czech and Central European identifiers**

Leveraging the FastAPI ecosystem for modern Python PII protection

[Quick Start](#quick-start) • [Redaction API](#redaction-api) • [Detectors](#czech-identifiers) • [Documentation](#documentation) • [Integrations](#integrations)

</div>

---

## Why FastPII?

**Performance meets Accuracy:**

| PII Type | FastPII | Microsoft Presidio | AWS Macie | Google DLP |
|----------|---------|---------------------|-----------|------------|
| Rodné číslo (CZ) | **>95%** | 22.7% | 18.4% | 15.9% |
| IČO (CZ) | **>99%** | 45.3% | 38.7% | 41.2% |
| DIČ (CZ) | **>98%** | 31.2% | 24.6% | 28.8% |

**Why the difference?**

- Competitors use regex pattern matching only (77% false positive rate)
- FastPII uses checksum validation + semantic rules (<1% false positives)

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
text = "Jan Novák, RČ: 8001011238, IČO: 25596641"
result = guard.detect(text)

for finding in result.findings:
    print(f"{finding.type}: {finding.value}")
    print(f"  Confidence: {finding.confidence:.1%}")
    print(f"  Position: {finding.start}-{finding.end}")
    if finding.metadata:
        print(f"  Metadata: {finding.metadata}")

# Validate specific identifiers
validation = guard.validate("8001011238", "rodne_cislo")
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
guard.anonymize("Email: jan@email.cz, RČ: 8001011238")
# → "Email: [REDACTED], RČ: [REDACTED]"

# Custom placeholder
guard.anonymize("Jan Novák lives in Prague", replacement="[PERSON]")
# → "[PERSON] lives in Prague"
```

### Redact — Replace with PII type label

```python
guard.redact("Email: jan@email.cz, RČ: 8001011238")
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

| Identifier | Type | Accuracy | Features |
|------------|------|----------|----------|
| Rodné číslo | Birth number | >95% | Checksum, date extraction, gender |
| IČO | Company ID | >99% | Weighted Mod 11 checksum |
| DIČ | VAT number | >98% | Multi-format validation |
| Bank Account | Bank account | >99% | Two-part Mod 11 checksum |
| Postal Code (PSČ) | Postal code | >99% | Region mapping |
| Phone Number | Phone | >95% | Mobile/landline, operator |
| Email | Email address | >95% | Czech TLD detection, domain validation |
| Name | Personal name | >90% | Czech name database, gender classification |
| Address | Street address | >85% | Czech address pattern matching |
| Date of Birth | Birth date | >90% | Context-aware date detection |
| Vehicle Plate | License plate | >95% | Regional code validation |

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
safe_text = anonymizer("Jan Novák, RČ: 8001011238")
# Output: "Jan Novák, [REDACTED]"

# Redaction modes available
result = anonymizer.anonymize("Email: jan@email.cz")
result = anonymizer.redact("RČ: 8001011238")
result = anonymizer.mask("IČO: 25596641")
result = anonymizer.remove("Phone: +420 777 123 456")
```

### CLI

```bash
fastpii detect "Jan Novák, RČ: 8001011238"
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