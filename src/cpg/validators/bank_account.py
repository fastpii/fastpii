"""
Czech Bank Account Number Validator

Implementation of MOD11 checksum validation for Czech bank account numbers.
Each part (prefix and base) must pass its own MOD11 check.
"""

import re
from typing import Tuple, Optional


def validate_prefix_prefix(value: str) -> Tuple[bool, str]:
    """
    Validate the prefix part (optional, up to 6 digits) with weights [10,5,8,4,2,1] from left.
    
    Algorithm:
    - Pad with leading zeros to 6 digits
    - Apply weights [10,5,8,4,2,1] left to right
    - Sum must be divisible by 11
    """
    if not value:
        return True, ""  # Empty is valid (no prefix)
    
    if not re.match(r'^\d{1,6}$', value):
        return False, "Prefix must be 1-6 digits"
    
    # Pad to 6 digits
    padded = value.zfill(6)
    digits = [int(d) for d in padded]
    weights = [10, 5, 8, 4, 2, 1]
    
    weighted_sum = sum(d * w for d, w in zip(digits, weights))
    
    if weighted_sum % 11 != 0:
        remainder = weighted_sum % 11
        return False, f"Prefix checksum failed: sum={weighted_sum}, remainder={remainder}"
    
    return True, ""


def validate_base_part(value: str) -> Tuple[bool, str]:
    """
    Validate the base part (up to 10 digits) with weights [6,3,7,9,10,5,8,4,2,1] from left.
    
    Algorithm:
    - Pad with leading zeros to 10 digits
    - Apply weights [6,3,7,9,10,5,8,4,2,1] left to right
    - Sum must be divisible by 11
    """
    if not re.match(r'^\d{1,10}$', value):
        return False, "Base part must be 1-10 digits"
    
    # Pad to 10 digits
    padded = value.zfill(10)
    digits = [int(d) for d in padded]
    weights = [6, 3, 7, 9, 10, 5, 8, 4, 2, 1]
    
    weighted_sum = sum(d * w for d, w in zip(digits, weights))
    
    if weighted_sum % 11 != 0:
        remainder = weighted_sum % 11
        return False, f"Base checksum failed: sum={weighted_sum}, remainder={remainder}"
    
    return True, ""


def parse_bank_account(value: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse a Czech bank account number into its components.
    
    Format: [prefix]-base/bank_code
    
    :param value: Bank account number
    :return: Tuple of (prefix, base, bank_code) or (None, None, None) on parse error
    """
    match = re.match(r'^(\d{1,6})?-(\d{2,10})/(\d{4})$', value)
    if match:
        prefix, base, bank_code = match.groups()
        return prefix or "", base, bank_code
    
    # Try without prefix
    match = re.match(r'^(\d{2,10})/(\d{4})$', value)
    if match:
        base, bank_code = match.groups()
        return "", base, bank_code
    
    return None, None, None


def is_valid_bank_account(value: str) -> bool:
    """
    Validate a Czech bank account number.
    
    :param value: Bank account number
    :return: True if valid, False otherwise
    """
    prefix, base, bank_code = parse_bank_account(value)
    if prefix is None:
        return False  # Parse error
    
    # Validate prefix
    if prefix:
        valid, error = validate_prefix_prefix(prefix)
        if not valid:
            return False
    
    # Validate base part
    valid, error = validate_base_part(base)
    if not valid:
        return False
    
    # Bank code validation (not implemented - requires current CNB code list)
    # For format validation, we just check it exists
    if not re.match(r'^\d{4}$', bank_code):
        return False
    
    return True


def validate_bank_account(value: str) -> Tuple[bool, str]:
    """
    Validate Czech bank account with detailed error information.
    
    :param value: Bank account number
    :return: Tuple of (is_valid, error_message)
    """
    if not value or not isinstance(value, str):
        return False, "Invalid input type"
    
    prefix, base, bank_code = parse_bank_account(value)
    if prefix is None:
        return False, "Invalid format. Expected [prefix-]base/bank_code"
    
    if prefix:
        valid, error = validate_prefix_prefix(prefix)
        if not valid:
            return False, f"Prefix: {error}"
    
    valid, error = validate_base_part(base)
    if not valid:
        return False, f"Base: {error}"
    
    if not re.match(r'^\d{4}$', bank_code):
        return False, "Bank code must be exactly 4 digits"
    
    return True, ""


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("19-2000145399/0800", True),   # Valid (Česká spořitelna)
        ("1234567890/0100", True),      # Valid (Komerční banka)
        ("000000/0000", True),          # Minimal valid (dummy)
        ("19-19/0800", True),           # Minimal with prefix
        ("19-12/0800", False),          # Invalid prefix checksum
        ("19-123/0800", False),         # Invalid base checksum
        ("", False),                      # Empty
        ("abc", False),                   # Invalid format
        ("19-1234567890/0800", True),   # Max length valid
        ("19-1234567890/080", False),   # Invalid bank code
    ]
    
    print("Testing Bank Account validators:")
    print("-" * 60)
    for value, expected in test_cases:
        result = is_valid_bank_account(value)
        status = "✓" if result == expected else "✗"
        print(f"{status} {value:30s} -> {result} (expected {expected})")
