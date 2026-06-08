"""
Czech IČO (Identifikační číslo osoby) Validator

Implementation of the MOD11 checksum algorithm for Czech business identification numbers.
"""

import re
from typing import Tuple


def calculate_ico_checksum(number: int) -> int:
    """
    Calculate the check digit for a 7-digit IČO number.
    
    Algorithm (MOD11 ADDO):
    1. Multiply first 7 digits by weights [8, 7, 6, 5, 4, 3, 2] from left to right
    2. Sum the products
    3. Calculate modulo 11
    4. Map result to check digit:
       - 0 → 1
       - 1 → 0
       - 2-10 → 11 - remainder
    
    :param number: 7-digit base number
    :return: Check digit (0-9)
    """
    digits = [int(d) for d in f"{number:07d}"]
    weights = [8, 7, 6, 5, 4, 3, 2]
    
    weighted_sum = sum(d * w for d, w in zip(digits, weights))
    modulo = weighted_sum % 11
    
    if modulo == 0:
        return 1
    elif modulo == 1:
        return 0
    else:
        return 11 - modulo


def is_valid_ico(value: str) -> bool:
    """
    Validate a Czech IČO (business ID).
    
    :param value: IČO as string (8 digits, may have leading zeros or be shorter)
    :return: True if valid, False otherwise
    """
    if not value:
        return False
    
    # Clean and normalize input
    value = re.sub(r'\s+', '', str(value))
    
    # Check format (must be 8 digits after padding)
    if not re.match(r'^\d{1,8}$', value):
        return False
    
    # Pad to 8 digits
    value = value.zfill(8)
    
    # Extract parts
    number = int(value[:7])
    check_digit = int(value[7])
    
    # Calculate expected check digit
    expected_check = calculate_ico_checksum(number)
    
    return check_digit == expected_check


def validate_ico(value: str) -> Tuple[bool, str]:
    """
    Validate Czech IČO with detailed error information.
    
    :param value: IČO to validate
    :return: Tuple of (is_valid, error_message)
    """
    if not value or not isinstance(value, str):
        return False, "Invalid input type"
    
    value = re.sub(r'\s+', '', value)
    
    if not re.match(r'^\d+$', value):
        return False, "Must contain only digits"
    
    if len(value) > 8:
        return False, "IČO must be at most 8 digits"
    
    # Pad to 8 digits for processing
    padded = value.zfill(8)
    number = int(padded[:7])
    check_digit = int(padded[7])
    expected_check = calculate_ico_checksum(number)
    
    if check_digit != expected_check:
        return False, f"Invalid check digit. Expected {expected_check}, got {check_digit}"
    
    return True, ""


if __name__ == "__main__":
    # Test cases from official sources
    test_cases = [
        ("25596641", True),  # Known valid IČO (David Grudl's test case)
        ("02559664", False),  # Wrong check digit
        ("12345678", False),  # Invalid checksum
        ("69663963", True),  # Another valid IČO
        ("00000001", False),  # Invalid
        ("00000000", False),  # Invalid
        ("10000000", False),  # Invalid
        ("80000005", False),  # Invalid
        ("72343976", False),  # Invalid (from MFCR - has MOD11 issue)
        ("2559664", True),   # 7-digit version
        ("", False),          # Empty
        ("abc", False),       # Non-numeric
    ]
    
    print("Testing IČO validators:")
    print("-" * 50)
    for value, expected in test_cases:
        result = is_valid_ico(value)
        status = "✓" if result == expected else "✗"
        print(f"{status} {value:10s} -> {result} (expected {expected})")
