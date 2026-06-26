import re


def _mod_11_10_check(digits: str, num_check_digits: int = 1) -> int:
    product = 10
    for i in range(len(digits) - num_check_digits):
        s = (int(digits[i]) + product) % 10
        if s == 0:
            s = 10
        product = (2 * s) % 11
    check = 11 - product
    if check == 10:
        check = 0
    return check


def is_valid_steuer_id(value: str) -> bool:
    cleaned = re.sub(r"\s+", "", value)
    if not re.match(r"^\d{11}$", cleaned):
        return False
    if cleaned[0] == "0":
        return False

    for i in range(1, 10):
        if cleaned[i] == cleaned[i - 1]:
            return False

    return _mod_11_10_check(cleaned) == int(cleaned[10])


def validate_steuer_id(value: str) -> tuple[bool, str]:
    cleaned = re.sub(r"\s+", "", value)
    if not re.match(r"^\d{11}$", cleaned):
        return False, "Steuer-ID must be 11 digits"
    if cleaned[0] == "0":
        return False, "Steuer-ID cannot start with 0"
    if not is_valid_steuer_id(cleaned):
        return False, "Invalid checksum"
    return True, ""


def extract_steuer_id_metadata(value: str) -> dict[str, object]:
    cleaned = re.sub(r"\s+", "", value)
    return {"checksum_valid": is_valid_steuer_id(cleaned)}


def is_valid_ust_id(value: str) -> bool:
    cleaned = value.strip().upper()
    if not re.match(r"^DE\d{9}$", cleaned):
        return False
    if cleaned[2] == "0":
        return False

    digits = cleaned[2:]
    return _mod_11_10_check(digits) == int(digits[8])


def validate_ust_id(value: str) -> tuple[bool, str]:
    cleaned = value.strip().upper()
    if not re.match(r"^DE\d{9}$", cleaned):
        return False, "USt-IdNr must be DE + 9 digits"
    if not is_valid_ust_id(cleaned):
        return False, "Invalid checksum"
    return True, ""


_HANDELSREGISTER_PATTERN = re.compile(
    r"^(?:(.+?)\s+)?(HRA|HRB|PR|GnR|VR)\s+([1-9]\d{0,5})(?:\s+([A-ZÄÖÜa-zäöü.&]+))?$"
)


def is_valid_handelsregister(value: str) -> bool:
    return bool(_HANDELSREGISTER_PATTERN.match(value.strip()))


def validate_handelsregister(value: str) -> tuple[bool, str]:
    match = _HANDELSREGISTER_PATTERN.match(value.strip())
    if not match:
        return False, "Invalid Handelsregister format"
    return True, ""


def parse_handelsregister(value: str) -> dict[str, str] | None:
    match = _HANDELSREGISTER_PATTERN.match(value.strip())
    if not match:
        return None
    court, reg_type, number, qualifier = match.groups()
    result: dict[str, str] = {"type": reg_type, "number": number}
    if court:
        result["court"] = court.strip()
    if qualifier:
        result["qualifier"] = qualifier.strip()
    return result