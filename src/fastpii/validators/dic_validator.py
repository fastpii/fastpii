"""
Czech DIČ (Daňové identifikační číslo) Validator

Tax identification numbers for Czech Republic.
- Legal entities: CZ + 8-digit IČO
- Individuals: CZ + 9-10 digit birth number
"""

import re


def format_dic(value: str) -> str:
    """Normalize DIČ: trim whitespace, uppercase, remove spaces."""
    return re.sub(r'\s+', '', str(value).upper())


def parse_dic(value: str) -> tuple[str | None, str | None]:
    """
    Parse Czech DIČ into country code and number.
    
    :param value: DIČ to parse
    :return: Tuple of (country_code, number) or (None, None) on error
    """
    normalized = format_dic(value)
    
    if not normalized.startswith('CZ'):
        return None, None
    
    number = normalized[2:]
    
    if not number:
        return None, None
    
    return 'CZ', number


def is_valid_ico(value: str) -> bool:
    """Validate Czech IČO (for DIČ validation)."""
    value = re.sub(r'\s+', '', str(value))
    if not re.match(r'^\d{1,8}$', value):
        return False
    
    value = value.zfill(8)
    if len(value) != 8:
        return False
    
    digits = [int(d) for d in value[:7]]
    weights = [8, 7, 6, 5, 4, 3, 2]
    weighted_sum = sum(d * w for d, w in zip(digits, weights))
    modulo = weighted_sum % 11
    
    if modulo == 0:
        check = 1
    elif modulo == 1:
        check = 0
    else:
        check = 11 - modulo
    
    return int(value[7]) == check


def is_valid_birth_number(rc: str) -> bool:
    """Validate Czech birth number format (for DIČ validation)."""
    value = re.sub(r'\s+', '', rc)
    
    match = re.match(r'^(\d\d)(\d\d)(\d\d)/?(\d{3,4})$', value)
    if not match:
        return False
    
    year_part, month_part, day_part, extension = match.groups()
    _year = int(year_part)
    _month = int(month_part)
    _day = int(day_part)
    
    if len(extension) == 3:
        # 9-digit format (pre-1954), no checksum validation needed
        return True
    else:
        # 10-digit format (post-1954), requires checksum
        first_9_str = f"{year_part}{month_part}{day_part}{extension[:3]}"
        first_9 = int(first_9_str)
        mod = first_9 % 11
        
        expected_check = 0 if mod == 10 else mod
        return int(extension[3]) == expected_check


def is_valid_dic(value: str) -> bool:
    """
    Validate Czech DIČ (VAT ID).
    
    :param value: DIČ to validate
    :return: True if valid, False otherwise
    """
    country_code, number = parse_dic(value)
    if country_code is None:
        return False
    
    if not number:
        return False
    
    if not re.match(r'^\d{8,10}$', number):
        return False
    
    if len(number) == 8:
        return is_valid_ico(number)
    else:
        return is_valid_birth_number(number)


def validate_dic(value: str) -> tuple[bool, str]:
    """
    Validate Czech DIČ with detailed error information.
    
    :param value: DIČ to validate
    :return: Tuple of (is_valid, error_message)
    """
    if not value:
        return False, "Invalid input type"
    
    country_code, number = parse_dic(value)
    if country_code is None:
        return False, "Must start with 'CZ'"
    
    if not number:
        return False, "No number part after 'CZ'"
    
    if not re.match(r'^\d{8,10}$', number):
        return False, "Number part must be 8-10 digits"
    
    if len(number) == 8:
        if not is_valid_ico(number):
            return False, f"IČO: Invalid checksum"
    else:
        if not is_valid_birth_number(number):
            return False, "Birth number: Invalid format or checksum"
    
    return True, ""


if __name__ == "__main__":
    # Test cases - note: 9-digit birth numbers ARE valid for DIČ
    test_cases = [
        ("CZ25596641", True),      # Valid IČO
        ("CZ2559664", False),       # Invalid (7 digits)
        ("CZ25596640", False),      # Invalid checksum
        ("CZ7801233540", True),     # Valid birth number
        ("CZ780123354", True),      # Valid 9-digit birth number (for DIČ)
        ("CZ401224001", True),      # Valid pre-1954 birth number
        ("cZ25596641", True),       # Case insensitive
        ("CZ", False),               # No number
        ("US", False),               # Wrong country code
        ("abc", False),              # Invalid format
    ]
    
    print("Testing DIČ validators:")
    print("-" * 60)
    for value, expected in test_cases:
        result = is_valid_dic(value)
        status = "✓" if result == expected else "✗"
        print(f"{status} {value:20s} -> {result} (expected {expected})")
