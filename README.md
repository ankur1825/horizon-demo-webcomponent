# Vulnerable Agentic AI Demo App

This repository is an intentionally vulnerable real-time agentic AI demo workload for validating the Horizon Relevance SSDLC pipeline.

Do not deploy this application outside an isolated test namespace.

## Purpose

The app simulates a small AI operations assistant:

- Accepts real-time tasks over WebSocket.
- Stores agent memories in SQLite.
- Provides HTTP endpoints for task planning, memory search, URL fetch, DNS-style diagnostics, and feedback.
- Includes a Dockerfile and Kubernetes manifest so the SSDLC platform can scan source code, dependencies, container configuration, and deployment policy.

## Expected SSDLC Findings

| Area | Seeded issue | Detection phase |
| --- | --- | --- |
| SAST | SQL injection in memory search | Code security scan |
| SAST | Command injection in DNS diagnostic endpoint | Code security scan |
| SAST | SSRF-prone URL fetch endpoint | Code security scan |
| SAST / DAST | Reflected XSS in feedback rendering | App security test |
| Secrets | Fake hardcoded API key and JWT secret | Secret scan |
| Dependency | Old pinned dependency versions | Dependency scan |
| Container | Container runs as root | Container scan |
| Kubernetes | Privileged pod, no limits, no probes | IaC / policy validation |
| AppSec | Wildcard CORS and debug responses | Policy / SAST |

## Local Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

WebSocket endpoint:

```text
ws://localhost:8080/ws/agent
```

HTTP endpoints:

```text
GET  /healthz
POST /api/agent/task
GET  /api/memory/search?owner=<value>
GET  /api/agent/tools/dns?host=<value>
GET  /api/agent/fetch?url=<value>
POST /api/feedback
```

## Container Build

```bash
docker build -t vulnerable-agentic-ai-app:demo .
```

## Kubernetes Test Deployment

```bash
kubectl create namespace ssdlc-vuln-demo
kubectl apply -n ssdlc-vuln-demo -f k8s/deployment.yaml
```

Delete after scanner validation:

```bash
kubectl delete namespace ssdlc-vuln-demo
```

## Safety Boundary

These vulnerabilities are present so the SSDLC scanner can find them. Keep this app out of shared production clusters and do not attach it to real credentials, real internal metadata services, or real customer data.
