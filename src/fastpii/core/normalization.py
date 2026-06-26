import re


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", "", value)


def normalize_phone(phone: str) -> str:
    cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]
    return cleaned
