from app.models import Decision, Dependency, RiskLevel, Signal
from app.settings import APPROVED_LICENSES, DEFAULT_POLICIES, KNOWN_BAD_PACKAGES


def _version_jump_score(dependency: Dependency) -> int:
    if not dependency.previousVersion:
        return 4
    old_major = dependency.previousVersion.split(".")[0]
    new_major = dependency.version.split(".")[0]
    return 8 if old_major != new_major else 2


def _fake_cve_count(dependency: Dependency) -> int:
    vulnerable_names = {"lodash", "debug", "minimist", "serialize-javascript", "requests"}
    if dependency.name in vulnerable_names:
        return 1
    if dependency.version.startswith(("0.", "1.0", "2.28")):
        return 1
    return 0


def evaluate_dependencies(dependencies: list[Dependency]) -> list[Signal]:
    signals: list[Signal] = []
    critical_count = 0
    unknown_license_count = 0
    risky_change_count = 0

    for dependency in dependencies:
        cves = _fake_cve_count(dependency)
        if cves and dependency.runtime:
            critical_count += cves
        if not dependency.license or dependency.license not in APPROVED_LICENSES:
            unknown_license_count += 1
        if dependency.name in KNOWN_BAD_PACKAGES or _version_jump_score(dependency) >= 8:
            risky_change_count += 1

    signals.append(
        Signal(
            name="criticalRuntimeVulnerabilities",
            status="failed" if critical_count else "passed",
            severity=RiskLevel.critical if critical_count else RiskLevel.low,
            detail=f"{critical_count} critical runtime vulnerability signal(s) found",
        )
    )
    signals.append(
        Signal(
            name="unknownLicenses",
            status="warning" if unknown_license_count else "passed",
            severity=RiskLevel.medium if unknown_license_count else RiskLevel.low,
            detail=f"{unknown_license_count} package(s) have unknown or unapproved licenses",
        )
    )
    signals.append(
        Signal(
            name="riskyDependencyChanges",
            status="warning" if risky_change_count else "passed",
            severity=RiskLevel.high if risky_change_count else RiskLevel.low,
            detail=f"{risky_change_count} dependency change(s) need maintainer/reputation review",
        )
    )
    return signals


def evaluate_artifact(signature_status: str, provenance_status: str, target_environment: str) -> list[Signal]:
    prod_like = target_environment.upper() in {"PROD", "PRODUCTION"}
    return [
        Signal(
            name="artifactSignature",
            status="passed" if signature_status == "valid" else "failed" if prod_like else "warning",
            severity=RiskLevel.critical if prod_like and signature_status != "valid" else RiskLevel.medium,
            detail=f"Artifact signature status is {signature_status}",
        ),
        Signal(
            name="buildProvenance",
            status="passed" if provenance_status == "present" else "warning",
            severity=RiskLevel.medium if provenance_status != "present" else RiskLevel.low,
            detail=f"Build provenance status is {provenance_status}",
        ),
    ]


def score_and_decide(signals: list[Signal]) -> tuple[int, RiskLevel, Decision, str]:
    score = 0
    for signal in signals:
        if signal.severity == RiskLevel.critical and signal.status == "failed":
            score += 40
        elif signal.severity == RiskLevel.high:
            score += 25
        elif signal.severity == RiskLevel.medium:
            score += 12
        else:
            score += 2
    score = min(score, 100)

    has_critical_blocker = any(s.severity == RiskLevel.critical and s.status == "failed" for s in signals)
    has_warning = any(s.status in {"warning", "failed"} for s in signals)

    if has_critical_blocker and DEFAULT_POLICIES["blockCriticalRuntimeCve"]:
        return score, RiskLevel.critical, Decision.block, "Block release until critical supply-chain issues are resolved."
    if score >= 70:
        return score, RiskLevel.high, Decision.review, "Manual security review required before release."
    if has_warning:
        return score, RiskLevel.medium, Decision.review, "Review warnings and document exceptions before shipping."
    return score, RiskLevel.low, Decision.ship, "Release can ship based on current trust signals."
