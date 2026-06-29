"""Synthetic PII generation script for expanding the Czech PII benchmark corpus.

Generates realistic Czech PII values with valid checksums for testing.
NOT for production use — these are test fixtures only.
"""

import json
import random
from pathlib import Path

CORPUS_DIR = Path(__file__).parent


def generate_rodne_cislo(year: int | None = None, month: int | None = None,
                         day: int | None = None, valid: bool = True) -> str:
    if year is None:
        year = random.randint(40, 99)
    if month is None:
        month = random.randint(1, 12)
    if day is None:
        day = random.randint(1, 28)

    month_code = month + 50 if random.random() < 0.5 and year >= 54 else month
    suffix = random.randint(100, 9999)

    rc = f"{year:02d}{month_code:02d}{day:02d}{suffix:04d}"
    if valid:
        remainder = int(rc) % 11
        if remainder != 0:
            last_digit = (10 - remainder) % 10
            rc = rc[:9] + str(last_digit)
    return f"{rc[:6]}/{rc[6:]}"


def generate_ico(valid: bool = True) -> str:
    first7 = random.randint(1000000, 9999999)
    if valid:
        weights = [8, 7, 6, 5, 4, 3, 2]
        digits = [int(d) for d in str(first7)]
        weighted_sum = sum(d * w for d, w in zip(digits, weights))
        remainder = weighted_sum % 11
        check = (11 - remainder) % 10
        return f"{first7}{check}"
    return str(first7) + str(random.randint(0, 9))


def generate_dic(valid: bool = True) -> str:
    return f"CZ{generate_ico(valid=valid)}"


def generate_bank_account() -> str:
    bank_codes = ["0800", "3030", "5500", "0100", "0600", "2010", "2600"]
    bank_code = random.choice(bank_codes)
    prefix = random.randint(0, 99)
    base = random.randint(100000, 9999999)
    return f"{prefix}-{base}/{bank_code}"


def generate_phone() -> str:
    prefixes = ["601", "602", "603", "604", "605", "606", "607",
                "702", "720", "721", "722", "723", "724", "725",
                "726", "727", "728", "729", "730", "731", "732",
                "733", "734", "735", "736", "737", "738", "739",
                "770", "771", "772", "773", "774", "775", "776", "777"]
    prefix = random.choice(prefixes)
    number = random.randint(100000, 999999)
    return f"+420 {prefix} {number // 1000:03d} {number % 1000:03d}"


def generate_email() -> str:
    first_names = ["jan", "petr", "martin", "tomáš", "josef", "pavel",
                   "marie", "jana", "eva", "anna", "lenka", "kateřina",
                   "petra", "monika", "helena", "markéta"]
    last_names = ["novak", "svoboda", "novotny", "dvorak", "cerny",
                  "prochazka", "kucera", "vesely", "horak", "nemec"]
    domains = ["email.cz", "seznam.cz", "centrum.cz", "gmail.com",
               "volny.cz", "post.cz", "atlas.cz"]
    return f"{random.choice(first_names)}.{random.choice(last_names)}@{random.choice(domains)}"


CZECH_CITIES = [
    "Praha", "Brno", "Ostrava", "Plzeň", "Liberec", "Olomouc",
    "České Budějovice", "Hradec Králové", "Ústí nad Labem", "Pardubice",
]

CZECH_STREETS = [
    "Václavské náměstí", "Wilsonova", "Národní", "Ostravská", "Hlavní",
    "Komenského", "Dlouhá třída", "Jiráskova", "Masarykova", "Lidická",
    "Československé armády", "Palackého", "Husova", "Tyršova", "Smetanova",
]

CZECH_POSTAL_CODES = [
    "11000", "12000", "13000", "15000", "16000", "17000",
    "60200", "60300", "70200", "70300", "30100", "46001",
    "77900", "53002", "37001", "50002",
]


def generate_address() -> str:
    street = random.choice(CZECH_STREETS)
    number = random.randint(1, 200)
    orientation = random.choice(["", f"/{random.randint(1, 50)}"])
    postal = random.choice(CZECH_POSTAL_CODES)
    city = random.choice(CZECH_CITIES)
    return f"{street} {number}{orientation}, {postal[:3]} {postal[3:]} {city}"


def generate_identity_card(new_format: bool = True) -> str:
    if new_format:
        first = random.randint(1, 9)
        rest = random.randint(0, 99999999)
        return f"{first}{rest:08d}"
    digits = random.randint(100000, 999999)
    letters = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return f"{digits}{letters}"


