from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app import db
from app.agent import trustops_agent
from app.lab import router as lab_router
from app.models import ReleaseAssessment, ReleaseAssessmentRequest
from app.realtime import event_hub
from app.reports import render_pr_comment
from app.settings import APP_NAME, APP_VERSION


app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=True)

# INTENTIONAL_VULNERABILITY: wildcard CORS for SSDLC scanner validation.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lab_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def startup() -> None:
    db.init_db()


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "service": APP_NAME, "version": APP_VERSION}


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>TrustOps Agent</title>
        <link rel="stylesheet" href="/static/styles.css" />
      </head>
      <body>
        <main class="shell">
          <section class="hero">
            <div>
              <p class="eyebrow">Software Supply Chain Trust</p>
              <h1>Can I trust this release?</h1>
              <p class="lede">Real-time AI agent workflow for SBOM, dependency, provenance, signature, license, and release-risk evidence.</p>
            </div>
            <button id="runDemo">Run Demo Assessment</button>
          </section>
          <section class="grid">
            <article>
              <h2>Live Agent Trace</h2>
              <ol id="events"></ol>
            </article>
            <article>
              <h2>Latest Decision</h2>
              <pre id="decision">{}</pre>
            </article>
          </section>
          <section>
            <h2>Release History</h2>
            <div id="history" class="history"></div>
          </section>
        </main>
        <script src="/static/app.js"></script>
      </body>
    </html>
    """


@app.get("/api/releases")
def list_releases() -> list[dict]:
    return db.list_assessments()


@app.post("/api/releases/assess", response_model=ReleaseAssessment)
async def assess_release(request: ReleaseAssessmentRequest) -> ReleaseAssessment:
    return await trustops_agent.assess_release(request, event_hub.broadcast)


@app.get("/api/releases/{release_id}", response_model=ReleaseAssessment)
def get_release(release_id: str) -> JSONResponse:
    assessment = db.get_assessment(release_id)
    if not assessment:
        return JSONResponse({"error": "release not found"}, status_code=404)
    return JSONResponse(assessment)


@app.get("/api/releases/{release_id}/evidence")
def get_evidence(release_id: str) -> JSONResponse:
    assessment = db.get_assessment(release_id)
    if not assessment:
        return JSONResponse({"error": "release not found"}, status_code=404)
    return JSONResponse(
        {
            "evidenceBundle": assessment["evidence"],
            "sbom": assessment["sbom"],
            "signals": assessment["signals"],
            "agentTrace": assessment["agentTrace"],
        }
    )


@app.get("/api/releases/{release_id}/pr-comment", response_class=PlainTextResponse)
def get_pr_comment(release_id: str) -> str:
    assessment = db.get_assessment(release_id)
    if not assessment:
        return "release not found"
    return render_pr_comment(ReleaseAssessment(**assessment))


@app.websocket("/ws/releases")
async def release_events(websocket: WebSocket) -> None:
    await event_hub.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        event_hub.disconnect(websocket)
