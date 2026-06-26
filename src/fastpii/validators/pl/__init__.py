"""Polish identifier validators.

PESEL: 11-digit national ID with Mod10 checksum
NIP: 10-digit tax ID with weighted Mod11 checksum
REGON: 9/14-digit business registry with weighted Mod11 checksum
"""

import re

PESEL_WEIGHTS = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
NIP_WEIGHTS = [6, 5, 7, 2, 3, 4, 5, 6, 7]
REGON9_WEIGHTS = [8, 9, 2, 3, 4, 5, 6, 7]
REGON14_WEIGHTS = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]

PESEL_CENTURY_MAP = {
    (0, 19): 1900, (20, 39): 2000, (40, 59): 2100,
    (60, 79): 2200, (80, 99): 1800,
}


def _pesel_decode_month(raw_month: int) -> tuple[int, int]:
    for (lo, hi), century in PESEL_CENTURY_MAP.items():
        if lo <= raw_month <= hi:
            return century, raw_month - lo
    return 1900, raw_month


def is_valid_pesel(value: str) -> bool:
    cleaned = re.sub(r"\s+", "", value)
    if not re.match(r"^\d{11}$", cleaned):
        return False

    total = sum(int(cleaned[i]) * PESEL_WEIGHTS[i] for i in range(10))
    remainder = total % 10
    expected = 0 if remainder == 0 else 10 - remainder
    return int(cleaned[10]) == expected


def validate_pesel(value: str) -> tuple[bool, str]:
    cleaned = re.sub(r"\s+", "", value)
    if not re.match(r"^\d{11}$", cleaned):
        return False, "PESEL must be 11 digits"
    if not is_valid_pesel(cleaned):
        return False, "Invalid checksum"
    return True, ""


def extract_pesel_metadata(value: str) -> dict[str, object]:
    cleaned = re.sub(r"\s+", "", value)
    metadata: dict[str, object] = {}

    try:
        year_raw = int(cleaned[0:2])
        month_raw = int(cleaned[2:4])
        day = int(cleaned[4:6])

        century, month = _pesel_decode_month(month_raw)
        year = century + year_raw

        metadata["birth_date"] = f"{year:04d}-{month:02d}-{day:02d}"
        metadata["gender"] = "female" if int(cleaned[9]) % 2 == 0 else "male"
        metadata["checksum_valid"] = is_valid_pesel(cleaned)
    except (ValueError, IndexError):
        pass

    return metadata


def is_valid_nip(value: str) -> bool:
    cleaned = re.sub(r"[\s-]", "", value)
    if not re.match(r"^\d{10}$", cleaned):
        return False

    total = sum(int(cleaned[i]) * NIP_WEIGHTS[i] for i in range(9))
    remainder = total % 11
    if remainder == 10:
        return False
    return int(cleaned[9]) == remainder


def validate_nip(value: str) -> tuple[bool, str]:
    cleaned = re.sub(r"[\s-]", "", value)
    if not re.match(r"^\d{10}$", cleaned):
        return False, "NIP must be 10 digits"
    if not is_valid_nip(cleaned):
        return False, "Invalid checksum"
    return True, ""


def is_valid_regon(value: str) -> bool:
    cleaned = re.sub(r"[\s-]", "", value)
    if len(cleaned) == 9:
        return _validate_regon9(cleaned)
    if len(cleaned) == 14:
        return _validate_regon9(cleaned[:9]) and _validate_regon14(cleaned)
    return False


def _validate_regon9(value: str) -> bool:
    if not value.isdigit() or len(value) != 9:
        return False
    total = sum(int(value[i]) * REGON9_WEIGHTS[i] for i in range(8))
    remainder = total % 11
    if remainder == 10:
        remainder = 0
    return int(value[8]) == remainder


def _validate_regon14(value: str) -> bool:
    total = sum(int(value[i]) * REGON14_WEIGHTS[i] for i in range(13))
    remainder = total % 11
    if remainder == 10:
        remainder = 0
    return int(value[13]) == remainder


def validate_regon(value: str) -> tuple[bool, str]:
    cleaned = re.sub(r"[\s-]", "", value)
    if len(cleaned) == 9:
        if not _validate_regon9(cleaned):
            return False, "Invalid 9-digit REGON checksum"
        return True, ""
    if len(cleaned) == 14:
        if not _validate_regon9(cleaned[:9]):
            return False, "Invalid REGON: first 9 digits checksum failed"
        if not _validate_regon14(cleaned):
            return False, "Invalid 14-digit REGON checksum"
        return True, ""
    return False, "REGON must be 9 or 14 digits"