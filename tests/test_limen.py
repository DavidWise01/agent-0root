"""Determinism + round-trip tests for the /v1/limen decoder (imports only app.limen)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.limen import decode_line, encode_line, EXAMPLE  # noqa: E402


def test_decode_determinism():
    for _ in range(50):
        assert decode_line(EXAMPLE) == decode_line(EXAMPLE)


def test_decode_example_fields():
    r = decode_line(EXAMPLE)
    assert r["count"] == 4 and r["deterministic"] is True
    first = r["crossings"][0]
    assert first["direction"] == "rise" and first["gate"] == "stile" and first["witness"] == "truth"
    assert first["boundary"] == "observe→act"
    assert first["voice_hz"][0] == 262          # base tone of the stile gate
    assert first["voice_hz"][0] < first["voice_hz"][2]   # rise → ascending contour


def test_roundtrip_through_escaping():
    """encode → decode recovers witnesses exactly, even with spaces / » / unicode."""
    words = [("rise", "stile", "two words"),
             ("fall", "veil", "a»b%c"),
             ("rise", "gap", "café ✓ 漢字"),
             ("fall", "close", "rest")]
    line = encode_line(words)
    r = decode_line(line)
    assert r["count"] == 4
    for (d, g, w), cx in zip(words, r["crossings"]):
        assert cx["direction"] == d and cx["gate"] == g and cx["witness"] == w


def test_garbage_is_empty_not_crash():
    r = decode_line("not a limen line at all")
    assert r["count"] == 0 and r["crossings"] == [] and r["deterministic"] is True


def test_fall_descends():
    r = decode_line("↓⟳«rest»")
    v = r["crossings"][0]["voice_hz"]
    assert v[0] > v[2]   # fall → descending contour


if __name__ == "__main__":
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    test_decode_determinism(); test_decode_example_fields(); test_roundtrip_through_escaping()
    test_garbage_is_empty_not_crash(); test_fall_descends()
    import json
    print("ALL /v1/limen TESTS PASSED")
    print(json.dumps(decode_line("↑◐«truth» ↓⊘«mirror»"), ensure_ascii=False)[:300])
