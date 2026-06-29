from __future__ import annotations

import importlib
import time
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor

import pytest

from fastpii import DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST, DEFAULT_PRIORITY, FastPII
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.cz import CzechPack
from fastpii.countries.de import GermanPack
from fastpii.countries.fr import FrenchPack
from fastpii.countries.pl import PolishPack
from fastpii.patterns import regions as pattern_regions
from fastpii.patterns.registry import PatternRegistry, get_shared_registry, set_shared_registry


LOAD_ITERATIONS = 5
LOOKUP_ITERATIONS = 100000
DETECTION_ITERATIONS = 500
WARMUP_ITERATIONS = 10
CONCURRENT_WORKERS = 8
CONCURRENT_TASKS = 32

REGION_LOAD_TARGET_MS = 100.0
LOOKUP_TARGET_MS = 0.01
DETECTION_TARGET_MS = 1.0

FULL_DETECTION_TEXT = "IČO: 25596641"


def _build_engine() -> FastPII:
    scorer = ConfidenceScorer(
        base_scores=DEFAULT_CONFIDENCE_SCORES,
        context_boost=DEFAULT_CONTEXT_BOOST,
    )
    engine = FastPII(priority=DEFAULT_PRIORITY, confidence_scorer=scorer)
    engine.register_many([CzechPack(), GermanPack(), FrenchPack(), PolishPack()])
    return engine


@pytest.fixture(scope="module")
def full_registry() -> PatternRegistry:
    registry = PatternRegistry()
    registry.load_all_regions()
    return registry


@pytest.fixture(scope="module")
def full_engine() -> Generator[FastPII, None, None]:
    original_registry = get_shared_registry()
    registry = PatternRegistry()
    registry.load_all_regions()
    set_shared_registry(registry)
    try:
        yield _build_engine()
    finally:
        set_shared_registry(original_registry)


class TestPatternRegistryBenchmarks:
    def test_load_all_regions_under_100ms(self):
        _ = pattern_regions.get_region_loaders()

        best_ms: float | None = None
        for _ in range(LOAD_ITERATIONS):
            start = time.perf_counter()
            registry = PatternRegistry()
            registry.load_all_regions()
            elapsed_ms = (time.perf_counter() - start) * 1000
            if best_ms is None or elapsed_ms < best_ms:
                best_ms = elapsed_ms

        assert best_ms is not None
        assert best_ms < REGION_LOAD_TARGET_MS, (
            f"Loading all regions took {best_ms:.3f}ms, exceeds {REGION_LOAD_TARGET_MS}ms"
        )

    def test_pattern_lookup_by_entity_type_under_001ms(self, full_registry: PatternRegistry):
        for _ in range(WARMUP_ITERATIONS):
            _ = full_registry.get_patterns("phone", "fr")

        start = time.perf_counter()
        for _ in range(LOOKUP_ITERATIONS):
            _ = full_registry.get_patterns("phone", "fr")
        elapsed = time.perf_counter() - start

        mean_ms = (elapsed / LOOKUP_ITERATIONS) * 1000
        assert mean_ms < LOOKUP_TARGET_MS, (
            f"Entity lookup mean {mean_ms:.6f}ms exceeds {LOOKUP_TARGET_MS}ms"
        )

    def test_pattern_lookup_by_cache_key_under_001ms(self, full_registry: PatternRegistry):
        for _ in range(WARMUP_ITERATIONS):
            _ = full_registry.get_pattern("phone", "mobile", "fr")

        start = time.perf_counter()
        for _ in range(LOOKUP_ITERATIONS):
            _ = full_registry.get_pattern("phone", "mobile", "fr")
        elapsed = time.perf_counter() - start

        mean_ms = (elapsed / LOOKUP_ITERATIONS) * 1000
        assert mean_ms < LOOKUP_TARGET_MS, (
            f"Cache-key lookup mean {mean_ms:.6f}ms exceeds {LOOKUP_TARGET_MS}ms"
        )

    def test_full_detection_under_1ms_with_all_regions(self, full_engine: FastPII):
        for _ in range(WARMUP_ITERATIONS):
            _ = full_engine.detect(FULL_DETECTION_TEXT)

        start = time.perf_counter()
        for _ in range(DETECTION_ITERATIONS):
            _ = full_engine.detect(FULL_DETECTION_TEXT)
        elapsed = time.perf_counter() - start

        mean_ms = (elapsed / DETECTION_ITERATIONS) * 1000
        assert mean_ms < DETECTION_TARGET_MS, (
            f"Detection mean {mean_ms:.6f}ms exceeds {DETECTION_TARGET_MS}ms"
        )

    def test_patterns_are_not_recompiled_on_repeated_detection(self):
        original_registry = get_shared_registry()
        registry = PatternRegistry()
        registry.load_all_regions()
        pattern = registry.get_pattern("ico", "standard", "cz")

        assert pattern is not None
        compiled = pattern.compiled

        set_shared_registry(registry)
        try:
            engine = _build_engine()
            for _ in range(WARMUP_ITERATIONS):
                _ = engine.detect(FULL_DETECTION_TEXT)
        finally:
            set_shared_registry(original_registry)

        assert pattern.compiled is compiled

    def test_shared_registry_concurrent_detection_is_deterministic(self, full_engine: FastPII):
        expected = full_engine.detect(FULL_DETECTION_TEXT)
        expected_values = [(finding.type, finding.value) for finding in expected.findings]

        def run_detection() -> list[tuple[str, str]]:
            result = full_engine.detect(FULL_DETECTION_TEXT)
            return [(finding.type, finding.value) for finding in result.findings]

        with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
            futures = [executor.submit(run_detection) for _ in range(CONCURRENT_TASKS)]
            results = [future.result() for future in futures]

        assert all(result == expected_values for result in results)

    def test_get_region_loaders_returns_cached_result(self, monkeypatch: pytest.MonkeyPatch):
        pattern_regions.get_region_loaders.cache_clear()
        first = pattern_regions.get_region_loaders()

        def fail_import(module_path: str):
            raise AssertionError(f"unexpected import for {module_path}")

        monkeypatch.setattr(importlib, "import_module", fail_import)

        second = pattern_regions.get_region_loaders()
        assert second is first
