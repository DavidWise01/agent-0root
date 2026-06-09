"""Determinism + round-trip tests for the /v1/limen decoder (imports only app.limen)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.limen import decode_line, encode_line, exchange_line, EXAMPLE  # noqa: E402


def test_exchange_clean_is_intact():
    line = encode_line([("rise", "stile", "truth"), ("fall", "airgap", "mirror")])
    r = exchange_line(line)
    assert r["intact"] is True and r["deterministic"] is True
    assert all(x["checksum_ok"] for x in r["received"])
    assert r["received"][0]["heard"]["gate"] == "stile"


def test_exchange_tamper_is_caught():
    line = encode_line([("rise", "stile", "truth")])           # sent as stile (262 Hz)
    r = exchange_line(line, voice=[[523.0, 587.0, 659.0]])     # but heard as 'close' (523 Hz)
    assert r["received"][0]["checksum_ok"] is False            # voice ≠ glyph → caught
    assert r["intact"] is False


def test_exchange_determinism():
    line = encode_line([("rise", "gap", "q")])
    assert exchange_line(line) == exchange_line(line)


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
