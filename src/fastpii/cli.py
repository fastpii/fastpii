#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from fastpii import (
    FastPII,
    DEFAULT_PRIORITY,
    DEFAULT_CONFIDENCE_SCORES,
    DEFAULT_CONTEXT_BOOST,
    DetectionResult,
    ValidationResult,
)
from fastpii.core.confidence import ConfidenceScorer


def _build_engine(regions: list[str]) -> FastPII:
    scorer = ConfidenceScorer(
        base_scores=DEFAULT_CONFIDENCE_SCORES,
        context_boost=DEFAULT_CONTEXT_BOOST,
    )
    engine = FastPII(priority=DEFAULT_PRIORITY, confidence_scorer=scorer)
    from fastpii.countries import get_country_pack
    for region_code in regions:
        pack_cls = get_country_pack(region_code)
        if pack_cls is not None:
            engine.register(pack_cls())
    return engine


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FastPII - Fast PII Detection and Validation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Detect PII in text (Czech)
  fastpii detect "Jan Novák, RČ: 8001011234" -r cz

  # Detect PII in multiple regions
  fastpii detect "PESEL: 44051401458" -r cz pl

  # Detect PII from file
  fastpii detect --file document.txt -r cz

  # Validate specific identifier
  fastpii validate 8001011234 --detector rodne_cislo -r cz

  # List available detectors
  fastpii list-detectors -r cz

        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    detect_parser = subparsers.add_parser("detect", help="Detect PII in text or file")
    _ = detect_parser.add_argument("text", nargs="?", help="Text to analyze")
    _ = detect_parser.add_argument("--file", "-f", type=Path, help="Read text from file")
    _ = detect_parser.add_argument("--regions", "-r", nargs="+", required=True, help="Region codes to enable (e.g. cz pl de fr)")
    _ = detect_parser.add_argument("--format", "-fmt", choices=["json", "text"], default="text", help="Output format")
    _ = detect_parser.add_argument("--output", "-o", type=Path, help="Write output to file")

    validate_parser = subparsers.add_parser("validate", help="Validate a specific identifier")
    _ = validate_parser.add_argument("value", help="Value to validate")
    _ = validate_parser.add_argument("--detector", "-d", required=True, help="Detector to use")
    _ = validate_parser.add_argument("--regions", "-r", nargs="+", required=True, help="Region codes to enable")
    _ = validate_parser.add_argument("--format", "-fmt", choices=["json", "text"], default="text", help="Output format")

    list_parser = subparsers.add_parser("list-detectors", help="List available detectors")
    _ = list_parser.add_argument("--regions", "-r", nargs="+", required=True, help="Region codes to enable")
    _ = list_parser.add_argument("--format", "-fmt", choices=["json", "text"], default="text", help="Output format")

    args: argparse.Namespace = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "detect":
        handle_detect(args)
    elif args.command == "validate":
        handle_validate(args)
    elif args.command == "list-detectors":
        handle_list_detectors(args)


def handle_detect(args: argparse.Namespace) -> None:
    if args.file:
        try:
            text = args.file.read_text()
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        except Exception as error:
            print(f"Error reading file: {error}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        print("Error: Either text or --file must be provided", file=sys.stderr)
        sys.exit(1)

    engine = _build_engine(args.regions)
    result = engine.detect(text)

    if args.format == "json":
        output = result_to_json(result)
    else:
        output = result_to_text(result)

    if args.output:
        args.output.write_text(output)
        print(f"Output written to {args.output}")
    else:
        print(output)


def handle_validate(args: argparse.Namespace) -> None:
    engine = _build_engine(args.regions)

    try:
        result = engine.validate(args.value, detector_name=args.detector)
    except KeyError:
        print(f"Error: Detector '{args.detector}' not found", file=sys.stderr)
        print(f"Available detectors: {', '.join(d.name for d in engine.list_detectors())}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        output = validation_to_json(result)
    else:
        output = validation_to_text(result)

    print(output)


def handle_list_detectors(args: argparse.Namespace) -> None:
    engine = _build_engine(args.regions)
    detectors = engine.list_detectors()

    if args.format == "json":
        data = [{"name": d.name, "region": d.region, "description": d.description} for d in detectors]
        print(json.dumps(data, indent=2))
    else:
        print("Available Detectors:")
        print("-" * 60)
        for detector in detectors:
            print(f"  {detector.name:20} ({detector.region})")
            print(f"    {detector.description}")
        print("-" * 60)
        print(f"Total: {len(detectors)} detectors")


def result_to_json(result: DetectionResult) -> str:
    data = {
        "text": result.text,
        "findings": [
            {
                "type": f.type,
                "value": f.value,
                "start": f.start,
                "end": f.end,
                "confidence": f.confidence,
                "region": f.region,
                "metadata": f.metadata
            }
            for f in result.findings
        ],
        "detector_names": result.detector_names,
        "processing_time_ms": result.processing_time_ms
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def result_to_text(result: DetectionResult) -> str:
    lines = [f"Detected {len(result.findings)} finding(s) in {result.processing_time_ms}ms:", ""]

    if not result.findings:
        lines.append("  No PII detected.")
    else:
        for i, finding in enumerate(result.findings, 1):
            lines.append(f"  [{i}] {finding.type}: {finding.value}")
            lines.append(f"      Position: {finding.start}-{finding.end}")
            lines.append(f"      Region: {finding.region}")
            lines.append(f"      Confidence: {finding.confidence:.1%}")

            if finding.metadata:
                lines.append("      Metadata:")
                for key, value in finding.metadata.items():
                    lines.append(f"        - {key}: {value}")
            lines.append("")

    return "\n".join(lines)


def validation_to_json(result: ValidationResult) -> str:
    data = {
        "detector": result.detector,
        "value": result.value,
        "is_valid": result.is_valid,
        "metadata": result.metadata
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def validation_to_text(result: ValidationResult) -> str:
    status = "✓ VALID" if result.is_valid else "✗ INVALID"
    lines = [
        f"Validation Result:",
        f"  Detector: {result.detector}",
        f"  Value: {result.value}",
        f"  Status: {status}"
    ]

    if result.metadata:
        lines.append("  Metadata:")
        for key, value in result.metadata.items():
            lines.append(f"    - {key}: {value}")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