def generate_health_insurance() -> str:
    codes = ["111", "201", "205", "207", "209", "211", "213"]
    code = random.choice(codes)
    personal = random.randint(100000, 999999)
    if random.random() < 0.5:
        return f"{code}/{personal}"
    return f"{code}{personal}"


def generate_iban() -> str:
    bank_codes = ["0800", "3030", "5500", "0100", "0600"]
    bank_code = random.choice(bank_codes)
    prefix = f"{random.randint(0, 99):06d}"
    account = f"{random.randint(100000, 9999999999):010d}"
    bban = bank_code + prefix + account
    country_code = "CZ"
    check_input = bban + "1234" + country_code
    numeric = ""
    for char in check_input:
        if char.isdigit():
            numeric += char
        else:
            numeric += str(ord(char) - ord('A') + 10)
    remainder = int(numeric) % 97
    check_digits = 98 - remainder
    if check_digits < 10:
        check_str = f"0{check_digits}"
    else:
        check_str = str(check_digits)
    return f"{country_code}{check_str} {bank_code} {prefix[:4]} {prefix[4:]} {account[:4]} {account[4:]}"


def generate_credit_card(card_type: str = "visa") -> str:
    if card_type == "visa":
        prefixes = ["4"]
        length = 16
    elif card_type == "mastercard":
        prefixes = ["51", "52", "53", "54", "55"]
        length = 16
    elif card_type == "amex":
        prefixes = ["34", "37"]
        length = 15
    else:
        prefixes = ["4"]
        length = 16

    prefix = random.choice(prefixes)
    digits = prefix + "".join(str(random.randint(0, 9)) for _ in range(length - len(prefix) - 1))

    total = 0
    for i, d in enumerate(reversed(digits)):
        d = int(d)
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    check = (10 - total % 10) % 10
    return digits + str(check)


def generate_vehicle_plate() -> str:
    regions = ["1A", "2A", "3A", "4A", "5A", "6A", "7A", "8A", "9A",
               "1B", "2B", "3B", "4B", "5B", "6B", "7B", "8B", "9B",
               "1C", "2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C"]
    region = random.choice(regions)
    letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUV", k=2))
    numbers = f"{random.randint(1000, 9999)}"
    return f"{region}{letters} {numbers}"


def generate_postal_code() -> str:
    code = random.choice(CZECH_POSTAL_CODES)
    return f"{code[:3]} {code[3:]}"


def generate_date_of_birth() -> str:
    day = random.randint(1, 28)
    month = random.randint(1, 12)
    year = random.randint(1940, 2005)
    return f"{day:02d}.{month:02d}.{year}"


def generate_name() -> str:
    first_names = ["Jan", "Petr", "Martin", "Tomáš", "Josef", "Pavel",
                   "Marie", "Jana", "Eva", "Anna", "Lenka", "Kateřina",
                   "Petra", "Monika", "Helena", "Markéta"]
    last_names = ["Novák", "Svoboda", "Novotný", "Dvořák", "Černý",
                  "Procházka", "Kučera", "Veselý", "Horák", "Němec"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


GENERATORS = {
    "rodne_cislo": generate_rodne_cislo,
    "ico": generate_ico,
    "dic": generate_dic,
    "bank_account": generate_bank_account,
    "phone": generate_phone,
    "email": generate_email,
    "address": generate_address,
    "postal_code": generate_postal_code,
    "date_of_birth": generate_date_of_birth,
    "name": generate_name,
    "vehicle_plate": generate_vehicle_plate,
    "identity_card": generate_identity_card,
    "health_insurance": generate_health_insurance,
    "iban": generate_iban,
    "credit_card": generate_credit_card,
}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic Czech PII for benchmark corpus")
    parser.add_argument("--type", choices=list(GENERATORS.keys()), required=True, help="PII type to generate")
    parser.add_argument("--count", type=int, default=10, help="Number of values to generate")
    parser.add_argument("--valid", action="store_true", default=True, help="Generate valid PII (default)")
    parser.add_argument("--invalid", action="store_true", help="Generate invalid PII")
    args = parser.parse_args()

    generator = GENERATORS[args.type]
    for _ in range(args.count):
        if args.type in ("rodne_cislo", "ico", "dic"):
            print(generator(valid=not args.invalid))
        elif args.type == "credit_card":
            print(generator(card_type=random.choice(["visa", "mastercard", "amex"])))
        elif args.type == "identity_card":
            print(generator(new_format=random.random() < 0.7))
        else:
            print(generator())


if __name__ == "__main__":
    main()