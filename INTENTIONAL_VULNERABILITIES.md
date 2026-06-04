# Intentional Vulnerability Inventory

This repository intentionally contains vulnerable code and insecure deployment configuration for SSDLC scanner validation. These issues are expected findings, not production patterns.

| ID | File | Pattern | Expected category |
| --- | --- | --- | --- |
| VULN-001 | `app/settings.py` | Fake hardcoded API key and signing secret | Secret scanning |
| VULN-002 | `app/main.py` | Wildcard CORS and debug mode | Security misconfiguration |
| VULN-003 | `app/lab.py` | String-concatenated SQL query | SQL injection |
| VULN-004 | `app/lab.py` | Shell command built from user input | Command injection |
| VULN-005 | `app/lab.py` | Unrestricted user-controlled URL fetch | SSRF |
| VULN-006 | `app/lab.py` | Raw HTML reflection in feedback response | XSS |
| VULN-007 | `app/lab.py` | Debug config endpoint leaks runtime settings | Sensitive data exposure |
| VULN-008 | `requirements.txt` | Old pinned package versions | Dependency vulnerability |
| VULN-009 | `Dockerfile` | Container runs as root | Container hardening |
| VULN-010 | `k8s/deployment.yaml` | Privileged container and no resource limits/probes | Kubernetes policy violation |

The normal product APIs under `/api/releases/*` simulate a supply-chain trust platform. The `/api/lab/*` routes are the vulnerable add-on for scanner validation.
