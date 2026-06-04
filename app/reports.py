from app.models import ReleaseAssessment


def render_pr_comment(assessment: ReleaseAssessment) -> str:
    issues = "\n".join(
        f"- {signal.name}: {signal.status} ({signal.severity}) - {signal.detail}"
        for signal in assessment.signals
        if signal.status != "passed"
    )
    if not issues:
        issues = "- No blocking issues found"

    return f"""## Supply Chain Trust Report

**Repository:** `{assessment.repository}`
**Release:** `{assessment.releaseVersion}`
**Commit:** `{assessment.commitSha}`
**Environment:** `{assessment.targetEnvironment}`
**Risk:** `{assessment.riskLevel}` ({assessment.riskScore}/100)
**Decision:** `{assessment.decision}`

### Issues
{issues}

### Recommended Action
{assessment.recommendedAction}

### Evidence
- SBOM format: `{assessment.sbom.get("bomFormat")}`
- Dependency count: `{len(assessment.sbom.get("components", []))}`
- Artifact signature: `{assessment.evidence["artifact"]["signatureStatus"]}`
- Build provenance: `{assessment.evidence["artifact"]["provenanceStatus"]}`
"""
