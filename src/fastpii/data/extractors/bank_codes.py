"""Bank codes extractor for any country.

Each country implements this with their specific source
(e.g., scrape ČNB for Czech Republic, Bundesbank for Germany).
"""

from abc import ABC, abstractmethod
from typing import override

from fastpii.data.extractors.base import BaseExtractor


class BankCodesExtractor(BaseExtractor, ABC):
    """Abstract base class for bank code extraction.

    Extract bank codes from a national banking authority and generate
    a Python file with VALID_BANK_CODES (set) and BANK_NAMES (dict).

    Example:
        class CzechBankCodesExtractor(BankCodesExtractor):
            country_code = 'CZ'

            def extract(self) -> dict[str, str]:
                # Scrape ČNB website, return {code: name}
                ...

            def get_source_url(self) -> str:
                return "https://www.czso.cz/"

            def get_license(self) -> str:
                return "Public domain"
    """

    @override
    def _data_type(self) -> str:
        return "Bank Codes"

    @abstractmethod
    @override
    def extract(self) -> dict[str, str]:
        """Extract bank codes from source.

        Returns:
            Dict mapping bank code to bank name.
        """

    def save(self, output_path: str) -> None:
        """Extract and save bank codes to a Python file.

        Generates a Python file with:
            - VALID_BANK_CODES: set[str] of bank codes
            - BANK_NAMES: dict[str, str] mapping code to name

        Args:
            output_path: path to output Python file.
        """
        bank_codes = self.extract()
        source = self.get_source(entry_count=len(bank_codes))

        with open(output_path, "w") as f:
            self._write_header(f, source)

            f.write("VALID_BANK_CODES: set[str] = {\n")
            for code in sorted(bank_codes.keys()):
                f.write(f'    "{code}",\n')
            f.write("}\n\n")

            f.write("BANK_NAMES: dict[str, str] = {\n")
            for code, name in sorted(bank_codes.items()):
                name_escaped = name.replace('"', '\\"')
                f.write(f'    "{code}": "{name_escaped}",\n')
            f.write("}\n")

        print(f"Extracted {len(bank_codes)} bank codes to {output_path}")