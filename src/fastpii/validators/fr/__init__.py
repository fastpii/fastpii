import re

from fastpii.core.checksum import validate_luhn


def is_valid_siren(value: str) -> bool:
    cleaned = re.sub(r"[\s-]", "", value)
    if not re.match(r"^\d{9}$", cleaned):
        return False
    return validate_luhn(cleaned)


def validate_siren(value: str) -> tuple[bool, str]:
    cleaned = re.sub(r"[\s-]", "", value)
    if not re.match(r"^\d{9}$", cleaned):
        return False, "SIREN must be 9 digits"
    if not validate_luhn(cleaned):
        return False, "Invalid Luhn checksum"
    return True, ""


def is_valid_siret(value: str) -> bool:
    cleaned = re.sub(r"[\s-]", "", value)
    if not re.match(r"^\d{14}$", cleaned):
        return False
    if not is_valid_siren(cleaned[:9]):
        return False
    return validate_luhn(cleaned)


def validate_siret(value: str) -> tuple[bool, str]:
    cleaned = re.sub(r"[\s-]", "", value)
    if not re.match(r"^\d{14}$", cleaned):
        return False, "SIRET must be 14 digits"
    if not is_valid_siren(cleaned[:9]):
        return False, "Invalid SIREN component (first 9 digits)"
    if not validate_luhn(cleaned):
        return False, "Invalid Luhn checksum"
    return True, ""


def _replace_corsica(value: str) -> str:
    return value.upper().replace("2A", "19").replace("2B", "18")


def is_valid_insee(value: str) -> bool:
    cleaned = re.sub(r"[\s-]", "", value).upper()
    if not re.match(r"^[12]\d{2}(0[1-9]|1[0-2])(\d{2}|2[AB])\d{8}$", cleaned):
        return False

    numeric_part = cleaned[:13]
    numeric_for_check = _replace_corsica(numeric_part)

    provided_key = int(cleaned[13:15])
    expected_key = 97 - (int(numeric_for_check) % 97)
    return provided_key == expected_key


def validate_insee(value: str) -> tuple[bool, str]:
    cleaned = re.sub(r"[\s-]", "", value).upper()
    if not re.match(r"^[12]\d{2}(0[1-9]|1[0-2])(\d{2}|2[AB])\d{8}$", cleaned):
        return False, "INSEE format: SYYMMDeptCommRegNN + 2-digit key"
    if not is_valid_insee(cleaned):
        return False, "Invalid control key"
    return True, ""


def extract_insee_metadata(value: str) -> dict[str, object]:
    cleaned = re.sub(r"[\s-]", "", value).upper()
    metadata: dict[str, object] = {}

    try:
        sex_digit = cleaned[0]
        metadata["sex"] = "male" if sex_digit == "1" else "female"

        year = int(cleaned[1:3])
        metadata["birth_year"] = year

        dept = cleaned[5:7]
        if dept == "2A":
            metadata["department"] = "Corse-du-Sud"
        elif dept == "2B":
            metadata["department"] = "Haute-Corse"
        else:
            metadata["department"] = dept

        metadata["checksum_valid"] = is_valid_insee(cleaned)
    except (ValueError, IndexError):
        pass

    return metadata