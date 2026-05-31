import os
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel


DATABASE_PATH = Path(os.getenv("AGENT_DB", "/tmp/agent_memory.db"))

# INTENTIONAL_VULNERABILITY: fake hardcoded secrets for scanner validation only.
DEMO_OPENAI_API_KEY = "sk-hr-demo-do-not-use-1234567890"
DEMO_JWT_SECRET = "super-secret-demo-jwt-signing-key"


app = FastAPI(
    title="Horizon Vulnerable Agentic AI Demo",
    version="0.1.0",
    debug=True,
)

# INTENTIONAL_VULNERABILITY: wildcard CORS for policy/SAST detection.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    owner: str
    task: str
    context: str | None = None


class FeedbackRequest(BaseModel):
    name: str
    message: str


class AgentRuntime:
    def __init__(self) -> None:
        self.connections: list[WebSocket] = []
        self._init_db()

    def _init_db(self) -> None:
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner TEXT NOT NULL,
                    task TEXT NOT NULL,
                    context TEXT,
                    plan TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, payload: dict) -> None:
        stale = []
        for websocket in self.connections:
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(websocket)

    def plan_task(self, request: TaskRequest) -> dict:
        plan = [
            "Classify request intent",
            "Retrieve matching operational memory",
            "Select tool: deploy-check, risk-check, or evidence-check",
            "Return recommended next action",
        ]
        result = {
            "owner": request.owner,
            "task": request.task,
            "context": request.context,
            "plan": plan,
            "risk": "demo-high" if "prod" in request.task.lower() else "demo-medium",
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        self.save_memory(request, " | ".join(plan))
        return result

    def save_memory(self, request: TaskRequest, plan: str) -> None:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute(
                "INSERT INTO memories(owner, task, context, plan, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    request.owner,
                    request.task,
                    request.context,
                    plan,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )


runtime = AgentRuntime()


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "service": "vulnerable-agentic-ai-demo"}


@app.post("/api/agent/task")
async def create_agent_task(request: TaskRequest) -> dict:
    result = runtime.plan_task(request)
    await runtime.broadcast({"event": "agent.plan.created", "data": result})
    return result


@app.websocket("/ws/agent")
async def websocket_agent(websocket: WebSocket) -> None:
    await runtime.connect(websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            request = TaskRequest(
                owner=str(payload.get("owner", "anonymous")),
                task=str(payload.get("task", "")),
                context=payload.get("context"),
            )
            result = runtime.plan_task(request)
            await websocket.send_json({"event": "agent.plan.created", "data": result})
    except WebSocketDisconnect:
        runtime.disconnect(websocket)


@app.get("/api/memory/search")
def search_memory(owner: str) -> JSONResponse:
    # INTENTIONAL_VULNERABILITY: SQL injection for scanner validation.
    query = f"SELECT id, owner, task, context, plan, created_at FROM memories WHERE owner = '{owner}'"
    with sqlite3.connect(DATABASE_PATH) as conn:
        rows = conn.execute(query).fetchall()
    return JSONResponse(
        {
            "query": query,
            "results": [
                {
                    "id": row[0],
                    "owner": row[1],
                    "task": row[2],
                    "context": row[3],
                    "plan": row[4],
                    "createdAt": row[5],
                }
                for row in rows
            ],
        }
    )


@app.get("/api/agent/tools/dns")
def dns_lookup(host: str) -> JSONResponse:
    # INTENTIONAL_VULNERABILITY: command injection for scanner validation.
    command = f"nslookup {host}"
    output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT, timeout=5)
    return JSONResponse({"command": command, "output": output})


@app.get("/api/agent/fetch")
def fetch_url(url: str) -> JSONResponse:
    # INTENTIONAL_VULNERABILITY: SSRF-prone unrestricted outbound fetch.
    response = requests.get(url, timeout=5)
    return JSONResponse(
        {
            "url": url,
            "statusCode": response.status_code,
            "bodyPreview": response.text[:1000],
        }
    )


@app.post("/api/feedback")
def feedback(request: FeedbackRequest) -> HTMLResponse:
    # INTENTIONAL_VULNERABILITY: reflected XSS for scanner validation.
    html = f"""
    <html>
      <body>
        <h1>Thanks, {request.name}</h1>
        <div class="feedback">{request.message}</div>
      </body>
    </html>
    """
    return HTMLResponse(html)
