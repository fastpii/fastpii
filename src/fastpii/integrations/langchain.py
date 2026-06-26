import importlib

from fastpii import FastPII, DEFAULT_PRIORITY, DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries import get_country_pack


class PIIAnonymizer:
    """
    LangChain integration wrapper for FastPII anonymization.

    Accepts an explicit FastPII engine instance.

    Usage:
        >>> from fastpii import FastPII, DEFAULT_PRIORITY
        >>> from fastpii.countries.cz import CzechPack
        >>> engine = FastPII(priority=DEFAULT_PRIORITY)
        >>> engine.register(CzechPack())
        >>> anonymizer = PIIAnonymizer(engine=engine)
        >>> anonymizer.anonymize("Jan Novák, RČ: 8001011238")
    """

    engine: FastPII

    def __init__(self, engine: FastPII | None = None, regions: list[str] | None = None) -> None:
        if engine is not None:
            self.engine = engine
        elif regions is not None:
            scorer = ConfidenceScorer(
                base_scores=DEFAULT_CONFIDENCE_SCORES,
                context_boost=DEFAULT_CONTEXT_BOOST,
            )
            self.engine = FastPII(priority=DEFAULT_PRIORITY, confidence_scorer=scorer)
            for region_code in regions:
                pack_cls = get_country_pack(region_code)
                if pack_cls is not None:
                    self.engine.register(pack_cls())
        else:
            raise ValueError("Either engine or regions must be provided")

    def anonymize(self, text: str, replacement: str = "[REDACTED]") -> str:
        return self.engine.anonymize(text, replacement)

    def __call__(self, text: str) -> str:
        return self.anonymize(text)


class PIIPreprocessor:
    """
    LangChain integration wrapper for FastPII preprocessing.

    Accepts an explicit FastPII engine instance.

    Usage:
        >>> from fastpii import FastPII, DEFAULT_PRIORITY
        >>> from fastpii.countries.cz import CzechPack
        >>> engine = FastPII(priority=DEFAULT_PRIORITY)
        >>> engine.register(CzechPack())
        >>> preprocessor = PIIPreprocessor(engine=engine)
        >>> preprocessor.preprocess(text, action="redact")
    """

    engine: FastPII

    def __init__(self, engine: FastPII | None = None, regions: list[str] | None = None) -> None:
        if engine is not None:
            self.engine = engine
        elif regions is not None:
            scorer = ConfidenceScorer(
                base_scores=DEFAULT_CONFIDENCE_SCORES,
                context_boost=DEFAULT_CONTEXT_BOOST,
            )
            self.engine = FastPII(priority=DEFAULT_PRIORITY, confidence_scorer=scorer)
            for region_code in regions:
                pack_cls = get_country_pack(region_code)
                if pack_cls is not None:
                    self.engine.register(pack_cls())
        else:
            raise ValueError("Either engine or regions must be provided")

    def preprocess(self, text: str, action: str = "redact") -> str:
        if action == "redact":
            return self.engine.redact(text)
        elif action == "mask":
            return self.engine.mask(text)
        elif action == "remove":
            return self.engine.remove(text)
        else:
            raise ValueError(f"Invalid action: {action}. Must be one of: redact, mask, remove")

    def __call__(self, text: str) -> str:
        return self.preprocess(text)


def create_pii_filter_tool(engine: FastPII | None = None, regions: list[str] | None = None) -> object:
    base_tool_module = importlib.import_module("langchain.tools")
    BaseTool = base_tool_module.BaseTool
    from pydantic import Field

    class PIIFilterTool(BaseTool):
        name: str = "pii_filter"
        description: str = "Detect and redact PII (Personally Identifiable Information) from text. Use before sending user input to external services or LLMs."
        regions: list[str] | None = Field(default=None)

        def _run(self, text: str) -> str:
            app_engine = engine
            if app_engine is None:
                if not self.regions:
                    raise ValueError("regions must be provided when no engine is configured")
                scorer = ConfidenceScorer(
                    base_scores=DEFAULT_CONFIDENCE_SCORES,
                    context_boost=DEFAULT_CONTEXT_BOOST,
                )
                app_engine = FastPII(priority=DEFAULT_PRIORITY, confidence_scorer=scorer)
                for region_code in self.regions:
                    pack_cls = get_country_pack(region_code)
                    if pack_cls is not None:
                        app_engine.register(pack_cls())
            return app_engine.anonymize(text)

        async def _arun(self, text: str) -> str:
            return self._run(text)

    if engine is not None:
        return PIIFilterTool()
    elif regions is not None:
        return PIIFilterTool(regions=regions)
    else:
        raise ValueError("Either engine or regions must be provided")