#!/usr/bin/env python3
"""Extract Czech cities from OpenStreetMap PBF file.

Parses an OSM PBF file and extracts all cities, towns, villages,
and municipalities in the Czech Republic.

Usage:
    python scripts/data/extract_cz_cities.py <osm_file>

Arguments:
    osm_file: Path to the Czech Republic OSM PBF file.
              Download from: https://download.geofabrik.de/europe/czech-republic-latest.osm.pbf

Output:
    src/fastpii/data/countries/cz/cities.py
"""

import sys

sys.path.insert(0, "src")

try:
    import osmium
except ImportError:
    print("Error: osmium is required.")
    print("Install with: pip install osmium")
    sys.exit(1)

from fastpii.data.extractors.cities import CitiesExtractor


CITY_PLACE_TAGS = {"city", "town", "village", "suburb", "municipality"}


class CityHandler(osmium.SimpleHandler):
    """OSM handler that extracts city names from nodes and ways."""

    def __init__(self) -> None:
        super().__init__()
        self.cities: set[str] = set()

    def _extract_city(self, tags: osmium.TagList) -> None:
        place_type = tags.get("place", "")
        if place_type in CITY_PLACE_TAGS:
            name = tags.get("name", "")
            if name:
                self.cities.add(name.lower())

    def node(self, n: osmium.osm.Node) -> None:
        self._extract_city(n.tags)

    def way(self, w: osmium.osm.Way) -> None:
        self._extract_city(w.tags)


class CzechCitiesExtractor(CitiesExtractor):
    """Extract Czech cities from OpenStreetMap."""

    country_code = "CZ"

    def __init__(self, osm_file: str) -> None:
        self.osm_file = osm_file
        self._cities: set[str] | None = None

    def extract(self) -> set[str]:
        if self._cities is not None:
            return self._cities

        handler = CityHandler()
        handler.apply_file(self.osm_file)
        self._cities = handler.cities
        return self._cities

    def get_source_url(self) -> str:
        return "https://download.geofabrik.de/europe/czech-republic.html"

    def get_license(self) -> str:
        return "ODbL"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/data/extract_cz_cities.py <osm_file>")
        print("Download OSM file from: https://download.geofabrik.de/europe/czech-republic-latest.osm.pbf")
        sys.exit(1)

    osm_file = sys.argv[1]
    output = "src/fastpii/data/countries/cz/_cities.py"
    extractor = CzechCitiesExtractor(osm_file)
    extractor.save(output)