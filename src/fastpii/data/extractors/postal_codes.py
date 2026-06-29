"""Postal codes extractor for any country.

Each country implements this with their specific source
(typically OpenStreetMap or national postal service).
"""

from abc import abstractmethod

from fastpii.data.extractors.base import BaseExtractor


class PostalCodesExtractor(BaseExtractor):
    """Abstract base class for postal code extraction.

    Extract postal codes from a geographic source and generate
    a Python file with POSTAL_CODES (set[str]).

    Example:
        class CzechPostalCodesExtractor(PostalCodesExtractor):
            country_code = 'CZ'

            def extract(self) -> set[str]:
                # Parse OSM PBF file for postal codes
                ...

            def get_source_url(self) -> str:
                return "https://download.geofabrik.de/europe/czech-republic.html"

            def get_license(self) -> str:
                return "ODbL"
    """

    def _data_type(self) -> str:
        return "Postal Codes"

    @abstractmethod
    def extract(self) -> set[str]:
        """Extract postal codes from source.

        Returns:
            Set of postal code strings.
        """

    def save(self, output_path: str) -> None:
        """Extract and save postal codes to a Python file.

        Generates a Python file with POSTAL_CODES: set[str].

        Args:
            output_path: path to output Python file.
        """
        postal_codes = self.extract()
        source = self.get_source(entry_count=len(postal_codes))

        with open(output_path, "w") as f:
            self._write_header(f, source)

            f.write("POSTAL_CODES: set[str] = {\n")
            for code in sorted(postal_codes):
                code_escaped = code.replace('"', '\\"')
                f.write(f'    "{code_escaped}",\n')
            f.write("}\n")

        print(f"Extracted {len(postal_codes)} postal codes to {output_path}")