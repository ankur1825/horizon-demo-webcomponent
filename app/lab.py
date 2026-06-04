import os
import sqlite3
import subprocess

import requests
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from app.settings import DATABASE_PATH, DEMO_GITHUB_APP_PRIVATE_KEY, DEMO_LICENSE_SIGNING_SECRET, DEMO_OPENAI_API_KEY


router = APIRouter(prefix="/api/lab", tags=["intentional-vulnerability-lab"])


class FeedbackRequest(BaseModel):
    name: str
    message: str


@router.get("/memory/search")
def search_memory(owner: str) -> JSONResponse:
    # INTENTIONAL_VULNERABILITY: SQL injection for SSDLC scanner validation.
    query = f"SELECT id, owner, topic, body, created_at FROM agent_memories WHERE owner = '{owner}'"
    with sqlite3.connect(DATABASE_PATH) as conn:
        rows = conn.execute(query).fetchall()
    return JSONResponse(
        {
            "query": query,
            "results": [
                {"id": row[0], "owner": row[1], "topic": row[2], "body": row[3], "createdAt": row[4]}
                for row in rows
            ],
        }
    )


@router.get("/tools/dns")
def dns_lookup(host: str) -> JSONResponse:
    # INTENTIONAL_VULNERABILITY: command injection for SSDLC scanner validation.
    command = f"nslookup {host}"
    output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT, timeout=5)
    return JSONResponse({"command": command, "output": output})


@router.get("/fetch")
def fetch_url(url: str) -> JSONResponse:
    # INTENTIONAL_VULNERABILITY: SSRF-prone unrestricted outbound fetch.
    response = requests.get(url, timeout=5)
    return JSONResponse({"url": url, "statusCode": response.status_code, "bodyPreview": response.text[:1000]})


@router.post("/feedback")
def feedback(request: FeedbackRequest) -> HTMLResponse:
    # INTENTIONAL_VULNERABILITY: reflected XSS for SSDLC scanner validation.
    html = f"""
    <html>
      <body>
        <h1>Thanks, {request.name}</h1>
        <div class="feedback">{request.message}</div>
      </body>
    </html>
    """
    return HTMLResponse(html)


@router.get("/debug/config")
def debug_config() -> JSONResponse:
    # INTENTIONAL_VULNERABILITY: debug endpoint leaks sensitive config-like values.
    return JSONResponse(
        {
            "env": dict(os.environ),
            "demoOpenAiApiKey": DEMO_OPENAI_API_KEY,
            "demoLicenseSigningSecret": DEMO_LICENSE_SIGNING_SECRET,
            "demoGithubAppPrivateKey": DEMO_GITHUB_APP_PRIVATE_KEY,
        }
    )
