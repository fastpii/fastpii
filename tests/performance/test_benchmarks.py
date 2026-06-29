from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import psutil
import pytest

from fastpii import DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST, DEFAULT_PRIORITY, FastPII
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.cz import CzechPack


WARMUP_ITERATIONS = 3
LATENCY_ITERATIONS = 100
THROUGHPUT_SINGLE_ITERATIONS = 1000
THROUGHPUT_FULL_ITERATIONS = 100
PIPELINE_LATENCY_ITERATIONS = 50
LEAK_TEST_ITERATIONS = 500
CONCURRENT_THREADS = 10
CONCURRENT_TASKS_MULTIPLIER = 10

MEMORY_LIMIT_MB = 100
LEAK_GROWTH_LIMIT_MB = 5
IMPORT_LATENCY_MS = 500
DETECTOR_LATENCY_MS = 1.0
PIPELINE_LATENCY_MS = 100
THROUGHPUT_MIN_DOCS_PER_SEC = 100

DETECTOR_NAMES = [
    "rodne_cislo", "ico", "dic", "bank_account",
    "identity_card", "health_insurance", "iban", "credit_card",
    "email", "phone", "postal_code", "address",
    "name", "date_of_birth", "vehicle_plate",
]

SAMPLE_TEXTS = {
    "rodne_cislo": "Jan Novák, RČ: 800101/1238",
    "ico": "Společnost s.r.o., IČO: 25596641",
    "dic": "DIČ: CZ25596641",
    "bank_account": "Číslo účtu: 19-2000145399/0800",
    "identity_card": "OP: 123456789",
    "health_insurance": "Pojišťovna: 211",
    "iban": "IBAN: CZ49 0800 0000 0019 2000 1453 99",
    "credit_card": "Karta: 4111111111111111",
    "email": "Email: jan.novak@seznam.cz",
    "phone": "Telefon: +420 777 123 456",
    "postal_code": "PSČ: 110 00",
    "address": "Václavské náměstí 1, Praha 11000",
    "name": "Jan Novák",
    "date_of_birth": "Datum narození: 1.1.1980",
    "vehicle_plate": "SPZ: 1A2 3456",
}

FULL_TEXT = (
    "Smlouva uzavřená dne 1.1.2024 mezi Jan Novák, RČ: 800101/1238, "
    "IČO: 25596641, DIČ: CZ25596641, bytem Václavské náměstí 1, Praha 11000, "
    "PSČ 110 00, telefon +420 777 123 456, email jan.novak@seznam.cz, "
    "číslo účtu 19-2000145399/0800, zdravotní pojišťovna 211, "
    "IBAN: CZ49 0800 0000 0019 2000 1453 99, "
    "datum narození 1. ledna 1980, SPZ: 1A2 3456."
)


@pytest.fixture(scope="module")
def engine():
    scorer = ConfidenceScorer(
        base_scores=DEFAULT_CONFIDENCE_SCORES,
        context_boost=DEFAULT_CONTEXT_BOOST,
    )
    eng = FastPII(priority=DEFAULT_PRIORITY, confidence_scorer=scorer)
    eng.register(CzechPack())
    return eng


def _time_to_first_detect() -> float:
    scorer = ConfidenceScorer(
        base_scores=DEFAULT_CONFIDENCE_SCORES,
        context_boost=DEFAULT_CONTEXT_BOOST,
    )
    start = time.perf_counter()
    eng = FastPII(priority=DEFAULT_PRIORITY, confidence_scorer=scorer)
    eng.register(CzechPack())
    eng.detect("IČO: 25596641", ["ico"])
    return (time.perf_counter() - start) * 1000


class TestTimeToFirstDetect:
    def test_time_to_first_detect(self):
        elapsed_ms = _time_to_first_detect()
        assert elapsed_ms < IMPORT_LATENCY_MS, (
            f"Time to first detect {elapsed_ms:.1f}ms exceeds {IMPORT_LATENCY_MS}ms target"
        )

    def test_import_and_detect_memory(self):
        _time_to_first_detect()
        mem_mb = psutil.Process().memory_info().rss / 1024 / 1024
        assert mem_mb < MEMORY_LIMIT_MB, (
            f"Memory {mem_mb:.1f}MB exceeds {MEMORY_LIMIT_MB}MB target"
        )


