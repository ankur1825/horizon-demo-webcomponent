import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from app import db
from app.models import AgentStep, ReleaseAssessment, ReleaseAssessmentRequest
from app.risk_engine import evaluate_artifact, evaluate_dependencies, score_and_decide
from app.sbom import generate_cyclonedx_like_sbom


class TrustOpsAgent:
    async def assess_release(self, request: ReleaseAssessmentRequest, event_sink=None) -> ReleaseAssessment:
        trace: list[AgentStep] = []

        async def step(name: str, message: str) -> None:
            event = AgentStep(name=name, status="completed", message=message)
            trace.append(event)
            if event_sink:
                await event_sink({"event": "agent.step", "data": event.dict()})
            await asyncio.sleep(0.05)

        await step("ingest-release", f"Loaded {request.repository}@{request.commitSha}")

        sbom = generate_cyclonedx_like_sbom(request)
        await step("generate-sbom", f"Generated SBOM with {len(sbom['components'])} components")

        dependency_signals = evaluate_dependencies(request.dependencies)
        await step("analyze-dependencies", "Computed CVE, license, and dependency-change signals")

        artifact_signals = evaluate_artifact(
            request.artifact.signatureStatus,
            request.artifact.provenanceStatus,
            request.targetEnvironment,
        )
        await step("verify-artifact", "Checked artifact signature and build provenance signals")

        signals = dependency_signals + artifact_signals
        risk_score, risk_level, decision, recommended_action = score_and_decide(signals)
        await step("policy-decision", f"Decision={decision}; riskScore={risk_score}")

        release_id = f"{request.repository}-{request.commitSha}-{uuid4().hex[:6]}"
        evidence = {
            "releaseId": release_id,
            "repository": request.repository,
            "commitSha": request.commitSha,
            "targetEnvironment": request.targetEnvironment,
            "artifact": request.artifact.dict(),
            "dependencyCount": len(request.dependencies),
            "policyDecision": decision,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "standards": ["SLSA", "NIST SSDF", "CycloneDX", "SPDX", "Sigstore"],
        }

        assessment = ReleaseAssessment(
            releaseId=release_id,
            organization=request.organization,
            repository=request.repository,
            branch=request.branch,
            commitSha=request.commitSha,
            releaseVersion=request.releaseVersion,
            targetEnvironment=request.targetEnvironment,
            riskScore=risk_score,
            riskLevel=risk_level,
            decision=decision,
            recommendedAction=recommended_action,
            signals=signals,
            sbom=sbom,
            evidence=evidence,
            agentTrace=trace,
            createdAt=datetime.now(timezone.utc).isoformat(),
        )
        db.save_assessment(assessment.dict())
        db.remember(request.requester, "release-assessment", f"{release_id}: {decision} ({risk_score})")
        if event_sink:
            await event_sink({"event": "assessment.completed", "data": assessment.dict()})
        return assessment


trustops_agent = TrustOpsAgent()
