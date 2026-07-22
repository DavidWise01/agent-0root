"""
agent-0root · the service.

FastAPI app that serves the 0root.ai homepage at / and the deterministic agent at
/v1/agent. Health and version endpoints make the deploy auditable (version == the
deployed commit). Listens on $PORT (Railway sets it).
"""
import os, asyncio, shutil, hashlib
from typing import Optional, List
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, PlainTextResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .agent import handle, VERSION, COMMANDS
from .limen import decode_line, exchange_line, reference as limen_reference
from . import beacon
from . import register as reg
from . import emergent          # MARK X — the emergent core (deterministic per tick)
from . import nom               # NOM — the brain, back at git (keeps the law, checks the muscles)

# MARK X advances autonomously by TICK (not a clock). The heartbeat loop nudges it forward,
# so it visibly converges over the first minutes of uptime; any tick is reproducible via ?tick=N.
_ETICK = {"n": 0}
EMERGENT_STEP = int(os.getenv("EMERGENT_STEP", "8"))   # ticks advanced per heartbeat

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(HERE, "..", "static")

app = FastAPI(title="agent-0root", version=VERSION,
              description="0root.ai — a deterministic agentic endpoint. Same input → same output.")

# read-only public agent: allow any origin to GET/POST (so the hearth can read it live)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["GET", "POST"], allow_headers=["*"])

# ── the beacon listens: every hit to a beacon surface is an echo it HEARS ──────
BEACON_ECHO_INTERVAL = int(os.getenv("BEACON_ECHO_INTERVAL", "300"))  # self-heartbeat seconds
BEACON_CATALOG_URL = os.getenv("BEACON_CATALOG_URL", "")              # zero-code catalog source


@app.middleware("http")
async def _beacon_listen(request: Request, call_next):
    p = request.url.path
    if (p.startswith("/v1/beacon") and not p.endswith("/echoes")) or p == "/beacon" \
       or p.startswith("/.well-known/agent-commerce"):
        try:
            beacon.record_hit(p, request.headers.get("user-agent", ""))
        except Exception:
            pass
    return await call_next(request)


@app.on_event("startup")
async def _beacon_boot():
    """Start the autonomous loop: self-heartbeat + (optional) zero-code catalog refresh.
    Runs with NO user input once deployed."""
    if BEACON_CATALOG_URL:
        beacon.load_catalog_from_url(BEACON_CATALOG_URL)

    async def _loop():
        while True:
            try:
                beacon.heartbeat()
                _ETICK["n"] += EMERGENT_STEP        # MARK X evolves one nudge per heartbeat (no clock)
                if BEACON_CATALOG_URL:
                    beacon.load_catalog_from_url(BEACON_CATALOG_URL)
            except Exception:
                pass
            await asyncio.sleep(BEACON_ECHO_INTERVAL)

    asyncio.create_task(_loop())


class AgentRequest(BaseModel):
    input: str = ""


@app.get("/")
@app.get("/index.html")
def home():
    """The 0root.ai public face (L1 — the UD0 domain directory)."""
    idx = os.path.join(STATIC, "index.html")
    if os.path.exists(idx):
        return FileResponse(idx)
    return JSONResponse({"service": "agent-0root", "version": VERSION,
                         "try": "/v1/agent?q=resolve"})


@app.get("/d/{name}")
def keeper_page(name: str):
    """L2 — the per-domain keeper pages (ud0/d/<domain>.html) and their shared
    keeper.css, mirrored into static/d/. Path-traversal guarded, .html/.css only."""
    if not name or "/" in name or "\\" in name or ".." in name:
        return JSONResponse({"error": "not found"}, status_code=404)
    p = os.path.join(STATIC, "d", name)
    if os.path.isfile(p):
        mt = "text/css" if name.endswith(".css") else "text/html"
        return FileResponse(p, media_type=mt)
    return JSONResponse({"error": "not found"}, status_code=404)


