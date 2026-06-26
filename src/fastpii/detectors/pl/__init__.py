from fastpii.detectors.pl.pesel import PeseleDetector
from fastpii.detectors.pl.nip import NIPDetector
from fastpii.detectors.pl.regon import REGONDetector
from fastpii.detectors.pl.postal_code import PolishPostalCodeDetector
from fastpii.detectors.pl.phone import PolishPhoneDetector
from fastpii.detectors.pl.address import PolishAddressDetector

__all__ = [
    "PeseleDetector",
    "NIPDetector",
    "REGONDetector",
    "PolishPostalCodeDetector",
    "PolishPhoneDetector",
    "PolishAddressDetector",
]