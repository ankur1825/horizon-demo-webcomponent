from datetime import datetime, timezone

from app.models import Dependency, ReleaseAssessmentRequest


def generate_cyclonedx_like_sbom(request: ReleaseAssessmentRequest) -> dict:
    components = []
    for dependency in request.dependencies:
        components.append(
            {
                "type": "library",
                "name": dependency.name,
                "version": dependency.version,
                "licenses": [{"license": {"id": dependency.license or "UNKNOWN"}}],
                "purl": f"pkg:{dependency.registry}/{dependency.name}@{dependency.version}",
                "properties": [
                    {"name": "trustops:runtime", "value": str(dependency.runtime).lower()},
                    {"name": "trustops:maintainer", "value": dependency.maintainer or "unknown"},
                ],
            }
        )

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{request.commitSha}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": {
                "type": "application",
                "name": request.repository,
                "version": request.releaseVersion,
            },
            "properties": [
                {"name": "trustops:branch", "value": request.branch},
                {"name": "trustops:targetEnvironment", "value": request.targetEnvironment},
            ],
        },
        "components": components,
    }
