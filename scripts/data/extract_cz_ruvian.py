#!/usr/bin/env python3
"""Extract Czech cities, postal codes, and streets from ČÚZK RÚIAN CSV data.

Downloads the latest RÚIAN address ZIP export, parses the semicolon-separated
CSV inside, and generates Python data modules for cities, postal codes, and
streets in a single pass.

Usage:
    python scripts/data/extract_cz_ruvian.py

Output:
    src/fastpii/countries/cz/data/_data/cities.py
    src/fastpii/countries/cz/data/_data/postal_codes.py
    src/fastpii/countries/cz/data/_data/streets.py
"""

import calendar
import csv
import io
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import IO

sys.path.insert(0, "src")

try:
    import requests
except ImportError:
    print("Error: requests is required.")
    print("Install with: pip install requests")
    sys.exit(1)

from fastpii.data.base import DataSource


def _get_ruvian_url() -> str:
    """Compute the latest RÚIAN CSV URL using the last day of the previous month."""
    today = datetime.now()

    if today.month == 1:
        prev_year = today.year - 1
        prev_month = 12
    else:
        prev_year = today.year
        prev_month = today.month - 1

    last_day = calendar.monthrange(prev_year, prev_month)[1]
    date_str = f"{prev_year}{prev_month:02d}{last_day:02d}"
    return f"https://vdp.cuzk.gov.cz/vymenny_format/csv/{date_str}_OB_ADR_csv.zip"


class CzechRuvianExtractor:
    """Extract Czech cities, postal codes, and streets from ČÚZK RÚIAN CSV."""

    country_code: str = "CZ"

    def __init__(self) -> None:
        self._cities: set[str] | None = None
        self._postal_codes: set[str] | None = None
        self._streets: set[str] | None = None

    def extract(self) -> tuple[set[str], set[str], set[str]]:
        """Download and parse RÚIAN CSV. Returns (cities, postal_codes, streets)."""
        if self._cities is not None and self._postal_codes is not None and self._streets is not None:
            return self._cities, self._postal_codes, self._streets

        url = _get_ruvian_url()
        cities: set[str] = set()
        postal_codes: set[str] = set()
        streets: set[str] = set()

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                zip_path = temp_path / "ruvian.zip"

                response = requests.get(url, timeout=300)
                response.raise_for_status()
                _ = zip_path.write_bytes(response.content)
                print(f"Downloaded ZIP from {url}")

                with zipfile.ZipFile(zip_path) as archive:
                    csv_names = sorted(
                        name for name in archive.namelist()
                        if name.lower().endswith(".csv")
                    )
                    if not csv_names:
                        print("Error: ZIP archive does not contain any CSV files.")
                        sys.exit(1)

                    total = len(csv_names)
                    print(f"Parsing {total} CSV files (this may take a few minutes)...")

                    for idx, csv_name in enumerate(csv_names, 1):
                        if idx % 50 == 0 or idx == total:
                            print(f"  Processing file {idx}/{total}...")

                        with archive.open(csv_name) as csv_file:
                            raw = csv_file.read()

                        # Try UTF-8 first (some files are UTF-8), fall back to windows-1250
                        try:
                            content = raw.decode("utf-8-sig")
                        except UnicodeDecodeError:
                            content = raw.decode("windows-1250")

                        reader = csv.reader(io.StringIO(content), delimiter=";")
                        _ = next(reader, None)

                        for row in reader:
                            if len(row) <= 15:
                                continue

                            city = row[2].strip().lower()
                            if city:
                                cities.add(city)

                            street = row[10].strip().lower()
                            if street:
                                streets.add(street)

                            postal_code = row[15].strip().replace(" ", "")
                            if postal_code.isdigit() and len(postal_code) == 5:
                                postal_codes.add(postal_code)

        except requests.RequestException as exc:
            print(f"Error: Failed to download RÚIAN ZIP: {exc}")
            sys.exit(1)
        except zipfile.BadZipFile as exc:
            print(f"Error: Invalid ZIP archive downloaded from RÚIAN: {exc}")
            sys.exit(1)
        except OSError as exc:
            print(f"Error: Failed to process RÚIAN data: {exc}")
            sys.exit(1)

        self._cities = cities
        self._postal_codes = postal_codes
        self._streets = streets

        print(
            f"Found {len(cities)} cities, {len(postal_codes)} postal codes, {len(streets)} streets"
        )

        if not cities:
            print("Warning: No cities were extracted.")
        if not postal_codes:
            print("Warning: No postal codes were extracted.")
        if not streets:
            print("Warning: No streets were extracted.")

        return cities, postal_codes, streets

    def get_source_url(self) -> str:
        return "https://vdp.cuzk.gov.cz/vymenny_format/csv/"

    def get_license(self) -> str:
        return "CC-BY 4.0"

    def save(self, cities_path: str, postal_codes_path: str, streets_path: str) -> None:
        """Extract and save all 3 data files."""
        cities, postal_codes, streets = self.extract()

        self._save_set_file(
            cities,
            cities_path,
            variable_name="CITIES",
            data_name="CZ Cities",
        )
        self._save_set_file(
            postal_codes,
            postal_codes_path,
            variable_name="POSTAL_CODES",
            data_name="CZ Postal Codes",
        )
        self._save_set_file(
            streets,
            streets_path,
            variable_name="STREETS",
            data_name="CZ Streets",
        )

    def _write_header(self, f: IO[str], source: DataSource) -> None:
        _ = f.write("# Auto-generated by FastPII data extractor\n")
        _ = f.write(f"# Country: {self.country_code}\n")
        _ = f.write(f"# Source: {source.url}\n")
        _ = f.write(f"# License: {source.license}\n")
        _ = f.write(f"# Extracted: {source.last_updated.isoformat()}\n")
        _ = f.write(f"# Entries: {source.entry_count}\n\n")

    def _save_set_file(
        self,
        entries: set[str],
        output_path: str,
        *,
        variable_name: str,
        data_name: str,
    ) -> None:
        source = DataSource(
            name=data_name,
            url=self.get_source_url(),
            license=self.get_license(),
            last_updated=datetime.now(),
            entry_count=len(entries),
        )

        with open(output_path, "w") as f:
            self._write_header(f, source)
            _ = f.write(f"{variable_name}: set[str] = {{\n")
            for entry in sorted(entries):
                entry_escaped = entry.replace('"', '\\"')
                _ = f.write(f'    "{entry_escaped}",\n')
            _ = f.write("}\n")

        print(f"Extracted {len(entries)} {variable_name.lower()} to {output_path}")


if __name__ == "__main__":
    cities_output = "src/fastpii/countries/cz/data/_data/cities.py"
    postal_codes_output = "src/fastpii/countries/cz/data/_data/postal_codes.py"
    streets_output = "src/fastpii/countries/cz/data/_data/streets.py"

    extractor = CzechRuvianExtractor()
    extractor.save(cities_output, postal_codes_output, streets_output)
