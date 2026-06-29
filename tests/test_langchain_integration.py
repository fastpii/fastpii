from typing import Any, cast

import pytest

from fastpii import FastPII, DEFAULT_PRIORITY, DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.cz import CzechPack
from fastpii.integrations.langchain import PIIAnonymizer, PIIPreprocessor, create_pii_filter_tool


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


class TestLangChainEdgeCases:
    def test_empty_text(self, engine):
        anonymizer = PIIAnonymizer(engine=engine)
        preprocessor = PIIPreprocessor(engine=engine)

        assert anonymizer.anonymize("") == ""
        assert preprocessor.preprocess("", action="redact") == ""

    def test_text_with_no_pii(self, engine):
        anonymizer = PIIAnonymizer(engine=engine)
        preprocessor = PIIPreprocessor(engine=engine)

        text = "Hello world, this document contains no sensitive data."

        assert anonymizer.anonymize(text) == text
        assert preprocessor.preprocess(text, action="redact") == text

    def test_very_long_text(self, engine):
        anonymizer = PIIAnonymizer(engine=engine)
        preprocessor = PIIPreprocessor(engine=engine)

        text = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 90) + "RČ: 8001011238"

        anonymized = anonymizer.anonymize(text)
        processed = preprocessor.preprocess(text, action="redact")

        assert len(text) > 5000
        assert "8001011238" not in anonymized
        assert "8001011238" not in processed
        assert "[REDACTED]" in anonymized
        assert "[RODNE_CISLO]" in processed

    def test_multi_language_document(self):
        anonymizer = PIIAnonymizer(regions=["cz", "de"])
        preprocessor = PIIPreprocessor(regions=["cz", "de"])

        text = "CZ RČ: 8001011238, DE Steuer-ID: 86095742719"

        anonymized = anonymizer.anonymize(text)
        processed = preprocessor.preprocess(text, action="redact")

        assert "8001011238" not in anonymized
        assert "86095742719" not in anonymized
        assert "8001011238" not in processed
        assert "86095742719" not in processed
        assert "[REDACTED]" in anonymized
        assert "[RODNE_CISLO]" in processed
        assert "[STEUER_ID]" in processed

    def test_filter_tool_creation(self, engine, monkeypatch):
        import sys
        import types

        from pydantic import BaseModel

        import fastpii.integrations.langchain as langchain_integration

        langchain_module = types.ModuleType("langchain")
        tools_module = types.ModuleType("langchain.tools")
        cast(Any, tools_module).BaseTool = BaseModel
        cast(Any, langchain_module).tools = tools_module
        sys.modules["langchain"] = langchain_module
        sys.modules["langchain.tools"] = tools_module

        original_import_module = langchain_integration.importlib.import_module

        def fake_import_module(name: str):
            if name == "langchain.tools":
                return tools_module
            return original_import_module(name)

        monkeypatch.setattr(langchain_integration.importlib, "import_module", fake_import_module)

        engine_tool = cast(Any, create_pii_filter_tool(engine=engine))
        regions_tool = cast(Any, create_pii_filter_tool(regions=["cz"]))

        assert engine_tool.name == "pii_filter"
        assert regions_tool.name == "pii_filter"
        assert "8001011238" not in engine_tool._run("RČ: 8001011238")
        assert "8001011238" not in regions_tool._run("RČ: 8001011238")

    def test_callback_does_not_modify_original(self, engine):
        anonymizer = PIIAnonymizer(engine=engine)
        preprocessor = PIIPreprocessor(engine=engine)

        original = "IČO: 25596641"
        snapshot = original

        anonymized = anonymizer(original)
        processed = preprocessor(original)

        assert original == snapshot
        assert anonymized != original
        assert processed != original
