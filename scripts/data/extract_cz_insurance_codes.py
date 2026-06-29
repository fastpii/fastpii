#!/usr/bin/env python3
"""Extract Czech health insurance codes.

Czech health insurance company codes are hardcoded (only 7 exist)
as they don't change frequently and aren't available via a stable API.

Usage:
    python scripts/data/extract_cz_insurance_codes.py

Output:
    src/fastpii/data/countries/cz/insurance_codes.py
"""

import sys

sys.path.insert(0, "src")

from fastpii.data.extractors.bank_codes import BankCodesExtractor


CZECH_INSURANCE_CODES: dict[str, str] = {
    "111": "VZP (Všeobecná zdravotní pojišťovna)",
    "201": "ZP MVČR (Zdravotní pojišťovna Ministerstva vnitra ČR)",
    "205": "ČPZP (Česká průmyslová zdravotní pojišťovna)",
    "207": "OZP (Oborová zdravotní pojišťovna)",
    "209": "RBP (Rytířská zdravotní pojišťovna)",
    "211": "VoZP (Vojenská zdravotní pojišťovna)",
    "213": "ZPŠ (Zdravotní pojišťovna Škoda)",
}


class CzechInsuranceCodesExtractor(BankCodesExtractor):
    """Extract Czech health insurance codes (hardcoded).

    Inherits from BankCodesExtractor since insurance codes follow
    the same code→name dict pattern and output format.
    """

    country_code = "CZ"

    def extract(self) -> dict[str, str]:
        return CZECH_INSURANCE_CODES

    def get_source_url(self) -> str:
        return "https://www.mfcr.cz/"

    def get_license(self) -> str:
        return "Public domain"

    def _data_type(self) -> str:
        return "Insurance Codes"


if __name__ == "__main__":
    output = "src/fastpii/data/countries/cz/_insurance_codes.py"
    extractor = CzechInsuranceCodesExtractor()
    extractor.save(output, set_var="VALID_INSURANCE_CODES", dict_var="INSURANCE_NAMES", label="insurance codes")