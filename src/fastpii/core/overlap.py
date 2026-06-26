from fastpii.models import Finding


def deduplicate_findings(
    findings: list[Finding],
    priority: dict[str, int] | None = None,
) -> list[Finding]:
    if not findings:
        return findings

    if priority is None:
        raise ValueError(
            "Overlap priority is required. "
            "Pass an explicit priority dict mapping detector type names to integer priorities. "
            "Higher priority types win when findings overlap."
        )

    sorted_findings = sorted(
        findings,
        key=lambda f: (
            priority.get(f.type, 0),
            f.confidence,
            f.end - f.start,
        ),
        reverse=True,
    )

    result: list[Finding] = []
    for finding in sorted_findings:
        overlaps = False
        for existing in result:
            if finding.start >= existing.end:
                continue
            if finding.end <= existing.start:
                continue
            overlaps = True
            break
        if not overlaps:
            result.append(finding)

    result.sort(key=lambda f: f.start)
    return result