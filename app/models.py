from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Decision(str, Enum):
    ship = "ship"
    review = "review"
    block = "block"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Dependency(BaseModel):
    name: str
    version: str
    license: str | None = None
    registry: str = "npm"
    maintainer: str | None = None
    previousVersion: str | None = None
    runtime: bool = True


class Artifact(BaseModel):
    image: str
    digest: str | None = None
    signatureStatus: str = "missing"
    provenanceStatus: str = "missing"
    sbomFormat: str = "CycloneDX"


class ReleaseAssessmentRequest(BaseModel):
    organization: str = "acme-fintech"
    repository: str
    branch: str = "main"
    commitSha: str = Field(default_factory=lambda: uuid4().hex[:12])
    releaseVersion: str = "0.1.0"
    targetEnvironment: str = "DEV"
    artifact: Artifact
    dependencies: list[Dependency]
    changedFiles: list[str] = []
    requester: str = "developer@example.com"


class Signal(BaseModel):
    name: str
    status: str
    severity: RiskLevel
    detail: str


class AgentStep(BaseModel):
    name: str
    status: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReleaseAssessment(BaseModel):
    releaseId: str
    organization: str
    repository: str
    branch: str
    commitSha: str
    releaseVersion: str
    targetEnvironment: str
    riskScore: int
    riskLevel: RiskLevel
    decision: Decision
    recommendedAction: str
    signals: list[Signal]
    sbom: dict[str, Any]
    evidence: dict[str, Any]
    agentTrace: list[AgentStep]
    createdAt: str
