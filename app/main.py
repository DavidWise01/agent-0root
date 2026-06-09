"""
agent-0root · the service.

FastAPI app that serves the 0root.ai homepage at / and the deterministic agent at
/v1/agent. Health and version endpoints make the deploy auditable (version == the
deployed commit). Listens on $PORT (Railway sets it).
"""
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .agent import handle, VERSION, COMMANDS
from .limen import decode_line, reference as limen_reference

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(HERE, "..", "static")

app = FastAPI(title="agent-0root", version=VERSION,
              description="0root.ai — a deterministic agentic endpoint. Same input → same output.")


class AgentRequest(BaseModel):
    input: str = ""


@app.get("/")
def home():
    """The 0root.ai public face."""
    idx = os.path.join(STATIC, "index.html")
    if os.path.exists(idx):
        return FileResponse(idx)
    return JSONResponse({"service": "agent-0root", "version": VERSION,
                         "try": "/v1/agent?q=resolve"})


@app.get("/health")
def health():
    return {"ok": True, "version": VERSION}


@app.get("/version")
def version():
    """The deployed commit. Every response ties to this — that's the audit trail."""
    return {"service": "agent-0root", "version": VERSION, "deterministic": True,
            "commands": list(COMMANDS),
            "routes": ["GET /", "GET /health", "GET /version",
                       "POST|GET /v1/agent", "POST|GET /v1/limen"]}


@app.post("/v1/agent")
def agent_post(req: AgentRequest):
    return handle(req.input)


@app.get("/v1/agent")
def agent_get(q: str = ""):
    """Convenience GET so you can test in a browser: /v1/agent?q=resolve"""
    return handle(q)


class LimenRequest(BaseModel):
    line: str = ""


@app.post("/v1/limen")
def limen_post(req: LimenRequest):
    """Decode a LIMEN line into reconstructed crossings (deterministic)."""
    if not req.line.strip():
        return limen_reference()
    return decode_line(req.line)


@app.get("/v1/limen")
def limen_get(line: str = ""):
    """Browser test: /v1/limen?line=↑◐«truth» ↓⊘«mirror»  (empty → the gate vocabulary)."""
    if not line.strip():
        return limen_reference()
    return decode_line(line)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
