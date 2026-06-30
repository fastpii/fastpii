# Czech PII Benchmark Corpus — Changelog

## v1.0 (2026-06-29)

Initial release of the Czech PII benchmark corpus.

### Coverage

| Detector | Positive Samples | Negative Samples |
|----------|-----------------|-----------------|
| rodne_cislo | 23 | 179 |
| ico | 24 | 176 |
| dic | 21 | 179 |
| bank_account | 26 | 176 |
| postal_code | 28 | 175 |
| phone | 32 | 173 |
| date_of_birth | 17 | 185 |
| address | 26 | 179 |
| name | 29 | 177 |
| email | 33 | 173 |
| vehicle_plate | 18 | 182 |
| date | 24 | 180 |
| identity_card | 16 | 184 |
| health_insurance | 17 | 183 |
| iban | 17 | 183 |
| credit_card | 16 | 184 |

### Categories

| Category | Count |
|----------|-------|
| support_ticket | 35 |
| mixed | 28 |
| invoice | 30 |
| false_positive_trap | 24 |
| contract | 24 |
| medical_record | 20 |
| email | 17 |
| bank_statement | 12 |
| business_registry | 10 |

### Difficulty Distribution

| Difficulty | Count |
|-----------|-------|
| easy | 66 |
| medium | 81 |
| hard | 53 |

### Corpus Files

| File | Description | Samples |
|------|-------------|---------|
| cz_migrated.json | Migrated from eval_v024.py ground truth | 30 |
| cz_phase1.json | Core detector coverage (RC, ICO, DIC, bank, postal) | 50 |
| cz_phase2.json | Extended detectors (address, name, email, vehicle, date) | 80 |
| cz_supplement.json | Edge cases, hard samples, false positive traps | 40 |

### Validation

- All 200 samples pass schema validation
- All 200 samples pass coverage validation (15+ positive per detector, 10+ negative)
- All 200 samples pass quality validation (no duplicate IDs, no empty findings)