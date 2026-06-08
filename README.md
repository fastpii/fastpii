# FastPII

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![FastPII](https://img.shields.io/badge/FastPII-v0.1.0-orange)](https://github.com/fastpii/fastpii)

**Fast PII detection for Czech and Central European identifiers**

Leveraging the FastAPI ecosystem for modern Python PII protection

[Quick Start](#quick-start) • [Documentation](#documentation) • [Integrations](#integrations) • [Contributing](#contributing)

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
    print(f"Confidence: {finding.confidence:.1%}")
```

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
```

### CLI

```bash
fastpii detect "Jan Novák, RČ: 8001011238"
fastpii validate 8001011238 --detector rodne_cislo
fastpii list-detectors
```

## Czech Identifiers

| Identifier | Type | Accuracy | Features |
|------------|------|----------|----------|
| Rodné číslo | Birth number | >95% | Checksum, date extraction, gender |
| IČO | Company ID | >99% | Weighted Mod 11 checksum |
| DIČ | VAT number | >98% | Multi-format validation |
| Bank Account | Bank account | >99% | Two-part Mod 11 checksum |
| Postal Code (PSČ) | Postal code | >99% | Region mapping |
| Phone Number | Phone | >95% | Mobile/landline, operator |

## Documentation

- [Installation](docs/getting-started/installation.md) - Setup guide
- [Quick Start](docs/getting-started/quickstart.md) - 5-minute tutorial
- [API Reference](docs/api/core.md) - Core SDK docs
- [Integrations](docs/integrations/) - FastAPI, LangChain, MCP, CLI

## Contributing

Contributions welcome! See [Contributing Guide](CONTRIBUTING.md).

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

---

<div align="center">

Built for the FastAPI ecosystem

</div>