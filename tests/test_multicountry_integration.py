from __future__ import annotations

from fastpii import FastPII, DEFAULT_PRIORITY, DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST
from fastpii.countries import CountryPack
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries.cz import CzechPack
from fastpii.countries.de import GermanPack
from fastpii.countries.fr import FrenchPack
from fastpii.countries.pl import PolishPack
from fastpii.detectors.base import Detector
from fastpii.models import Finding
from fastpii.patterns.registry import get_shared_registry


def prime_patterns() -> None:
    registry = get_shared_registry()
    for region in ("cz", "de", "fr", "pl"):
        registry.load_patterns(region)


def make_engine(*packs: CountryPack, priority: dict[str, int] | None = None) -> FastPII:
    engine = FastPII(
        priority=priority or DEFAULT_PRIORITY,
        confidence_scorer=ConfidenceScorer(
            base_scores=DEFAULT_CONFIDENCE_SCORES,
            context_boost=DEFAULT_CONTEXT_BOOST,
        ),
    )
    if packs:
        engine.register_many(list(packs))
    return engine


def collect_raw_findings(engine: FastPII, text: str, *detector_names: str) -> list[Finding]:
    findings: list[Finding] = []
    for detector_name in detector_names:
        findings.extend(engine.get_detector(detector_name).detect(text))
    return findings


def get_pack_detector(pack: CountryPack, detector_name: str) -> Detector:
    return next(detector for detector in pack.detectors if detector.name == detector_name)


prime_patterns()


