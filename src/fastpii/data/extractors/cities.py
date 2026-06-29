"""Cities extractor for any country.

Typically extracts from OpenStreetMap, but each country implements
their specific extraction logic.
"""

from abc import ABC, abstractmethod
from typing import override

from fastpii.data.extractors.base import BaseExtractor


__all__ = ["CitiesExtractor"]


class CitiesExtractor(BaseExtractor, ABC):
    """Abstract base class for city extraction.

    Extract city names from a geographic source and generate
    a Python file with CITIES (set[str]).

    Example:
        class CzechCitiesExtractor(CitiesExtractor):
            country_code = 'CZ'

            def extract(self) -> set[str]:
                # Parse OSM PBF file
                ...

            def get_source_url(self) -> str:
                return "https://download.geofabrik.de/europe/czech-republic.html"

            def get_license(self) -> str:
                return "ODbL"
    """

    @override
    def _data_type(self) -> str:
        return "Cities"

    @abstractmethod
    @override
    def extract(self) -> set[str]:
        """Extract cities from source.

        Returns:
            Set of city names (lowercase for consistency).
        """

    def save(self, output_path: str) -> None:
        """Extract and save cities to a Python file.

        Generates a Python file with CITIES: set[str].

        Args:
            output_path: path to output Python file.
        """
        cities = self.extract()
        source = self.get_source(entry_count=len(cities))

        with open(output_path, "w") as f:
            self._write_header(f, source)

            f.write("CITIES: set[str] = {\n")
            for city in sorted(cities):
                city_escaped = city.replace('"', '\\"')
                f.write(f'    "{city_escaped}",\n')
            f.write("}\n")

        print(f"Extracted {len(cities)} cities to {output_path}")
