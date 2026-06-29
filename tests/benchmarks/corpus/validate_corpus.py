"""Validate the Czech PII benchmark corpus.

Checks schema compliance, coverage completeness, and data quality.
"""

import json
from pathlib import Path

CORPUS_DIR = Path(__file__).parent

REQUIRED_TYPES = [
    "rodne_cislo", "ico", "dic", "bank_account",
    "postal_code", "phone", "date_of_birth", "address",
    "name", "email", "vehicle_plate", "date",
    "identity_card", "health_insurance", "iban", "credit_card",
]

CATEGORIES = [
    "contract", "medical_record", "bank_statement",
    "business_registry", "support_ticket", "email",
    "invoice", "mixed", "false_positive_trap",
]

MIN_POSITIVE_PER_TYPE = 15
MIN_NEGATIVE_PER_TYPE = 10
MIN_TOTAL_SAMPLES = 200


def load_corpus() -> list[dict]:
    samples: list[dict] = []
    for path in sorted(CORPUS_DIR.glob("*.json")):
        if path.name == "schema.json":
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            samples.extend(data.get("samples", []))
    return samples


def validate_schema(samples: list[dict]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()

    for s in samples:
        sid = s.get("id", "")
        if sid in seen_ids:
            errors.append(f"Duplicate id: {sid}")
        seen_ids.add(sid)

        if not sid.startswith("CZ-") or len(sid.split("-")) != 3:
            errors.append(f"Invalid id format: {sid}")

        for field in ("id", "category", "description", "input", "expected_findings", "difficulty"):
            if field not in s:
                errors.append(f"Missing field '{field}' in {sid}")

        if s.get("category") not in CATEGORIES:
            errors.append(f"Invalid category in {sid}: {s.get('category')}")

        if s.get("difficulty") not in ("easy", "medium", "hard"):
            errors.append(f"Invalid difficulty in {sid}: {s.get('difficulty')}")

        for finding in s.get("expected_findings", []):
            if "type" not in finding or "value" not in finding:
                errors.append(f"Invalid finding in {sid}: {finding}")
            elif finding["type"] not in REQUIRED_TYPES:
                errors.append(f"Unknown type in {sid}: {finding['type']}")

    return errors


def validate_coverage(samples: list[dict]) -> list[str]:
    errors: list[str] = []

    positive_counts: dict[str, int] = {t: 0 for t in REQUIRED_TYPES}
    negative_counts: dict[str, int] = {t: 0 for t in REQUIRED_TYPES}

    for s in samples:
        findings = s.get("expected_findings", [])
        if not findings:
            for t in REQUIRED_TYPES:
                negative_counts[t] += 1
            continue

        types_in_sample = set()
        for f in findings:
            t = f.get("type", "")
            if t in positive_counts:
                positive_counts[t] += 1
                types_in_sample.add(t)

        for t in REQUIRED_TYPES:
            if t not in types_in_sample:
                negative_counts[t] += 1

    for t in REQUIRED_TYPES:
        if positive_counts[t] < MIN_POSITIVE_PER_TYPE:
            errors.append(f"{t}: only {positive_counts[t]} positive samples (need {MIN_POSITIVE_PER_TYPE})")
        if negative_counts[t] < MIN_NEGATIVE_PER_TYPE:
            errors.append(f"{t}: only {negative_counts[t]} negative samples (need {MIN_NEGATIVE_PER_TYPE})")

    if len(samples) < MIN_TOTAL_SAMPLES:
        errors.append(f"Only {len(samples)} total samples (need {MIN_TOTAL_SAMPLES})")

    return errors


def validate_quality(samples: list[dict]) -> list[str]:
    errors: list[str] = []

    for s in samples:
        sid = s.get("id", "unknown")
        input_text = s.get("input", "")

        if len(input_text.strip()) == 0:
            errors.append(f"{sid}: empty input text")

        for f in s.get("expected_findings", []):
            value = f.get("value", "")
            if not value:
                errors.append(f"{sid}: empty finding value")
                continue

            if "start" in f and "end" in f:
                start, end = f["start"], f["end"]
                if start < 0 or end < 0:
                    errors.append(f"{sid}: negative offset for '{value}'")
                elif end <= start:
                    errors.append(f"{sid}: end <= start for '{value}'")
                elif input_text[start:end] != value:
                    errors.append(f"{sid}: offset mismatch for '{value}': "
                                  f"input[{start}:{end}]='{input_text[start:end]}'")

    return errors


def main() -> None:
    samples = load_corpus()
    print(f"Loaded {len(samples)} samples from corpus")

    all_errors: list[str] = []

    schema_errors = validate_schema(samples)
    all_errors.extend(schema_errors)
    print(f"Schema validation: {len(schema_errors)} errors")

    coverage_errors = validate_coverage(samples)
    all_errors.extend(coverage_errors)
    print(f"Coverage validation: {len(coverage_errors)} errors")

    quality_errors = validate_quality(samples)
    all_errors.extend(quality_errors)
    print(f"Quality validation: {len(quality_errors)} errors")

    if all_errors:
        print("\n❌ VALIDATION FAILED:")
        for e in all_errors:
            print(f"  - {e}")
        raise SystemExit(1)
    else:
        print("\n✅ ALL VALIDATIONS PASSED")


if __name__ == "__main__":
    main()