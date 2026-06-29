#!/usr/bin/env python3
"""Extract Czech bank codes from ČNB website.

Scrapes the Czech Statistical Office website for valid bank codes
and generates a Python data module.

Usage:
    python scripts/data/extract_cz_bank_codes.py

Output:
    src/fastpii/data/countries/cz/bank_codes.py
"""

import sys

sys.path.insert(0, "src")

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: requests and beautifulsoup4 are required.")
    print("Install with: pip install requests beautifulsoup4")
    sys.exit(1)

from fastpii.data.extractors.bank_codes import BankCodesExtractor


class CzechBankCodesExtractor(BankCodesExtractor):
    """Extract bank codes from Czech National Bank."""

    country_code = "CZ"

    def extract(self) -> dict[str, str]:
        """Scrape bank codes from ČNB website."""
        url = "https://www.czso.cz/csu/cz/bankovni-kody"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        banks: dict[str, str] = {}
        table = soup.find("table", class_="table")
        if table is None:
            table = soup.find("table")

        if table is None:
            raise ValueError(f"No table found at {url}")

        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) >= 2:
                code = cols[0].text.strip()
                name = cols[1].text.strip()
                if code and code.isdigit() and len(code) == 4:
                    banks[code] = name

        return banks

    def get_source_url(self) -> str:
        return "https://www.czso.cz/csu/cz/bankovni-kody"

    def get_license(self) -> str:
        return "Public domain"


if __name__ == "__main__":
    output = "src/fastpii/data/countries/cz/_data/bank_codes.py"
    extractor = CzechBankCodesExtractor()
    extractor.save(output)