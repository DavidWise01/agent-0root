"""
agent-0root · the deterministic core.

A pure function: same input -> same output, always. No randomness, no clock, no
network, no LLM. The only external input is VERSION (the deployed commit), which is
fixed for a given deployment — so a response is reproducible byte-for-byte and
verifiable: re-run the same input on the same commit and you get the same `trace`.

This is the honest boundary of "deterministic": it holds because nothing here is a
black box. Add an LLM call to a handler and that handler stops being deterministic —
keep those, if any, behind a clearly-marked, non-deterministic route.
"""
import os
import hashlib
import json

# the deployed commit. Railway injects RAILWAY_GIT_COMMIT_SHA automatically; GIT_SHA
# is a manual fallback. "dev" when run locally without a build stamp.
VERSION = (os.getenv("RAILWAY_GIT_COMMIT_SHA")
           or os.getenv("GIT_SHA")
           or "dev")[:12]

COMMANDS = ("help", "status", "version", "resolve", "echo <text>")


def _reply(text: str) -> str:
    low = text.lower().strip()
    if low in ("", "help"):
        return "0root.ai deterministic agent. commands: " + " · ".join(COMMANDS)
    if low == "status":
        return "operational · deterministic · verifiable · no black box"
    if low == "version":
        return f"agent-0root @ {VERSION}"
    if low == "resolve":
        return "9.9.9.9 = 1 — every query resolves to one root"
    if low.startswith("echo "):
        return text.strip()[5:]
    return f"echo: {text.strip()}"


def handle(user_input: str) -> dict:
    """Deterministic request handler. Returns a dict including a `trace` SHA-256
    (16 hex) over the (input, reply, version) — the response's self-proof."""
    if not isinstance(user_input, str):
        user_input = str(user_input)
    reply = _reply(user_input)
    payload = {"input": user_input, "reply": reply, "version": VERSION}
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    payload["trace"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    payload["deterministic"] = True
    return payload
