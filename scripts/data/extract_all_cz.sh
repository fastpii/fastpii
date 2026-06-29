#!/bin/bash
# Extract ALL Czech data for FastPII
#
# This script runs all Czech extraction scripts in sequence.
# Some scripts require external dependencies:
#   - requests, beautifulsoup4 (for bank codes)
#   - osmium (for cities and postal codes)
#
# Usage:
#   bash scripts/data/extract_all_cz.sh
#
# Prerequisites:
#   - Download OSM file first:
#     wget -O data/czech-republic-latest.osm.pbf \
#       https://download.geofabrik.de/europe/czech-republic-latest.osm.pbf
#   - Install dependencies:
#     pip install requests beautifulsoup4 osmium

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

# Step 3: Check for OSM file
OSM_FILE="data/czech-republic-latest.osm.pbf"
if [ ! -f "$OSM_FILE" ]; then
    echo "Step 3: OSM file not found at $OSM_FILE"
    echo "  Download it first:"
    echo "  mkdir -p data"
    echo "  wget -O $OSM_FILE https://download.geofabrik.de/europe/czech-republic-latest.osm.pbf"
    echo "  Skipping cities and postal codes extraction."
else
    # Step 4: Cities (requires osmium)
    echo "Step 4: Cities..."
    python scripts/data/extract_cz_cities.py "$OSM_FILE" || echo "  Warning: City extraction failed (requires osmium)"

    # Step 5: Postal codes (requires osmium)
    echo "Step 5: Postal codes..."
    python scripts/data/extract_cz_postal_codes.py "$OSM_FILE" || echo "  Warning: Postal code extraction failed (requires osmium)"
fi

# Step 6: Names (requires requests)
echo "Step 6: Names..."
python scripts/data/extract_cz_names.py || echo "  Warning: Name extraction failed (requires requests)"

echo ""
echo "=== Czech data extraction complete ==="
echo "Generated files:"
ls -la src/fastpii/data/countries/cz/ 2>/dev/null || echo "  (No files generated — check errors above)"