class TestPerDetectorLatency:
    @pytest.mark.parametrize("detector_name", DETECTOR_NAMES)
    def test_single_detector_latency(self, engine, detector_name):
        text = SAMPLE_TEXTS[detector_name]

        for _ in range(WARMUP_ITERATIONS):
            engine.detect(text, [detector_name])

        start = time.perf_counter()
        for _ in range(LATENCY_ITERATIONS):
            engine.detect(text, [detector_name])
        elapsed = time.perf_counter() - start

        mean_ms = (elapsed / LATENCY_ITERATIONS) * 1000
        assert mean_ms < DETECTOR_LATENCY_MS, (
            f"{detector_name}: mean latency {mean_ms:.3f}ms exceeds {DETECTOR_LATENCY_MS}ms target"
        )

    def test_full_pipeline_latency(self, engine):
        for _ in range(WARMUP_ITERATIONS):
            engine.detect(FULL_TEXT)

        start = time.perf_counter()
        for _ in range(PIPELINE_LATENCY_ITERATIONS):
            engine.detect(FULL_TEXT)
        elapsed = time.perf_counter() - start

        mean_ms = (elapsed / PIPELINE_LATENCY_ITERATIONS) * 1000
        assert mean_ms < PIPELINE_LATENCY_MS, (
            f"Full pipeline mean latency {mean_ms:.1f}ms exceeds {PIPELINE_LATENCY_MS}ms target"
        )


class TestThroughput:
    def test_throughput_single_detector(self, engine):
        text = SAMPLE_TEXTS["ico"]

        for _ in range(WARMUP_ITERATIONS):
            engine.detect(text, ["ico"])

        start = time.perf_counter()
        for _ in range(THROUGHPUT_SINGLE_ITERATIONS):
            engine.detect(text, ["ico"])
        elapsed = time.perf_counter() - start

        docs_per_sec = THROUGHPUT_SINGLE_ITERATIONS / elapsed
        assert docs_per_sec >= THROUGHPUT_MIN_DOCS_PER_SEC, (
            f"Throughput {docs_per_sec:.0f} docs/sec below {THROUGHPUT_MIN_DOCS_PER_SEC} target"
        )

    def test_throughput_full_pipeline(self, engine):
        for _ in range(WARMUP_ITERATIONS):
            engine.detect(FULL_TEXT)

        start = time.perf_counter()
        for _ in range(THROUGHPUT_FULL_ITERATIONS):
            engine.detect(FULL_TEXT)
        elapsed = time.perf_counter() - start

        docs_per_sec = THROUGHPUT_FULL_ITERATIONS / elapsed
        assert docs_per_sec >= THROUGHPUT_MIN_DOCS_PER_SEC, (
            f"Full pipeline throughput {docs_per_sec:.0f} docs/sec below {THROUGHPUT_MIN_DOCS_PER_SEC} target"
        )


class TestMemory:
    def test_peak_memory_typical_workload(self, engine):
        process = psutil.Process()
        for _ in range(WARMUP_ITERATIONS):
            for text in SAMPLE_TEXTS.values():
                engine.detect(text)

        mem_peak = process.memory_info().rss / 1024 / 1024
        assert mem_peak < MEMORY_LIMIT_MB, (
            f"Peak memory {mem_peak:.1f}MB exceeds {MEMORY_LIMIT_MB}MB target"
        )

    def test_memory_no_leak_repeated_detection(self, engine):
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024

        for _ in range(LEAK_TEST_ITERATIONS):
            engine.detect(FULL_TEXT)

        mem_after = process.memory_info().rss / 1024 / 1024
        mem_growth = mem_after - mem_before
        assert mem_growth < LEAK_GROWTH_LIMIT_MB, (
            f"Memory grew {mem_growth:.1f}MB after {LEAK_TEST_ITERATIONS} iterations (potential leak)"
        )
        assert mem_after < MEMORY_LIMIT_MB, (
            f"Memory after {LEAK_TEST_ITERATIONS} iterations {mem_after:.1f}MB exceeds {MEMORY_LIMIT_MB}MB target"
        )


class TestConcurrency:
    def test_concurrent_detection_no_errors(self, engine):
        errors: list[str] = []
        results_count = 0
        total_tasks = CONCURRENT_THREADS * CONCURRENT_TASKS_MULTIPLIER

        with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
            futures = [
                executor.submit(engine.detect, FULL_TEXT)
                for _ in range(total_tasks)
            ]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results_count += 1
                    if not result.findings:
                        errors.append("No findings in concurrent detection")
                except Exception as e:
                    errors.append(f"Thread error: {e}")

        assert len(errors) == 0, f"Concurrent errors: {errors}"
        assert results_count == total_tasks, (
            f"Expected {total_tasks} results, got {results_count}"
        )

    def test_concurrent_deterministic_results(self, engine):
        expected_count: int | None = None

        with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
            futures = [
                executor.submit(engine.detect, FULL_TEXT)
                for _ in range(CONCURRENT_THREADS)
            ]
            for future in as_completed(futures):
                result = future.result()
                count = len(result.findings)
                if expected_count is None:
                    expected_count = count
                elif count != expected_count:
                    pytest.fail(
                        f"Non-deterministic results: got {count} findings, expected {expected_count}"
                    )