# Intentional Vulnerability Inventory

This file documents the intentionally vulnerable patterns seeded into the demo app. It exists so reviewers know these findings are expected during SSDLC validation.

| ID | File | Pattern | Expected category |
| --- | --- | --- | --- |
| VULN-001 | `app/main.py` | Hardcoded fake API key and JWT secret | Secret scanning |
| VULN-002 | `app/main.py` | Wildcard CORS | Security misconfiguration |
| VULN-003 | `app/main.py` | String-concatenated SQL query | SQL injection |
| VULN-004 | `app/main.py` | Shell command built from user input | Command injection |
| VULN-005 | `app/main.py` | Unrestricted user-controlled URL fetch | SSRF |
| VULN-006 | `app/main.py` | Raw HTML reflection in feedback response | XSS |
| VULN-007 | `requirements.txt` | Old pinned package versions | Dependency vulnerability |
| VULN-008 | `Dockerfile` | Root container user | Container hardening |
| VULN-009 | `k8s/deployment.yaml` | Privileged container and no resource limits | Kubernetes policy violation |

These are not false positives for the demo. In a real application, every item above should be remediated before release promotion.
