"""Names extractor for any country.

Each country implements this with their specific source
(e.g., CZSO for Czech Republic, PESEL registry for Poland).
"""

from abc import ABC, abstractmethod
from typing import override

from fastpii.data.extractors.base import BaseExtractor


class NamesExtractor(BaseExtractor, ABC):
    """Abstract base class for name extraction.

    Extract male and female names from a source and generate
    Python files with MALE_NAMES (set[str]) and FEMALE_NAMES (set[str]).

    Example:
        class CzechNamesExtractor(NamesExtractor):
            country_code = 'CZ'

            def extract(self) -> dict[str, set[str]]:
                # Parse CZSO CSV for names
                ...

            def get_source_url(self) -> str:
                return "https://www.czso.cz/"

            def get_license(self) -> str:
                return "Public domain"
    """

    @override
    def _data_type(self) -> str:
        return "Names"

    @abstractmethod
    @override
    def extract(self) -> dict[str, set[str]]:
        """Extract names from source.

        Returns:
            Dict with 'male' and 'female' keys mapping to name sets.
        """

    def save(self, output_path_male: str, output_path_female: str) -> None:
        """Extract and save names to Python files.

        Generates two Python files:
            - MALE_NAMES: set[str]
            - FEMALE_NAMES: set[str]

        Args:
            output_path_male: path to output male names Python file.
            output_path_female: path to output female names Python file.
        """
        names = self.extract()
        male_names = names["male"]
        female_names = names["female"]
        total = len(male_names) + len(female_names)
        source = self.get_source(entry_count=total)

        with open(output_path_male, "w") as f:
            self._write_header(f, source)
            f.write("# Gender: male\n\n")
            f.write("MALE_NAMES: set[str] = {\n")
            for name in sorted(male_names):
                f.write(f'    "{name.lower()}",\n')
            f.write("}\n")

        with open(output_path_female, "w") as f:
            self._write_header(f, source)
            f.write("# Gender: female\n\n")
            f.write("FEMALE_NAMES: set[str] = {\n")
            for name in sorted(female_names):
                f.write(f'    "{name.lower()}",\n')
            f.write("}\n")

        print(f"Extracted {len(male_names)} male names, {len(female_names)} female names")