import pytest

from fastpii.integrations.langchain import PIIAnonymizer, PIIPreprocessor


class TestLangChainIntegration:
    def test_pii_anonymizer_rodne_cislo(self):
        anonymizer = PIIAnonymizer(regions=["cz"])
        
        text = "Jan Novák, RČ: 8001011234"
        anonymized = anonymizer.anonymize(text)
        
        assert "8001011234" not in anonymized
        assert "[REDACTED]" in anonymized
        assert "Jan Novák" in anonymized

    def test_pii_anonymizer_multiple_identifiers(self):
        anonymizer = PIIAnonymizer(regions=["cz"])
        
        text = "IČO: 25596641, RČ: 8001011234, Tel: 777 123 456"
        anonymized = anonymizer.anonymize(text)
        
        assert "25596641" not in anonymized
        assert "8001011234" not in anonymized
        assert "777 123 456" not in anonymized

    def test_pii_anonymizer_custom_replacement(self):
        anonymizer = PIIAnonymizer(regions=["cz"])
        
        text = "IČO: 25596641"
        anonymized = anonymizer.anonymize(text, replacement="[PII]")
        
        assert "[PII]" in anonymized
        assert "25596641" not in anonymized

    def test_pii_anonymizer_callable(self):
        anonymizer = PIIAnonymizer(regions=["cz"])
        
        text = "RČ: 8001011234"
        result = anonymizer(text)
        
        assert "8001011234" not in result
        assert "[REDACTED]" in result

    def test_pii_preprocessor_redact_action(self):
        preprocessor = PIIPreprocessor(regions=["cz"])
        
        text = "Jan Novák, RČ: 8001011234"
        processed = preprocessor.preprocess(text, action="redact")
        
        assert "8001011234" not in processed
        assert "[RODNE_CISLO]" in processed

    def test_pii_preprocessor_mask_action(self):
        preprocessor = PIIPreprocessor(regions=["cz"])
        
        text = "IČO: 25596641"
        processed = preprocessor.preprocess(text, action="mask")
        
        assert "25596641" not in processed
        assert "********" in processed

    def test_pii_preprocessor_remove_action(self):
        preprocessor = PIIPreprocessor(regions=["cz"])
        
        text = "Jan Novák, RČ: 8001011234"
        processed = preprocessor.preprocess(text, action="remove")
        
        assert "8001011234" not in processed
        assert "Jan Novák," in processed
        assert "[REDACTED]" not in processed

    def test_pii_preprocessor_callable(self):
        preprocessor = PIIPreprocessor(regions=["cz"])
        
        text = "IČO: 25596641"
        result = preprocessor(text)
        
        assert "25596641" not in result
        assert "[ICO]" in result

    def test_pii_preprocessor_invalid_action(self):
        preprocessor = PIIPreprocessor(regions=["cz"])
        
        with pytest.raises(ValueError, match="Invalid action"):
            preprocessor.preprocess("test", action="invalid")

    def test_pii_anonymizer_no_pii(self):
        anonymizer = PIIAnonymizer(regions=["cz"])
        
        text = "Hello world, no PII here"
        anonymized = anonymizer.anonymize(text)
        
        assert anonymized == text

    def test_pii_anonymizer_all_czech_detectors(self):
        anonymizer = PIIAnonymizer(regions=["cz"])
        
        text = """
        RČ: 8001011234
        IČO: 25596641
        DIČ: CZ25596641
        Účet: 19-2000145399/0800
        PSČ: 110 00
        Tel: 777 123 456
        """
        
        anonymized = anonymizer.anonymize(text)
        
        assert "8001011234" not in anonymized
        assert "25596641" not in anonymized
        assert "CZ25596641" not in anonymized
        assert "2000145399" not in anonymized
        assert "110 00" not in anonymized
        assert "777 123 456" not in anonymized

    def test_langchain_pipe_operator(self):
        preprocessor = PIIPreprocessor(regions=["cz"])
        
        text = "RČ: 8001011234"
        processed = preprocessor.preprocess(text, action="redact")
        
        assert isinstance(processed, str)
        assert "[RODNE_CISLO]" in processed

    def test_multiple_regions(self):
        anonymizer_cz = PIIAnonymizer(regions=["cz"])
        
        text_cz = "RČ: 8001011234"
        anonymized_cz = anonymizer_cz.anonymize(text_cz)
        
        assert "8001011234" not in anonymized_cz

    def test_preprocessor_preserves_structure(self):
        preprocessor = PIIPreprocessor(regions=["cz"])
        
        text = "Name: Jan, IČO: 25596641, City: Prague"
        processed = preprocessor.preprocess(text, action="redact")
        
        assert "Name:" in processed
        assert "City:" in processed
        assert "25596641" not in processed