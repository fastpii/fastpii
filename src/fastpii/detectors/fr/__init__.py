from fastpii.detectors.fr.siren import SIRENDetector
from fastpii.detectors.fr.siret import SIRETDetector
from fastpii.detectors.fr.insee import INSEEDetector
from fastpii.detectors.fr.postal_code import FrenchPostalCodeDetector
from fastpii.detectors.fr.phone import FrenchPhoneDetector
from fastpii.detectors.fr.address import FrenchAddressDetector

__all__ = [
    "SIRENDetector",
    "SIRETDetector",
    "INSEEDetector",
    "FrenchPostalCodeDetector",
    "FrenchPhoneDetector",
    "FrenchAddressDetector",
]