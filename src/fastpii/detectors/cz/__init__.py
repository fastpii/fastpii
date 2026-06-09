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
]