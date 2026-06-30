# FastPII

Protect sensitive information before it reaches AI.

FastPII is an open-source privacy engine that detects, validates, and transforms PII. Deterministic, local, and fast.

[![PyPI](https://img.shields.io/pypi/v/fastpii.svg)](https://pypi.org/project/fastpii/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Docs](https://img.shields.io/badge/docs-docs.fastpii.com-blue)](https://docs.fastpii.com)

[Documentation](https://docs.fastpii.com) · [PyPI](https://pypi.org/project/fastpii/) · [Discussions](https://github.com/fastpii/fastpii/discussions) · [Contributing](CONTRIBUTING.md)

---

## Install

```bash
pip install fastpii
```

## Quick Start

```python
from fastpii import FastPII, DEFAULT_PRIORITY
from fastpii.countries.cz import CzechPack

engine = FastPII(priority=DEFAULT_PRIORITY)
engine.register(CzechPack())

result = engine.detect("Jan Novák, RČ: 800101/1238, IČO: 25596641")
for f in result.findings:
    print(f"{f.type}: {f.value} ({f.confidence:.0%})")
```

CLI:

```bash
fastpii detect "Jan Novák, RČ: 800101/1238" -r cz
```

---

## Why FastPII

- **Built for AI** designed for LLM prompts, RAG pipelines, and AI agents
- **Deterministic** no LLM calls, no cloud dependency, <1ms per detection
- **Country-aware** checksum validation for official identifiers (Rodné číslo, PESEL, Steuer-ID, SIREN)
- **Self-hosted** zero external dependencies, runs locally
- **Open Source** Apache 2.0, fully auditable

---

## Features

- **Detect** find PII in text with context-aware detection
- **Validate** verify identifiers with checksum algorithms
- **Anonymize** replace PII with `[REDACTED]`
- **Redact** replace PII with type labels like `[EMAIL]`
- **Mask** replace PII with asterisks
- **Remove** delete PII entirely
- **FastAPI** drop-in REST API
- **LangChain** anonymizer and filter for LLM chains
- **MCP** Model Context Protocol for AI agents
- **CLI** command-line detection and validation

---

## Country Support

**Production**

🇨🇿 Czech Republic
15 detectors with checksum validation

**Beta**

🇵🇱 Poland
PESEL, NIP, REGON, phone, postal code, address

🇩🇪 Germany
Steuer-ID, USt-IdNr, Handelsregister, phone, postal code, address

🇫🇷 France
SIREN, SIRET, INSEE/NIR, phone, postal code, address

[Country documentation →](https://docs.fastpii.com/countries)

---

## Integrations

```python
from fastpii.integrations.fastapi import create_app
from fastpii.integrations.langchain import PIIAnonymizer
from fastpii.integrations.mcp import MCPServer
```

---

## Architecture

```
Your Application
       ↓
    FastPII
       ↓
   Your AI
```

You configure. It executes. Explicit registration, no hidden defaults.

---

## Documentation

- [Getting Started](https://docs.fastpii.com)
- [API Reference](https://docs.fastpii.com/api)
- [Country Packs](https://docs.fastpii.com/countries)
- [Benchmarks](https://docs.fastpii.com/benchmarks)
- [Examples](https://docs.fastpii.com/examples)
- [Architecture](https://docs.fastpii.com/architecture)
- [Migration Guide](docs/MIGRATION_GUIDE.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

---

## Ecosystem

- **FastPII Core** this repository, Apache 2.0
- **Country Intelligence Packs** extended data and detection for more countries
- **FastPII Secure Chat** hosted privacy-first AI chat
- **FastPII Enterprise** governance, audit trails, compliance

[https://fastpii.com](https://fastpii.com)

---

## Community

- [GitHub Discussions](https://github.com/fastpii/fastpii/discussions)
- [GitHub Issues](https://github.com/fastpii/fastpii/issues)
- [Contributing Guide](CONTRIBUTING.md)

## Contributing

Contributions welcome. Country packs, validators, benchmarks, and documentation.

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and guidelines.

## License

Apache 2.0. See [LICENSE](LICENSE).

---

Privacy should be a default, not an afterthought.