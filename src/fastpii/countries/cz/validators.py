"""
Czech IČO (Identifikační číslo osoby) Validator

Implementation of the MOD11 checksum algorithm for Czech business identification numbers.
"""

from collections.abc import Mapping
from datetime import datetime
import re
from typing import Final

from fastpii.countries.cz.data.bank_codes import CzechBankCodesData


# --- IČO Validator ---

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


def validate_ico(value: str) -> tuple[bool, str]:
    """
    Validate Czech IČO with detailed error information.
    
    :param value: IČO to validate
    :return: Tuple of (is_valid, error_message)
    """
    if not value:
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


# --- Bank Account Validator ---

# Pattern Constants (organized for maintainability)
# These are validation patterns used by validators (different from detection patterns in registry)
PREFIX_PATTERN: Final[str] = r'^\d{1,6}$'
BASE_PATTERN: Final[str] = r'^\d{1,10}$'
BANK_CODE_PATTERN: Final[str] = r'^\d{4}$'
FULL_ACCOUNT_WITH_PREFIX: Final[str] = r'^(\d{1,6})-(\d{2,10})/(\d{4})$'
FULL_ACCOUNT_WITHOUT_PREFIX: Final[str] = r'^(\d{2,10})/(\d{4})$'

# Pre-compile patterns for performance
_PREFIX_COMPILED = re.compile(PREFIX_PATTERN)
_BASE_COMPILED = re.compile(BASE_PATTERN)
_BANK_CODE_COMPILED = re.compile(BANK_CODE_PATTERN)
_FULL_WITH_PREFIX_COMPILED = re.compile(FULL_ACCOUNT_WITH_PREFIX)
_FULL_WITHOUT_PREFIX_COMPILED = re.compile(FULL_ACCOUNT_WITHOUT_PREFIX)


# Module-level cache for bank code lookups (avoids per-call instantiation)
_valid_bank_codes: dict[str, str] | None = None


def _get_valid_bank_codes() -> dict[str, str]:
    """Load and cache the Czech bank codes registry."""
    global _valid_bank_codes
    if _valid_bank_codes is None:
        _valid_bank_codes = CzechBankCodesData().get_data()
    return _valid_bank_codes


def is_valid_bank_code(bank_code: str) -> bool:
    """
    Validate that a bank code is 4 digits and exists in the Czech National Bank code list.

    :param bank_code: 4-digit bank code
    :return: True if the code is valid and exists, False otherwise
    """
    if not _BANK_CODE_COMPILED.match(bank_code):
        return False

    return bank_code in _get_valid_bank_codes()


def validate_bank_code(bank_code: str) -> tuple[bool, str]:
    """
    Validate a Czech bank code with detailed error information.

    :param bank_code: 4-digit bank code
    :return: Tuple of (is_valid, error_message)
    """
    if not _BANK_CODE_COMPILED.match(bank_code):
        return False, "Bank code must be exactly 4 digits"

    if not is_valid_bank_code(bank_code):
        return False, f"Bank code {bank_code} is not a valid Czech bank code"

    return True, ""


def validate_prefix_prefix(value: str) -> tuple[bool, str]:
    """
    Validate the prefix part (optional, up to 6 digits) with weights [10,5,8,4,2,1] from left.
    
    Algorithm:
    - Pad with leading zeros to 6 digits
    - Apply weights [10,5,8,4,2,1] left to right
    - Sum must be divisible by 11
    - Reject all-same-digit sequences (degenerate MOD11 pass)
    """
    if not value:
        return True, ""
    
    if not _PREFIX_COMPILED.match(value):
        return False, "Prefix must be 1-6 digits"
    
    if len(set(value)) == 1:
        return False, "Prefix cannot be all same digits"
    
    padded = value.zfill(6)
    digits = [int(d) for d in padded]
    weights = [10, 5, 8, 4, 2, 1]
    
    weighted_sum = sum(d * w for d, w in zip(digits, weights))
    
    if weighted_sum % 11 != 0:
        remainder = weighted_sum % 11
        return False, f"Prefix checksum failed: sum={weighted_sum}, remainder={remainder}"
    
    return True, ""


def validate_base_part(value: str) -> tuple[bool, str]:
    """
    Validate the base part (up to 10 digits) with weights [6,3,7,9,10,5,8,4,2,1] from left.
    
    Algorithm:
    - Pad with leading zeros to 10 digits
    - Apply weights [6,3,7,9,10,5,8,4,2,1] left to right
    - Sum must be divisible by 11
    - Reject all-same-digit sequences (degenerate MOD11 pass)
    """
    if not _BASE_COMPILED.match(value):
        return False, "Base part must be 1-10 digits"
    
    if len(set(value)) == 1:
        return False, "Base part cannot be all same digits"
    
    # Pad to 10 digits
    padded = value.zfill(10)
    digits = [int(d) for d in padded]
    weights = [6, 3, 7, 9, 10, 5, 8, 4, 2, 1]
    
    weighted_sum = sum(d * w for d, w in zip(digits, weights))
    
    if weighted_sum % 11 != 0:
        remainder = weighted_sum % 11
        return False, f"Base checksum failed: sum={weighted_sum}, remainder={remainder}"
    
    return True, ""


def parse_bank_account(value: str) -> tuple[str | None, str | None, str | None]:
    """
    Parse a Czech bank account number into its components.
    
    Format: [prefix]-base/bank_code
    
    :param value: Bank account number
    :return: Tuple of (prefix, base, bank_code) or (None, None, None) on parse error
    """
    match = _FULL_WITH_PREFIX_COMPILED.match(value)
    if match:
        prefix, base, bank_code = match.groups()
        return prefix or "", base, bank_code
    
    # Try without prefix
    match = _FULL_WITHOUT_PREFIX_COMPILED.match(value)
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
        valid, _error = validate_prefix_prefix(prefix)
        if not valid:
            return False
    
    # Validate base part
    if base is None or bank_code is None:
        return False

    valid, _error = validate_base_part(base)
    if not valid:
        return False
    
    if not is_valid_bank_code(bank_code):
        return False
    
    return True


def validate_bank_account(value: str) -> tuple[bool, str]:
    """
    Validate Czech bank account with detailed error information.
    
    :param value: Bank account number
    :return: Tuple of (is_valid, error_message)
    """
    if not value:
        return False, "Invalid input type"
    
    prefix, base, bank_code = parse_bank_account(value)
    if prefix is None:
        return False, "Invalid format. Expected [prefix-]base/bank_code"
    
    if prefix:
        valid, error = validate_prefix_prefix(prefix)
        if not valid:
            return False, f"Prefix: {error}"
    
    if base is None or bank_code is None:
        return False, "Invalid format. Expected [prefix-]base/bank_code"

    valid, error = validate_base_part(base)
    if not valid:
        return False, f"Base: {error}"
    
    valid, error = validate_bank_code(bank_code)
    if not valid:
        return False, error
    
    return True, ""


# --- Birth Number Validator ---

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


# --- DIČ Validator ---

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
