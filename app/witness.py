"""
WITNESS TUNNEL LEARNER — the reciprocal loop's brain, ported to FastAPI.

A faithful Python port of witness-server.js (Claude D1's spec). It does NOT read
any sensor: it learns the TRAFFIC of the tunnel itself — request timing, header
fingerprint, and the OUTCOMES of the phone's own capability probes as the phone
reports them up. It classifies WHY each gate answered, from timing alone:

    granted                -> LIT
    fast refusal  (<60ms)  -> POLICY wall   (sandbox / iOS policy denied it)
    slow refusal  (>=60ms) -> USER declined (a human tapped no)

Every observation is sealed into a SHA-256 hash chain. The reciprocal part: the
phone POSTs each event to /observe; the server folds it into the model and pushes
the updated model to every connected phone via SSE (/stream). Single-worker,
in-memory (resets on redeploy) — the model is the *live* tunnel, not a database.
"""
import time
import json
import math
import hashlib
import asyncio

# ---------- the learned model of the tunnel ----------
_model = {
    "started": time.time(),
    "observations": 0,
    "kinds": {},          # kind -> Welford {n, mean, M2, last, min, max}
    "caps": {},           # cap  -> {granted, refused, refuseMs{...}, verdict}
    "fingerprint": {},    # header -> {value, count}
    "lastReqAt": 0.0,
    "arrival": {"n": 0, "mean": 0.0, "M2": 0.0},
    "chainHead": "tunnel00000000",
    "chainLen": 0,
}

# SSE client queues (the down-channel)
_clients = set()

# the sealed chain itself — every link kept so the phone can RE-VERIFY it in-browser.
# Each link stores the exact canonical input string that was hashed, so the client can
# recompute sha256(prev + "|" + input)[:12] and confirm it equals seal. Bounded (the
# model is a live tunnel that resets on redeploy, not a database).
_chain = []
_CHAIN_MAX = 500


def _welford(s, x):
    s["n"] = s.get("n", 0) + 1
    d = x - s.get("mean", 0.0)
    s["mean"] = s.get("mean", 0.0) + d / s["n"]
    s["M2"] = s.get("M2", 0.0) + d * (x - s["mean"])
    s["last"] = x
    s["min"] = x if s.get("min") is None else min(s["min"], x)
    s["max"] = x if s.get("max") is None else max(s["max"], x)
    return s


def _sd(s):
    return math.sqrt(s["M2"] / (s["n"] - 1)) if s.get("n", 0) > 1 else 0.0


def _seal(payload):
    inp = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    prev = _model["chainHead"]
    h = hashlib.sha256((prev + "|" + inp).encode("utf-8")).hexdigest()[:12]
    _model["chainHead"] = h
    _model["chainLen"] += 1
    _chain.append({"seq": _model["chainLen"], "prev": prev, "input": inp, "seal": h})
    if len(_chain) > _CHAIN_MAX:
        del _chain[0:len(_chain) - _CHAIN_MAX]
    return h


def chain_dump(limit: int = 500) -> dict:
    """The ordered sealed links, so the phone can recompute each SHA-256 and prove the
    chain is intact in-browser. Returns at most the last `limit` links (bounded memory);
    the client verifies internal linkage + that the final seal equals the live head."""
    links = _chain[-limit:] if limit else list(_chain)
    return {
        "genesis": "tunnel00000000",
        "head": _model["chainHead"],
        "len": _model["chainLen"],
        "returned": len(links),
        "truncated": len(links) < _model["chainLen"],
        "links": links,
    }


def learn(ev: dict) -> str:
    """Fold one phone-reported observation into the model; return its chain seal."""
    if not isinstance(ev, dict):
        ev = {}
    _model["observations"] += 1
    now = time.time() * 1000.0  # ms

    # request-arrival rhythm (server-side timing of the tunnel)
    if _model["lastReqAt"]:
        _welford(_model["arrival"], now - _model["lastReqAt"])
    _model["lastReqAt"] = now

    # generic numeric event -> per-kind running stats
    kind = ev.get("kind")
    val = ev.get("value")
    if kind and isinstance(val, (int, float)) and not isinstance(val, bool):
        _model["kinds"].setdefault(kind, {})
        _welford(_model["kinds"][kind], float(val))

    # capability probe outcome — the sensor-gate mapping learned from timing
    cap = ev.get("cap")
    if cap:
        c = _model["caps"].setdefault(cap, {"granted": 0, "refused": 0,
                                            "refuseMs": {"n": 0, "mean": 0.0, "M2": 0.0}})
        outcome = ev.get("outcome")
        if outcome == "granted":
            c["granted"] += 1
        elif outcome == "refused":
            c["refused"] += 1
            ms = ev.get("ms")
            if isinstance(ms, (int, float)) and not isinstance(ms, bool):
                _welford(c["refuseMs"], float(ms))
        avg = c["refuseMs"].get("mean", 0.0) or 0.0
        if c["granted"] > 0:
            c["verdict"] = "LIT granted"
        elif c["refused"] > 0 and 0 < avg < 60:
            c["verdict"] = "POLICY wall (%dms)" % round(avg)
        elif c["refused"] > 0 and avg >= 60:
            c["verdict"] = "USER declined (%dms)" % round(avg)
        elif c["refused"] > 0:
            c["verdict"] = "refused (timing unknown)"

    return _seal(ev)


def fingerprint(headers) -> None:
    """Fingerprint the tunnel from each request's own headers (never sensor data)."""
    for h in ["user-agent", "accept-language", "sec-ch-ua", "sec-ch-ua-platform",
              "sec-ch-ua-mobile", "accept-encoding", "connection"]:
        v = headers.get(h)
        if v:
            fp = _model["fingerprint"].setdefault(h, {"count": 0})
            fp["value"] = str(v)[:80]
            fp["count"] += 1


def snapshot() -> dict:
    """The model streamed back down — what the server has LEARNED about the tunnel."""
    kinds = {}
    for k, s in _model["kinds"].items():
        kinds[k] = {"n": s.get("n", 0), "mean": round(s.get("mean", 0.0), 3),
                    "sd": round(_sd(s), 3), "min": s.get("min"),
                    "max": s.get("max"), "last": s.get("last")}
    return {
        "uptime_s": int(time.time() - _model["started"]),
        "observations": _model["observations"],
        "arrival_ms": {"mean": round(_model["arrival"].get("mean", 0.0), 1),
                       "sd": round(_sd(_model["arrival"]), 1), "n": _model["arrival"].get("n", 0)},
        "kinds": kinds,
        "caps": _model["caps"],
        "fingerprint": _model["fingerprint"],
        "chain": {"head": _model["chainHead"], "len": _model["chainLen"]},
    }


async def broadcast() -> None:
    """Push the updated model to every connected phone (SSE down-channel)."""
    data = "data: " + json.dumps(snapshot()) + "\n\n"
    for q in list(_clients):
        try:
            q.put_nowait(data)
        except Exception:
            _clients.discard(q)
