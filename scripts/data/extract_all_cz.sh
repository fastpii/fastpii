#!/bin/bash
# Extract ALL Czech data for FastPII
#
# This script runs all Czech extraction scripts in sequence.
# Some scripts require external dependencies:
#   - requests, beautifulsoup4 (for bank codes)
#   - requests (for cities, postal codes, and streets from ČÚZK RÚIAN)
#
# Usage:
#   bash scripts/data/extract_all_cz.sh
#
# Install dependencies:
#   pip install requests beautifulsoup4

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_DIR"

echo "=== Extracting Czech Republic data ==="
echo ""

# Step 1: Bank codes (requires requests, beautifulsoup4)
echo "Step 1: Bank codes..."
python scripts/data/extract_cz_bank_codes.py || echo "  Warning: Bank code extraction failed (requires requests, beautifulsoup4)"

# Step 2: Insurance codes (hardcoded, no dependencies)
echo "Step 2: Insurance codes..."
python scripts/data/extract_cz_insurance_codes.py

# Step 3: Cities, postal codes, and streets from ČÚZK RÚIAN (requires requests)
echo "Step 3: Cities, postal codes, and streets from ČÚZK RÚIAN..."
python scripts/data/extract_cz_ruvian.py || echo "  Warning: RÚIAN extraction failed (requires requests)"

# Step 4: Names (requires requests)
echo "Step 4: Names..."
python scripts/data/extract_cz_names.py || echo "  Warning: Name extraction failed (requires requests)"

echo ""
echo "=== Czech data extraction complete ==="
echo "Generated files:"
ls -la src/fastpii/countries/cz/data/_data/ 2>/dev/null || echo "  (No files generated — check errors above)"
