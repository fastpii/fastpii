import re


class ContextWindowMatcher:
    """Context-aware matching utility for PII detection.

    Searches a text window around a position for context keywords,
    determining whether a regex match is likely genuine PII or a false positive.
    """

    def __init__(self, context_words: list[str], window_size: int = 50, case_sensitive: bool = False) -> None:
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = r"\b(?:" + "|".join(re.escape(w) for w in context_words) + r")\b\s*:?"
        self._regex: re.Pattern[str] = re.compile(pattern, flags)
        self._window_size: int = window_size

    def has_context(self, text: str, position: int) -> bool:
        window_start = max(0, position - self._window_size)
        window = text[window_start:position]
        return bool(self._regex.search(window))