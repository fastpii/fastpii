#!/usr/bin/env python3
"""Extract Czech postal codes from OpenStreetMap PBF file.

Parses an OSM PBF file and extracts all Czech postal codes (PSČ).

Usage:
    python scripts/data/extract_cz_postal_codes.py <osm_file>

Arguments:
    osm_file: Path to the Czech Republic OSM PBF file.
              Download from: https://download.geofabrik.de/europe/czech-republic-latest.osm.pbf

Output:
    src/fastpii/data/countries/cz/postal_codes.py
"""

import sys

sys.path.insert(0, "src")

try:
    import osmium
except ImportError:
    print("Error: osmium is required.")
    print("Install with: pip install osmium")
    sys.exit(1)

from fastpii.data.extractors.postal_codes import PostalCodesExtractor


class PostalCodeHandler(osmium.SimpleHandler):
    """OSM handler that extracts postal codes from nodes and ways."""

    def __init__(self) -> None:
        super().__init__()
        self.postal_codes: set[str] = set()

    def _extract_postal_codes(self, tags) -> None:
        if "addr:postcode" in tags:
            code = tags["addr:postcode"].strip()
            code_clean = code.replace(" ", "")
            if code_clean.isdigit() and len(code_clean) == 5:
                self.postal_codes.add(code_clean)

    def node(self, n: osmium.osm.Node) -> None:
        self._extract_postal_codes(n.tags)

    def way(self, w: osmium.osm.Way) -> None:
        self._extract_postal_codes(w.tags)


class CzechPostalCodesExtractor(PostalCodesExtractor):
    """Extract Czech postal codes from OpenStreetMap."""

    country_code = "CZ"

    def __init__(self, osm_file: str) -> None:
        self.osm_file = osm_file
        self._postal_codes: set[str] | None = None

    def extract(self) -> set[str]:
        if self._postal_codes is not None:
            return self._postal_codes

        handler = PostalCodeHandler()
        handler.apply_file(self.osm_file)
        self._postal_codes = handler.postal_codes
        return self._postal_codes

    def get_source_url(self) -> str:
        return "https://download.geofabrik.de/europe/czech-republic.html"

    def get_license(self) -> str:
        return "ODbL"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/data/extract_cz_postal_codes.py <osm_file>")
        print("Download OSM file from: https://download.geofabrik.de/europe/czech-republic-latest.osm.pbf")
        sys.exit(1)

    osm_file = sys.argv[1]
    output = "src/fastpii/data/countries/cz/_data/postal_codes.py"
    extractor = CzechPostalCodesExtractor(osm_file)
    extractor.save(output)