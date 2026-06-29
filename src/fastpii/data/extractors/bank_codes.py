"""Bank codes extractor for any country.

Each country implements this with their specific source
(e.g., scrape ČNB for Czech Republic, Bundesbank for Germany).
"""

from abc import ABC, abstractmethod
from typing import override

from fastpii.data.extractors.base import BaseExtractor


__all__ = ["BankCodesExtractor"]


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

    def save(self, output_path: str, *, set_var: str = "VALID_BANK_CODES", dict_var: str = "BANK_NAMES", label: str = "bank codes") -> None:
        """Extract and save bank codes to a Python file.

        Generates a Python file with:
            - {set_var}: set[str] of bank codes
            - {dict_var}: dict[str, str] mapping code to name

        Args:
            output_path: path to output Python file.
            set_var: name of the set variable in the output file.
            dict_var: name of the dict variable in the output file.
            label: label for the print message.
        """
        bank_codes = self.extract()
        source = self.get_source(entry_count=len(bank_codes))

        with open(output_path, "w") as f:
            self._write_header(f, source)

            f.write(f"{set_var}: set[str] = {{\n")
            for code in sorted(bank_codes.keys()):
                f.write(f'    "{code}",\n')
            f.write("}\n\n")

            f.write(f"{dict_var}: dict[str, str] = {{\n")
            for code, name in sorted(bank_codes.items()):
                name_escaped = name.replace('"', '\\"')
                f.write(f'    "{code}": "{name_escaped}",\n')
            f.write("}\n")

        print(f"Extracted {len(bank_codes)} {label} to {output_path}")
