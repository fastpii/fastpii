#!/usr/bin/env python3
"""Extract Czech names from CZSO (Czech Statistical Office).

Downloads first name frequency data from CZSO and extracts
male and female names. Uses a fallback to hardcoded data
if the download fails.

Usage:
    python scripts/data/extract_cz_names.py

Output:
    src/fastpii/data/countries/cz/names_male.py
    src/fastpii/data/countries/cz/names_female.py
"""

import csv
import io
import sys

sys.path.insert(0, "src")

from fastpii.data.extractors.names import NamesExtractor

# Fallback data used when CZSO is unreachable.
# Sourced from Czech Statistical Office and common naming patterns.
FALLBACK_MALE_NAMES: set[str] = {
    "adam", "aleš", "alexandr", "alois", "antonín",
    "bedřich", "bohumil", "bohuslav", "bronislav",
    "dalibor", "daniel", "david", "denis", "dušan",
    "eduard", "emil", "erik",
    "felix", "filip", "františek",
    "gabriel", "gustav",
    "hanuš", "heřman", "hynek",
    "ivan", "ivo",
    "jakub", "jan", "jaromír", "jaroslav", "jindřich",
    "jiří", "jozef",
    "karel", "kevin", "kristián",
    "ladislav", "leoš", "libor", "luboš", "lukáš", "lubomír",
    "marek", "martin", "matěj", "matyáš", "michal", "milan",
    "miloslav", "miroslav", "mojmír",
    "nikoláš", "norbert",
    "oldřich", "otakar", "oto",
    "patrik", "pavel", "petr", "prokop",
    "radim", "radomír", "radek", "rené", "richard", "robert",
    "roman", "rostislav", "rudolf",
    "simon", "stanislav", "štěpán", "svatopluk",
    "tadeáš", "tomáš",
    "urban", "uřich",
    "václav", "vladimír", "vlastimil", "vojtěch", "vítězslav",
    "zbyněk", "zdeněk",
}

FALLBACK_FEMALE_NAMES: set[str] = {
    "ada", "adéla", "alžběta", "alice", "amálie", "andrea", "anna",
    "barbora", "blanka", "božena", "brigit",
    "dagmar", "daniela", "denisa", "diana", "dominička",
    "eva", "emilie",
    "františka",
    "gabriela",
    "hana", "hedvika", "helena",
    "ilona", "ivana",
    "jana", "jitka", "josefa", "judita", "jindřiška",
    "kateřina", "klára", "kristýna",
    "lena", "lenka", "libuše", "lidmila", "lucie", "ludmila",
    "magdaléna", "marcela", "markéta", "martina", "marie", "monika",
    "naděžda", "natalie", "nika",
    "olga",
    "pavla", "pavlína", "petra",
    "radka", "renáta", "romana", "rozálie",
    "sára", "simona", "soňa", "stanislava", "štěpánka", "světla",
    "tereza", "týna",
    "vendula", "veronika", "vlasta",
    "zdenka", "zuzana",
}

CZSO_MALE_URL = (
    "https://www.czso.cz/documents/10180/177758690/jmena_muzi.csv"
)

CZSO_FEMALE_URL = (
    "https://www.czso.cz/documents/10180/177758690/jmena_zeny.csv"
)

MIN_FREQUENCY = 50


class CzechNamesExtractor(NamesExtractor):
    """Extract Czech names from CZSO with fallback to hardcoded data."""

    country_code = "CZ"

    def __init__(self, min_frequency: int = MIN_FREQUENCY) -> None:
        self.min_frequency = min_frequency
        self._names: dict[str, set[str]] | None = None

    def extract(self) -> dict[str, set[str]]:
        if self._names is not None:
            return self._names

        male_names = self._download_names(CZSO_MALE_URL, FALLBACK_MALE_NAMES)
        female_names = self._download_names(CZSO_FEMALE_URL, FALLBACK_FEMALE_NAMES)

        self._names = {"male": male_names, "female": female_names}
        return self._names

    def _download_names(self, url: str, fallback: set[str]) -> set[str]:
        """Download and parse CZSO name CSV. Falls back to hardcoded data on failure."""
        try:
            import requests

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            names: set[str] = set()
            reader = csv.reader(io.StringIO(response.text), delimiter=";")

            for row in reader:
                if len(row) < 3:
                    continue
                name = row[0].strip().lower()
                try:
                    frequency = int(row[2].strip().replace(" ", "").replace("\u00a0", ""))
                except (ValueError, IndexError):
                    continue
                if frequency >= self.min_frequency and name.isalpha():
                    names.add(name)

            if names:
                print(f"  Downloaded {len(names)} names from CZSO")
                return names

            print(f"  Warning: CZSO returned empty data, using fallback ({len(fallback)} names)")
            return fallback

        except Exception as e:
            print(f"  Warning: Failed to download from CZSO ({e}), using fallback ({len(fallback)} names)")
            return fallback

    def get_source_url(self) -> str:
        return "https://www.czso.cz/csu/cz/aha/jmena_rodne"

    def get_license(self) -> str:
        return "Public domain"


if __name__ == "__main__":
    male_output = "src/fastpii/data/countries/cz/_data/names_male.py"
    female_output = "src/fastpii/data/countries/cz/_data/names_female.py"
    extractor = CzechNamesExtractor()
    extractor.save(male_output, female_output)