"""Czech PII detectors."""

from fastpii.detectors.cz.rodne_cislo import RodneCisloDetector
from fastpii.detectors.cz.ico import ICODetector
from fastpii.detectors.cz.dic import DICDetector
from fastpii.detectors.cz.bank_account import BankAccountDetector
from fastpii.detectors.cz.postal_code import PostalCodeDetector
from fastpii.detectors.cz.phone import PhoneNumberDetector
from fastpii.detectors.cz.email import EmailDetector
from fastpii.detectors.cz.name import NameDetector
from fastpii.detectors.cz.address import AddressDetector
from fastpii.detectors.cz.date_of_birth import DateOfBirthDetector
from fastpii.detectors.cz.vehicle_plate import VehiclePlateDetector
from fastpii.detectors.cz.health_insurance import HealthInsuranceDetector
from fastpii.detectors.cz.iban import IBANDetector
from fastpii.detectors.cz.credit_card import CreditCardDetector
from fastpii.detectors.cz.identity_card import IdentityCardDetector

__all__ = [
    "RodneCisloDetector",
    "ICODetector",
    "DICDetector",
    "BankAccountDetector",
    "PostalCodeDetector",
    "PhoneNumberDetector",
    "EmailDetector",
    "NameDetector",
    "AddressDetector",
    "DateOfBirthDetector",
    "VehiclePlateDetector",
    "HealthInsuranceDetector",
    "IBANDetector",
    "CreditCardDetector",
    "IdentityCardDetector",
]