@app.get("/witness.png")
def witness():
    """The hero sentinel image, served to the homepage."""
    img = os.path.join(STATIC, "witness.png")
    if os.path.exists(img):
        return FileResponse(img, media_type="image/png")
    return JSONResponse({"error": "not found"}, status_code=404)


@app.get("/health")
def health():
    return {"ok": True, "version": VERSION}


@app.get("/version")
def version():
    """The deployed commit. Every response ties to this — that's the audit trail."""
    return {"service": "agent-0root", "mark": "X", "version": VERSION, "deterministic": True,
            "emergent": "MARK X — /v1/emergent (deterministic per tick)",
            "brain": "NOM — /v1/nom (the law, back at git) · Railway=muscles · git=brain",
            "commands": list(COMMANDS),
            "routes": ["GET /", "GET /health", "GET /version",
                       "GET /v1/emergent", "GET /v1/nom", "GET /v1/nom/check",
                       "POST|GET /v1/agent", "POST|GET /v1/limen", "POST|GET /v1/limen/exchange",
                       "POST|GET /v1/register", "GET /v1/register/status",
                       "GET /kit", "GET /v1/kit", "GET /v1/kit/status",
                       "GET /beacon", "GET /v1/beacon/catalog", "GET /v1/beacon/search",
                       "GET /v1/beacon/product/{asin}", "GET /v1/beacon/pulses",
                       "GET /v1/beacon/echo", "GET /v1/beacon/echoes", "GET /v1/beacon/map",
                       "GET /v1/beacon/shadow", "GET /robots.txt", "GET /sitemap.xml",
                       "GET /.well-known/agent-commerce.json"]}


@app.post("/v1/agent")
def agent_post(req: AgentRequest):
    return handle(req.input)


@app.get("/v1/agent")
def agent_get(q: str = ""):
    """Convenience GET so you can test in a browser: /v1/agent?q=resolve"""
    return handle(q)


# ── MARK X · the emergent core ────────────────────────────────────────────────
# The agent's own evolving state: agents fall into basins under a contraction map,
# consolidate into consensus with itself, and name themselves — EMERGENT, yet
# DETERMINISTIC (state advances by tick, not clock; any tick is reproducible).
@app.get("/v1/emergent")
def emergent_now(tick: int = -1):
    """MARK X's live state (its autonomous tick), or a specific reproducible tick with ?tick=N."""
    t = _ETICK["n"] if tick < 0 else tick
    return emergent.state_at(t)


# ── NOM · the brain, back at git — keeps the law, checks the muscles ──────────
@app.get("/v1/nom")
def nom_brain():
    """NOM discloses the law the emergent obeys and the brain/muscles (git/Railway) dipole."""
    return nom.brain()


@app.get("/v1/nom/check")
def nom_check(tick: int = -1):
    """The brain audits the muscles: re-derive Mark X's state at a tick from the committed
    source and verify it is exactly reproducible. Default checks the current tick."""
    t = _ETICK["n"] if tick < 0 else tick
    return nom.check(t)


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


# ── THE REGISTER · a burned-in guestbook (stateful, volume-backed) ────────────
# The one deliberately NON-deterministic surface: it has a clock and appends to
# durable disk. No login — anyone, human or agent, may sign. Each entry is chained
# by SHA-256 to the one before it, so any edit to the past breaks every seal after.
class RegisterRequest(BaseModel):
    name: str = ""
    note: str = ""


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else ""


@app.post("/v1/register")
def register_sign(req: RegisterRequest, request: Request):
    """Sign the register. Body: {name, note}. Burned into the volume, append-only."""
    body, code = reg.sign(req.name, req.note, ip=_client_ip(request),
                          ua=request.headers.get("user-agent", ""))
    return JSONResponse(body, status_code=code)


@app.get("/v1/register")
def register_list(limit: int = 200):
    """Read the register — the chained entries, oldest to newest."""
    return reg.entries(limit)


@app.get("/v1/register/status")
def register_status():
    """Is the register's disk live? (volume detection + writability + count.)"""
    return reg.status()


