def weighted_mod11(value: str, weights: list[int]) -> int:
    digits = [int(d) for d in value[:len(weights)]]
    total = sum(d * w for d, w in zip(digits, weights))
    return total % 11


def luhn_checksum(value: str) -> int:
    digits = [int(d) for d in value]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    return total % 10


def validate_luhn(value: str) -> bool:
    return luhn_checksum(value) == 0
