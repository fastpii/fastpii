__all__ = ["ConfidenceScorer"]


class ConfidenceScorer:
    def __init__(self, base_scores: dict[str, float], context_boost: float) -> None:
        self._scores = base_scores
        self._context_boost = context_boost

    def calculate(self, has_context: bool, has_checksum: bool = False, base_confidence: float | None = None) -> float:
        if base_confidence is not None:
            score = base_confidence
        elif has_checksum:
            score = self._scores["checksum_validated"]
        elif has_context:
            score = self._scores["context_match"]
        else:
            score = self._scores["no_context"]

        if has_context and not has_checksum:
            score = min(1.0, score + self._context_boost)

        return round(score, 3)
