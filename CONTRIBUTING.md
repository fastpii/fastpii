# Contributing to FastPII

Thank you for your interest in contributing to FastPII!

## Setup

```bash
git clone https://github.com/fastpii/fastpii.git
cd fastpii
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Development

```bash
pytest                    # Run tests
pytest --benchmark        # Run benchmarks
pyright src/              # Type check
ruff check src/ tests/    # Lint
```

## Coding Standards

- No external dependencies for the core package
- Type hints on all public APIs
- All detectors must have checksum validation where applicable
- Country data must use ASCII transliteration (e.g., "muenchen" not "münchen")
- Empty data modules return `{}` (dict) or `set()` — never `None`
- No unnecessary comments or docstrings in implementation code

## Adding a Country Pack

See [docs/ADD_A_COUNTRY_PACK.md](docs/ADD_A_COUNTRY_PACK.md) for the full guide.

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Ensure all tests pass and types check
5. Submit a PR with a clear description

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.