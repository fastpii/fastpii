from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., object])

try:
    from typing_extensions import override
except ImportError:
    def override(method: F, /) -> F:
        return method

from fastpii.countries.cz.data.insurance_codes import CzechInsuranceCodesData
from fastpii.detectors.cz.health_insurance import HealthInsuranceDetector


class TestHealthInsuranceDetector:
    def test_detector_creation(self):
        detector = HealthInsuranceDetector()

        assert detector.name == "health_insurance"
        assert detector.region == "cz"
        assert "health insurance" in detector.description.lower()

    def test_detect_with_slash_format(self):
        detector = HealthInsuranceDetector()
        text = "Pojištění: 111/123456"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].type == "health_insurance"
        assert findings[0].value == "111/123456"
        assert findings[0].metadata["insurance_code"] == "111"

    def test_detect_with_context_words(self):
        detector = HealthInsuranceDetector()
        text = "Zdravotní pojišťovna: 111123456"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].metadata["insurance_code"] == "111"

    def test_detect_without_context(self):
        detector = HealthInsuranceDetector()
        text = "111123456"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].confidence == 0.70

    def test_detect_all_7_insurance_codes_slash(self):
        detector = HealthInsuranceDetector()
        codes = ["111", "201", "205", "207", "209", "211", "213"]

        for code in codes:
            text = f"číslo pojištěnce: {code}/123456"
            findings = detector.detect(text)
            assert len(findings) >= 1, f"Failed for code {code}"
            assert findings[0].metadata["insurance_code"] == code

    def test_detect_all_7_insurance_codes_plain(self):
        detector = HealthInsuranceDetector()
        codes = ["111", "201", "205", "207", "209", "211", "213"]

        for code in codes:
            text = f"pojištění {code}123456"
            findings = detector.detect(text)
            assert len(findings) >= 1, f"Failed for code {code}"
            assert findings[0].metadata["insurance_code"] == code

    def test_metadata_includes_company_name(self):
        detector = HealthInsuranceDetector()
        text = "Pojištění: 111/123456"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert "company_name" in findings[0].metadata
        assert "VZP" in findings[0].metadata["company_name"]

    def test_metadata_includes_personal_number(self):
        detector = HealthInsuranceDetector()
        text = "Pojištění: 111/123456"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].metadata["personal_number"] == "123456"

    def test_rejects_invalid_insurance_code(self):
        detector = HealthInsuranceDetector()
        text = "pojištění: 999123456"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_rejects_non_insurance_numbers(self):
        detector = HealthInsuranceDetector()
        text = "Phone: 602123456"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_validate_valid_number(self):
        detector = HealthInsuranceDetector()

        assert detector.validate("111123456") is True
        assert detector.validate("201123456") is True

    def test_validate_valid_slash_format(self):
        detector = HealthInsuranceDetector()

        assert detector.validate("111/123456") is True

    def test_validate_invalid_code(self):
        detector = HealthInsuranceDetector()

        assert detector.validate("999123456") is False

    def test_validate_invalid_format(self):
        detector = HealthInsuranceDetector()

        assert detector.validate("abc") is False
        assert detector.validate("") is False
        assert detector.validate("12345") is False

    def test_no_detection_in_clean_text(self):
        detector = HealthInsuranceDetector()
        text = "No insurance numbers here"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_context_confidence(self):
        detector = HealthInsuranceDetector()
        text_with_context = "pojištění 111123456"
        text_without_context = "111123456"

        findings_with = detector.detect(text_with_context)
        findings_without = detector.detect(text_without_context)

        assert len(findings_with) >= 1
        assert len(findings_without) >= 1
        assert findings_with[0].confidence > findings_without[0].confidence

    def test_di_override(self):
        class EmptyInsuranceData(CzechInsuranceCodesData):
            @override
            def get_data(self) -> dict[str, str]:
                return {}

        detector = HealthInsuranceDetector(insurance_data=EmptyInsuranceData())
        text = "pojištění: 111/123456"

        findings = detector.detect(text)

        assert len(findings) == 0