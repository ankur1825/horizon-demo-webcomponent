import os
from pathlib import Path


APP_NAME = "TrustOps Agent"
APP_VERSION = "0.2.0"
DATABASE_PATH = Path(os.getenv("TRUSTOPS_DB", "/tmp/trustops_agent.db"))

# INTENTIONAL_VULNERABILITY: fake hardcoded secrets for SSDLC scanner validation.
DEMO_GITHUB_APP_PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nFAKE-TRUSTOPS-DEMO-KEY\n-----END PRIVATE KEY-----"
DEMO_OPENAI_API_KEY = "sk-trustops-demo-do-not-use-1234567890"
DEMO_LICENSE_SIGNING_SECRET = "trustops-demo-license-signing-secret"

DEFAULT_POLICIES = {
    "blockCriticalRuntimeCve": True,
    "warnUnknownLicense": True,
    "blockUnsignedProductionArtifact": True,
    "warnMissingProvenance": True,
    "warnRiskyDependencyChange": True,
}

KNOWN_BAD_PACKAGES = {
    "event-stream": "Historical package compromise risk",
    "left-pad": "Low maintainer confidence and abandoned package risk",
    "debug": "Old transitive versions often appear in vulnerable graphs",
    "lodash": "Commonly vulnerable when pinned to old versions",
}

APPROVED_LICENSES = {"MIT", "Apache-2.0", "BSD-3-Clause", "ISC"}
