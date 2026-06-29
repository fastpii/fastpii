from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., object])

try:
    from typing_extensions import override
except ImportError:
    def override(method: F, /) -> F:
        return method

from fastpii.countries.cz.data.bank_codes import CzechBankCodesData
from fastpii.detectors.cz.bank_account import BankAccountDetector


class TestBankAccountDetector:
    def test_detector_creation(self):
        detector = BankAccountDetector()

        assert detector.name == "bank_account"
        assert detector.region == "cz"
        assert "Czech bank account" in detector.description

    def test_detect_bank_account_with_bank_code(self):
        detector = BankAccountDetector()
        text = "Číslo účtu: 19-2000145399/0800"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].type == "bank_account"
        assert "19-2000145399" in findings[0].value
        assert findings[0].region == "cz"

    def test_detect_bank_account_without_prefix(self):
        detector = BankAccountDetector()
        text = "Account: 2000145399/0800"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert "2000145399" in findings[0].value

    def test_detect_bank_account_simple(self):
        detector = BankAccountDetector()
        text = "Účet: 1003/0800"

        findings = detector.detect(text)

        assert len(findings) >= 1

    def test_validate_valid_bank_account(self):
        detector = BankAccountDetector()

        valid = detector.validate("19-2000145399/0800")

        assert valid is True

    def test_validate_valid_without_prefix(self):
        detector = BankAccountDetector()

        valid = detector.validate("2000145399/0800")

        assert valid is True

    def test_validate_invalid_checksum(self):
        detector = BankAccountDetector()

        valid = detector.validate("19-12/0800")

        assert valid is False

    def test_validate_invalid_format(self):
        detector = BankAccountDetector()

        valid = detector.validate("invalid-account")

        assert valid is False

    def test_validate_rejects_invalid_bank_code(self):
        detector = BankAccountDetector()

        valid = detector.validate("19-2000145399/9999")

        assert valid is False

    def test_validate_rejects_nonexistent_bank_code(self):
        detector = BankAccountDetector()

        valid = detector.validate("2000145399/1234")

        assert valid is False

    def test_detect_multiple_accounts_in_text(self):
        detector = BankAccountDetector()
        text = "First: 19-2000145399/0800, Second: 1003/0100"

        findings = detector.detect(text)

        assert len(findings) >= 2

    def test_no_detection_in_clean_text(self):
        detector = BankAccountDetector()
        text = "No bank accounts here"

        findings = detector.detect(text)

        assert len(findings) == 0

    def test_extracts_metadata(self):
        detector = BankAccountDetector()
        text = "Účet: 19-2000145399/0800"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert "bank_code" in findings[0].metadata
        assert findings[0].metadata["bank_code"] == "0800"

    def test_metadata_includes_bank_name(self):
        detector = BankAccountDetector()
        text = "Účet: 19-2000145399/0800"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].metadata["bank_name"] == "Česká spořitelna, a.s."

    def test_metadata_missing_bank_name_for_unknown_code(self):
        class PartialBankCodesData(CzechBankCodesData):
            @override
            def get_data(self) -> dict[str, str]:
                return {}

        detector = BankAccountDetector(bank_codes_data=PartialBankCodesData())
        text = "Účet: 19-2000145399/0800"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].metadata["bank_name"] == ""

    def test_detects_standalone_account_detection(self):
        detector = BankAccountDetector()
        text = "2000145399/0800"

        findings = detector.detect(text)

        assert len(findings) >= 1
        assert findings[0].value == "2000145399/0800"

    def test_handles_different_separators(self):
        detector = BankAccountDetector()
        text = "Account: 19-2000145399/0800 and 2000145399/0800"

        findings = detector.detect(text)

        assert len(findings) >= 2
