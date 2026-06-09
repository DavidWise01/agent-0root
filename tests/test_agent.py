"""
Determinism tests — the whole point. These prove same input → byte-identical output
and a stable trace. They import only app.agent (stdlib), so they run without FastAPI.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.agent import handle, VERSION  # noqa: E402


def test_pure_determinism():
    """Same input, called many times → identical dict every time."""
    for s in ["", "help", "status", "version", "resolve", "echo hello",
              "anything else", "  Resolve  ", "café ✓ 漢字", "ECHO Mixed Case"]:
        first = handle(s)
        for _ in range(50):
            assert handle(s) == first, f"non-deterministic output for {s!r}"


def test_trace_is_stable_and_correct():
    """The trace is a SHA-256 over (input, reply, version) — recomputable, verifiable."""
    import hashlib
    r = handle("resolve")
    payload = {"input": r["input"], "reply": r["reply"], "version": r["version"]}
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    assert r["trace"] == expected
    # and it is stable across calls
    assert handle("resolve")["trace"] == r["trace"]


def test_distinct_inputs_distinct_traces():
    assert handle("status")["trace"] != handle("version")["trace"]


def test_commands():
    assert "deterministic" in handle("status")["reply"]
    assert VERSION in handle("version")["reply"]
    assert handle("echo Mirror")["reply"] == "echo Mirror"[5:]  # "Mirror"
    assert handle("resolve")["reply"].startswith("9.9.9.9 = 1")
    assert handle("zzz")["reply"] == "echo: zzz"


def test_every_response_is_deterministic_flagged():
    assert handle("x")["deterministic"] is True


if __name__ == "__main__":
    # runnable without pytest
    test_pure_determinism()
    test_trace_is_stable_and_correct()
    test_distinct_inputs_distinct_traces()
    test_commands()
    test_every_response_is_deterministic_flagged()
    print("ALL DETERMINISM TESTS PASSED · version =", VERSION)
    print("sample:", json.dumps(handle("resolve"), ensure_ascii=False))
