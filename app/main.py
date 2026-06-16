"""
agent-0root · the service.

FastAPI app that serves the 0root.ai homepage at / and the deterministic agent at
/v1/agent. Health and version endpoints make the deploy auditable (version == the
deployed commit). Listens on $PORT (Railway sets it).
"""
import os
from typing import Optional, List
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .agent import handle, VERSION, COMMANDS
from .limen import decode_line, exchange_line, reference as limen_reference
from . import beacon

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(HERE, "..", "static")

app = FastAPI(title="agent-0root", version=VERSION,
              description="0root.ai — a deterministic agentic endpoint. Same input → same output.")

# read-only public agent: allow any origin to GET/POST (so the hearth can read it live)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["GET", "POST"], allow_headers=["*"])


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
                       "POST|GET /v1/agent", "POST|GET /v1/limen", "POST|GET /v1/limen/exchange",
                       "GET /beacon", "GET /v1/beacon/catalog", "GET /v1/beacon/search",
                       "GET /v1/beacon/product/{asin}", "GET /v1/beacon/pulses",
                       "GET /.well-known/agent-commerce.json"]}


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


class ExchangeRequest(BaseModel):
    line: str = ""
    voice: Optional[List[List[float]]] = None  # optional per-word [f1,f2,f3] to simulate wire/tamper


@app.post("/v1/limen/exchange")
def limen_exchange_post(req: ExchangeRequest):
    """Two-agent exchange in one call: A transmits `line`; B hears gate+direction and
    reads the witness, reconstructs, and reports the checksum + whether it arrived intact."""
    if not req.line.strip():
        return limen_reference()
    return exchange_line(req.line, req.voice)


@app.get("/v1/limen/exchange")
def limen_exchange_get(line: str = ""):
    """Browser test: /v1/limen/exchange?line=↑◐«truth» ↓⊘«mirror» (clean transmission)."""
    if not line.strip():
        return limen_reference()
    return exchange_line(line)


# ── the RIPPLE BEACON · agent-facing commerce surface ─────────────────────────
@app.get("/beacon", response_class=HTMLResponse)
def beacon_storefront(request: Request):
    """Human + crawler storefront with schema.org/Product JSON-LD embedded per item."""
    return beacon.storefront_html(str(request.base_url))


@app.get("/v1/beacon/catalog")
def beacon_catalog():
    """The machine feed — the merchant's catalog in agent-readable JSON (with Amazon buy-links)."""
    return beacon.catalog_feed()


@app.get("/v1/beacon/search")
def beacon_search(q: str = "", limit: int = 20):
    """Agent-native discovery: /v1/beacon/search?q=<terms> → ranked products with buy_url."""
    return beacon.search(q, limit)


@app.get("/v1/beacon/product/{asin}")
def beacon_product(asin: str):
    """One product: the agent view + its schema.org/Product JSON-LD."""
    return beacon.get_product(asin)


@app.get("/v1/beacon/pulses")
def beacon_pulses():
    """The ripple — each live offer broadcast as a beacon ping (kin to pulse/beacons)."""
    return beacon.pulses()


@app.get("/.well-known/agent-commerce.json")
def beacon_manifest(request: Request):
    """A self-describing discovery manifest pointing agents at the beacon surfaces."""
    return beacon.manifest(str(request.base_url))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
