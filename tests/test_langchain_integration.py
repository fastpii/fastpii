import pytest

from fastpii import FastPII, DEFAULT_PRIORITY, DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.cz import CzechPack
from fastpii.integrations.langchain import PIIAnonymizer, PIIPreprocessor


@pytest.fixture
def engine():
    scorer = ConfidenceScorer(
        base_scores=DEFAULT_CONFIDENCE_SCORES,
        context_boost=DEFAULT_CONTEXT_BOOST,
    )
    eng = FastPII(priority=DEFAULT_PRIORITY, confidence_scorer=scorer)
    eng.register(CzechPack())
    return eng


class TestPIIAnonymizerWithEngine:
    def test_anonymize_rodne_cislo(self, engine):
        anonymizer = PIIAnonymizer(engine=engine)

        text = "Jan Novák, RČ: 8001011238"
        anonymized = anonymizer.anonymize(text)

        assert "8001011238" not in anonymized
        assert "[REDACTED]" in anonymized

    def test_anonymize_multiple_identifiers(self, engine):
        anonymizer = PIIAnonymizer(engine=engine)

        text = "IČO: 25596641, RČ: 8001011238, Tel: 777 123 456"
        anonymized = anonymizer.anonymize(text)

        assert "25596641" not in anonymized
        assert "8001011238" not in anonymized
        assert "777 123 456" not in anonymized

    def test_anonymize_custom_replacement(self, engine):
        anonymizer = PIIAnonymizer(engine=engine)

        text = "IČO: 25596641"
        anonymized = anonymizer.anonymize(text, replacement="[PII]")

        assert "[PII]" in anonymized
        assert "25596641" not in anonymized

    def test_anonymize_callable(self, engine):
        anonymizer = PIIAnonymizer(engine=engine)

        text = "RČ: 8001011238"
        result = anonymizer(text)

        assert "8001011238" not in result
        assert "[REDACTED]" in result

    def test_anonymize_no_pii(self, engine):
        anonymizer = PIIAnonymizer(engine=engine)

        text = "Hello world, no PII here"
        anonymized = anonymizer.anonymize(text)

        assert anonymized == text

    def test_anonymize_all_czech_detectors(self, engine):
        anonymizer = PIIAnonymizer(engine=engine)

        text = """
        RČ: 8001011238
        IČO: 25596641
        DIČ: CZ25596641
        Účet: 19-2000145399/0800
        PSČ: 110 00
        Tel: 777 123 456
        """

        anonymized = anonymizer.anonymize(text)

        assert "8001011238" not in anonymized
        assert "25596641" not in anonymized
        assert "CZ25596641" not in anonymized
        assert "2000145399" not in anonymized
        assert "110 00" not in anonymized
        assert "777 123 456" not in anonymized


class TestPIIPreprocessorWithEngine:
    def test_redact_action(self, engine):
        preprocessor = PIIPreprocessor(engine=engine)

        text = "Jan Novák, RČ: 8001011238"
        processed = preprocessor.preprocess(text, action="redact")

        assert "8001011238" not in processed
        assert "[RODNE_CISLO]" in processed

    def test_mask_action(self, engine):
        preprocessor = PIIPreprocessor(engine=engine)

        text = "IČO: 25596641"
        processed = preprocessor.preprocess(text, action="mask")

        assert "25596641" not in processed
        assert "********" in processed

    def test_remove_action(self, engine):
        preprocessor = PIIPreprocessor(engine=engine)

        text = "Jan Novák, RČ: 8001011238"
        processed = preprocessor.preprocess(text, action="remove")

        assert "8001011238" not in processed
        assert "[REDACTED]" not in processed

    def test_callable(self, engine):
        preprocessor = PIIPreprocessor(engine=engine)

        text = "IČO: 25596641"
        result = preprocessor(text)

        assert "25596641" not in result
        assert "[ICO]" in result

    def test_invalid_action(self, engine):
        preprocessor = PIIPreprocessor(engine=engine)

        with pytest.raises(ValueError, match="Invalid action"):
            preprocessor.preprocess("test", action="invalid")

    def test_preserves_structure(self, engine):
        preprocessor = PIIPreprocessor(engine=engine)

        text = "Name: Jan, IČO: 25596641, City: Prague"
        processed = preprocessor.preprocess(text, action="redact")

        assert "Name:" in processed
        assert "City:" in processed
        assert "25596641" not in processed

    def test_pipe_operator(self, engine):
        preprocessor = PIIPreprocessor(engine=engine)

        text = "RČ: 8001011238"
        processed = preprocessor.preprocess(text, action="redact")

        assert isinstance(processed, str)
        assert "[RODNE_CISLO]" in processed


class TestPIIAnonymizerFromRegions:
    def test_from_regions(self):
        anonymizer = PIIAnonymizer(regions=["cz"])

        text = "RČ: 8001011238"
        anonymized = anonymizer.anonymize(text)

        assert "8001011238" not in anonymized
        assert "[REDACTED]" in anonymized

    def test_no_engine_no_regions_raises(self):
        with pytest.raises(ValueError, match="Either engine or regions"):
            PIIAnonymizer()


class TestPIIPreprocessorFromRegions:
    def test_from_regions(self):
        preprocessor = PIIPreprocessor(regions=["cz"])

        text = "RČ: 8001011238"
        processed = preprocessor.preprocess(text, action="redact")

        assert "8001011238" not in processed

    def test_no_engine_no_regions_raises(self):
        with pytest.raises(ValueError, match="Either engine or regions"):
            PIIPreprocessor()