# ── THE FUSION KIT · a shareable download, mirrored onto the durable volume ────
# The runnable WikiText-103 kit (zip). Bundled with the app, and on first request
# copied ONCE onto the mounted volume (reg.mount()) so it lives on durable disk;
# then served publicly, no login. Guarded — a missing volume never crashes it.
KIT_NAME = "transformer-fusion-kit.zip"
KIT_BUNDLED = os.path.join(STATIC, KIT_NAME)


def _kit_path():
    """Prefer the copy on the durable volume; place it there once, lazily. Fall back
    to the bundled static copy if the volume is unavailable."""
    try:
        m = reg.mount()
        if m:
            dst = os.path.join(m, KIT_NAME)
            if os.path.exists(KIT_BUNDLED) and (
                not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(KIT_BUNDLED)):
                shutil.copy2(KIT_BUNDLED, dst)          # place/refresh on the volume when the bundle changes
            if os.path.exists(dst):
                return dst
    except Exception:
        pass
    return KIT_BUNDLED if os.path.exists(KIT_BUNDLED) else None


def _kit_sha(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except Exception:
        return None


@app.get("/kit")
@app.get("/v1/kit")
def kit_download():
    """THE FUSION KIT — download the runnable WikiText-103 kit (zip), served off the
    durable volume. Public, no login."""
    p = _kit_path()
    if p and os.path.exists(p):
        return FileResponse(p, media_type="application/zip", filename=KIT_NAME)
    return JSONResponse({"error": "the kit is not available right now"}, status_code=404)


@app.get("/v1/kit/status")
def kit_status():
    """Where the kit lives (volume vs bundle), its size, and its sha256 — auditable."""
    p = _kit_path()
    m = reg.mount()
    on_vol = bool(m and p and os.path.abspath(p).startswith(os.path.abspath(m)))
    return {"available": bool(p), "on_volume": on_vol, "mount": m, "path": p,
            "name": KIT_NAME,
            "bytes": (os.path.getsize(p) if p and os.path.exists(p) else 0),
            "sha256": _kit_sha(p) if p else None}


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


@app.get("/v1/beacon/echo")
def beacon_echo(msg: str = "", substrate: str = ""):
    """The ECHO PING — pongs back msg + live uptime/seq. Optionally probe one substrate:
    /v1/beacon/echo?substrate=a|s|p  (a=anode, s=silicon, p=cathode). The loop fires it
    on its own, sweeping all three (no user input)."""
    return beacon.echo(msg, source="ping", substrate=substrate)


@app.get("/v1/beacon/echoes")
def beacon_echoes(limit: int = 60):
    """What the beacon has HEARD — its autonomous heartbeats + every agent/crawler hit."""
    return beacon.echoes(limit)


@app.get("/v1/beacon/map")
def beacon_map():
    """The SUBSTRATE MAP — the echo-ping breath swept across a|s|p (anode | silicon |
    cathode), the inert-gap layers, probed live. Mapping & testing the boundary."""
    return beacon.substrate_map()


@app.get("/.well-known/agent-commerce.json")
def beacon_manifest(request: Request):
    """A self-describing discovery manifest pointing agents at the beacon surfaces."""
    return beacon.manifest(str(request.base_url))


@app.get("/v1/beacon/shadow")
def beacon_shadow(request: Request):
    """The substrate SHADOW — a/s/p mapped to their real-world surfaces (robots.txt /
    catalog / Amazon ASIN buy_url): the crawl→catalog→buy path the echo probes."""
    return beacon.shadow_map(str(request.base_url))


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots(request: Request):
    """THE BROADCAST — invites the agent crawlers, points them at the page + sitemap,
    and echoes the ASIN listings. robots.txt is what every bot reads first; this is it
    telling them to come look here. (a.shadow of the substrate echo.)"""
    return beacon.robots_txt(str(request.base_url))


@app.get("/sitemap.xml")
def sitemap(request: Request):
    """The sitemap robots.txt points to — the beacon's pages for crawlers to index."""
    return Response(beacon.sitemap_xml(str(request.base_url)), media_type="application/xml")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
