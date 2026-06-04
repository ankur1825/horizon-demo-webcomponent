# TrustOps Agent: Software Supply Chain Trust Platform

TrustOps Agent is a real-time enterprise AI agentic demo application for validating a Secure SDLC platform. It models a startup product wedge:

> Trust layer for software builds, dependencies, containers, and AI model artifacts.

The app answers:

- What dependencies are in this release?
- Was the build tampered with?
- Are containers signed?
- Is provenance present?
- Which packages create legal or security risk?
- Is this release safe to ship?
- Can we export an evidence bundle for a customer or auditor?

This repository intentionally includes vulnerable patterns so Horizon Relevance SSDLC testing can detect SAST, SCA, secret, container, Kubernetes, and DAST-style findings.

Do not deploy this application outside an isolated SSDLC validation namespace.

## Product Capabilities

- Real-time WebSocket release assessment stream.
- Agentic release analysis workflow.
- Simulated SBOM generation in CycloneDX-like shape.
- Dependency diff and maintainer reputation signals.
- Vulnerability and license risk scoring.
- Artifact signature and build provenance checks.
- Policy engine with pass, warn, and block decisions.
- Evidence bundle export per release.
- PR-comment style report generation.
- Demo dashboard for release trust history.

## Local Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Open:

```text
http://localhost:8080
```

## Core APIs

```text
GET  /healthz
GET  /
GET  /api/releases
POST /api/releases/assess
GET  /api/releases/{release_id}
GET  /api/releases/{release_id}/evidence
GET  /api/releases/{release_id}/pr-comment
WS   /ws/releases
```

## Intentional Vulnerability Add-On

The `/api/lab/*` endpoints are intentionally unsafe and exist only for SSDLC validation.

```text
GET  /api/lab/memory/search?owner=<value>
GET  /api/lab/tools/dns?host=<value>
GET  /api/lab/fetch?url=<value>
POST /api/lab/feedback
GET  /api/lab/debug/config
```

See [INTENTIONAL_VULNERABILITIES.md](INTENTIONAL_VULNERABILITIES.md).

## Container Build

```bash
docker build -t trustops-agent-vulnerable-demo:latest .
```

## Kubernetes Test Deployment

```bash
kubectl create namespace ssdlc-trustops-demo
kubectl apply -n ssdlc-trustops-demo -f k8s/deployment.yaml
```

Delete after validation:

```bash
kubectl delete namespace ssdlc-trustops-demo
```

## SSDLC Pipeline Metadata

The `horizon-pipeline.json` file describes this as a Python/FastAPI project with an intentional vulnerability profile.