class TestMultiCountryIntegration:
    def test_multi_pack_registration(self):
        engine = make_engine(CzechPack(), GermanPack(), FrenchPack(), PolishPack())

        detectors = engine.list_detectors()
        names = {detector.name for detector in detectors}
        regions = {detector.region for detector in detectors}

        assert regions == {"cz", "de", "fr", "pl"}
        assert {"rodne_cislo", "steuer_id", "siren", "pesel"}.issubset(names)
        assert {"ico", "ust_id", "siret", "regon"}.issubset(names)

    def test_findings_include_correct_region_for_each_country(self):
        engine = make_engine(CzechPack(), GermanPack(), FrenchPack(), PolishPack())
        text = "IČO: 25596641, Steuer-ID: 86095742719, SIREN: 552120222, PESEL: 44051401458"

        result = engine.detect(text)
        findings_by_type = {finding.type: finding for finding in result.findings}

        assert findings_by_type["ico"].region == "cz"
        assert findings_by_type["steuer_id"].region == "de"
        assert findings_by_type["siren"].region == "fr"
        assert findings_by_type["pesel"].region == "pl"

    def test_detects_multiple_regions_in_same_document(self):
        engine = make_engine(CzechPack(), GermanPack(), FrenchPack(), PolishPack())
        text = "RČ: 8001011238, USt-IdNr: DE136695976, SIRET: 73282932000074, REGON: 12345678512347"

        result = engine.detect(text)

        assert [finding.type for finding in result.findings] == ["rodne_cislo", "ust_id", "siret", "regon"]
        assert {finding.region for finding in result.findings} == {"cz", "de", "fr", "pl"}

    def test_czech_and_german_detection(self):
        engine = make_engine(CzechPack(), GermanPack())
        text = "IČO: 25596641, Steuer-ID: 86095742719"

        result = engine.detect(text)

        assert [(finding.type, finding.region) for finding in result.findings] == [
            ("ico", "cz"),
            ("steuer_id", "de"),
        ]

    def test_french_and_polish_detection(self):
        engine = make_engine(FrenchPack(), PolishPack())
        text = "SIREN: 552120222, PESEL: 44051401458"

        result = engine.detect(text)

        assert [(finding.type, finding.region) for finding in result.findings] == [
            ("siren", "fr"),
            ("pesel", "pl"),
        ]

    def test_unique_findings_do_not_interfere_across_regions(self):
        engine = make_engine(CzechPack(), GermanPack(), FrenchPack(), PolishPack())
        text = "RČ: 8001011238, Steuer-ID: 86095742719, SIRET: 73282932000074, REGON: 123456785"

        result = engine.detect(text)

        assert {finding.type for finding in result.findings} == {"rodne_cislo", "steuer_id", "siret", "regon"}
        assert {finding.region for finding in result.findings} == {"cz", "de", "fr", "pl"}

    def test_numeric_only_patterns_keep_country_attribution(self):
        engine = make_engine(CzechPack(), PolishPack())
        text = "IČO: 25596641, NIP: 1234563218, REGON: 123456785"

        result = engine.detect(text)
        findings_by_type = {finding.type: finding for finding in result.findings}

        assert findings_by_type["ico"].region == "cz"
        assert findings_by_type["nip"].region == "pl"
        assert findings_by_type["regon"].region == "pl"

    def test_postal_code_detectors_keep_country_specific_formats(self):
        text = "PSČ: 110 00 Praha, Kod pocztowy: 00-001 Warszawa"
        cz_postal = get_pack_detector(CzechPack(), "postal_code").detect(text)
        pl_postal = get_pack_detector(PolishPack(), "postal_code").detect(text)

        assert [(finding.region, finding.value) for finding in cz_postal] == [("cz", "110 00")]
        assert [(finding.region, finding.value) for finding in pl_postal] == [("pl", "00-001")]

    def test_phone_detectors_keep_country_specific_prefixes(self):
        text = "Telefon: +49 30 1234567, Portable: +33 6 12 34 56 78"
        de_phone = get_pack_detector(GermanPack(), "phone").detect(text)
        fr_phone = get_pack_detector(FrenchPack(), "phone").detect(text)

        assert [(finding.region, finding.value) for finding in de_phone] == [("de", "49301234567")]
        assert [(finding.region, finding.value) for finding in fr_phone] == [("fr", "33612345678")]

    def test_single_czech_pack_excludes_foreign_unique_ids(self):
        engine = make_engine(CzechPack())
        text = "IČO: 25596641, Steuer-ID: 86095742719, SIRET: 73282932000074, PESEL: 44051401458"

        result = engine.detect(text)

        assert [(finding.type, finding.region, finding.value) for finding in result.findings] == [
            ("ico", "cz", "25596641")
        ]

    def test_adding_second_pack_keeps_existing_czech_detection(self):
        cz_engine = make_engine(CzechPack())
        cz_de_engine = make_engine(CzechPack(), GermanPack())
        text = "RČ: 8001011238, IČO: 25596641"

        cz_only = [(finding.type, finding.region, finding.value) for finding in cz_engine.detect(text).findings]
        cz_with_de = [(finding.type, finding.region, finding.value) for finding in cz_de_engine.detect(text).findings]

        assert cz_only == cz_with_de == [
            ("rodne_cislo", "cz", "8001011238"),
            ("ico", "cz", "25596641"),
        ]

    def test_cross_region_overlap_default_priority(self):
        engine = make_engine(CzechPack(), PolishPack())
        text = "NIP: 5260250274"

        raw_findings = collect_raw_findings(engine, text, "rodne_cislo", "nip")
        result = engine.detect(text)

        assert {(finding.type, finding.region) for finding in raw_findings} == {
            ("rodne_cislo", "cz"),
            ("nip", "pl"),
        }
        assert [(finding.type, finding.region, finding.value) for finding in result.findings] == [
            ("rodne_cislo", "cz", "5260250274")
        ]

    def test_cross_region_custom_priority_can_flip_winner(self):
        custom_priority = dict(DEFAULT_PRIORITY)
        custom_priority["nip"] = 120
        custom_priority["rodne_cislo"] = 80
        engine = make_engine(CzechPack(), PolishPack(), priority=custom_priority)
        text = "NIP: 5260250274"

        result = engine.detect(text)

        assert [(finding.type, finding.region, finding.value) for finding in result.findings] == [
            ("nip", "pl", "5260250274")
        ]
