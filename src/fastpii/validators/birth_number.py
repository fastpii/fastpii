"""
Czech Rodné číslo (Birth Number) Validator

Implementation of validation algorithm for Czech personal identification numbers.
Based on: phpFashion algorithm and CSSZ specifications
"""

import re
from collections.abc import Mapping
from datetime import datetime


def validate_birth_number_format(value: str) -> tuple[bool, str, Mapping[str, int | str | None] | None]:
    """
    Validate Czech birth number format and extract information.
    
    Format rules:
    - RRMMDD/XXX (9 digits, before 1954, no checksum validation)
    - RRMMDD/XXXX (10 digits, from 1954, with checksum validation)
    
    :param value: Birth number as string
    :return: Tuple of (is_valid, error_message, parsed_info)
    """
    if not value:
        return False, "Invalid input type", None
    
    value = re.sub(r'\s+', '', value)
    
    match = re.match(r'^(\d\d)(\d\d)(\d\d)/?(\d{3,4})$', value)
    if not match:
        return False, "Invalid format. Expected RRMMDD/XXX or RRMMDD/XXXX", None
    
    year_part, month_part, day_part, extension = match.groups()
    year = int(year_part)
    month = int(month_part)
    day = int(day_part)
    
    if len(extension) == 3:
        # 9-digit format (pre-1954), no checksum validation
        # 00-53: 1900-1953 (normal pre-1954)
        # 54-99: 1800-1899 (very old people, born before 1900)
        if year < 54:
            base_year = 1900
        else:
            base_year = 1800
        actual_year = year + base_year
        
        try:
            _ = datetime(actual_year, month, day)
        except ValueError:
            return False, f"Invalid date: {actual_year}-{month:02d}-{day:02d}", None
        
        parsed_info = {
            'birth_year': actual_year,
            'birth_month': month,
            'birth_day': day,
            'gender': 'male',  # Pre-1954 doesn't use gender modifiers
            'birth_order': int(extension[:3]),
            'checksum': None,
        }
    else:
        # 10-digit format (post-1954), requires checksum validation
        first_9_str = f"{year_part}{month_part}{day_part}{extension[:3]}"
        first_9 = int(first_9_str)
        mod = first_9 % 11
        
        expected_check = 0 if mod == 10 else mod
        actual_check = int(extension[3])
        
        if actual_check != expected_check:
            return False, f"Invalid checksum. Expected {expected_check}, got {actual_check}", None
        
        # Determine base year: 00-53 -> 2000-2053, 54-99 -> 1900-1999
        if year < 54:
            actual_year = year + 2000
        else:
            actual_year = year + 1900
        
        # Handle gender modifiers: +50 for females, additional +20/+40 for special cases
        if month > 70 and actual_year > 2003:
            month -= 70
        elif month > 50:
            month -= 50
        elif month > 20 and actual_year > 2003:
            month -= 20
        
        try:
            _ = datetime(actual_year, month, day)
        except ValueError:
            return False, f"Invalid date after gender adjustment: {actual_year}-{month:02d}-{day:02d}", None
        
        parsed_info = {
            'birth_year': actual_year,
            'birth_month': month,
            'birth_day': day,
            'gender': 'female',
            'birth_order': int(extension[:3]),
            'checksum': int(extension[3]),
        }
    
    return True, "", parsed_info


def is_valid_birth_number(value: str) -> bool:
    """
    Check if a Czech birth number is valid.
    
    :param value: Birth number to validate
    :return: True if valid, False otherwise
    """
    is_valid, _, _ = validate_birth_number_format(value)
    return is_valid


if __name__ == "__main__":
    # Use valid checksum-generated test cases
    valid_nums = [
        "990720/3119",   # 1999, valid checksum
        "200101/0000",   # 2020, valid checksum
        "780123/3540",   # 1978, valid checksum
        "401224/001",    # Pre-1954 (1940), no checksum
        "950101/123",    # Pre-1954 (1895), no checksum - very old person
        "0531135099",    # Special case: first 9 digits divisible by 11
        "0681186066",    # Special case: first 9 digits divisible by 11
        "780123/3541",   # Wrong checksum
        "9999999999",    # Invalid date
        "000000/000",    # Invalid date
        "abc",           # Invalid format
    ]
    
    print("Testing Birth Number validators:")
    print("-" * 60)
    for value in valid_nums:
        result = is_valid_birth_number(value)
        status = "✓" if result else "✗"
        print(f"{status} {value:20s} -> {result}")
