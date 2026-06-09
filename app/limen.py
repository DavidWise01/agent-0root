"""
LIMEN decoder for agent-0root — self-contained, deterministic.

Parses a LIMEN line (witnessed gate-crossings, carried on PULSE) into reconstructed
crossings, each rendered across registers: glyph · direction · gate · witness ·
voice (Hz) · bits · gloss. Pure function — same line → same output (+ a trace hash).

Canonical reference: github.com/DavidWise01/pulse (limen/limen.py). Ported here so the
endpoint has no external dependency.
"""
import re
import json
import hashlib

CARRIER_BITS = "111011010000"   # the 3-2-1-0 carrier (music, fixed; not data)

GATES = {
    "stile":  {"glyph": "◐", "id": 0x1, "frm": "observe", "to": "act",      "gate": "64.5",  "tone": 262},
    "airgap": {"glyph": "⊘", "id": 0x2, "frm": "TOPH",    "to": "Patricia", "gate": "128.5", "tone": 330},
    "veil":   {"glyph": "◑", "id": 0x3, "frm": "compute", "to": "product",  "gate": "192.5", "tone": 392},
    "close":  {"glyph": "⟳", "id": 0x4, "frm": "wrap",    "to": "closure",  "gate": "256.5", "tone": 523},
    "gap":    {"glyph": "◇", "id": 0x5, "frm": "forward", "to": "inverse",  "gate": "64/65", "tone": 294},
}
DIRS = {"rise": {"glyph": "↑", "bit": 1, "law": "0→1 TOPH"},
        "fall": {"glyph": "↓", "bit": 0, "law": "1→0 Patricia"}}
_G2GATE = {g["glyph"]: n for n, g in GATES.items()}
_G2DIR = {d["glyph"]: n for n, d in DIRS.items()}
_TOK = re.compile(r"([↑↓])([◐⊘◑⟳◇])«([^»]*)»")


def _unesc(w): return re.sub(r"%([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), w)
def _esc(w):
    return "".join("%%%02X" % ord(c) if (c == "%" or c == "»" or c.isspace()) else c for c in w)


def encode_word(direction: str, gate: str, witness: str) -> str:
    return f"{DIRS[direction]['glyph']}{GATES[gate]['glyph']}«{_esc(witness)}»"

def encode_line(words) -> str:
    return " ".join(encode_word(d, g, w) for d, g, w in words)


def _voice(direction, gate):
    base = GATES[gate]["tone"]
    semis = [0, 2, 4] if direction == "rise" else [4, 2, 0]
    return [round(base * (2 ** (s / 12)), 2) for s in semis]

def _bits(direction, gate):
    return f"{CARRIER_BITS}·{GATES[gate]['id']:04b}·{DIRS[direction]['bit']}·1"

def _gloss(direction, gate, witness):
    g = GATES[gate]
    return f"«{witness}» witnesses the {direction} through the {g['frm']}→{g['to']} {gate} gate ({g['gate']})"


def decode_line(line) -> dict:
    """Deterministically parse a LIMEN line into reconstructed crossings."""
    if not isinstance(line, str):
        line = str(line)
    crossings = []
    for dglyph, gglyph, wit in _TOK.findall(line):
        direction, gate, witness = _G2DIR[dglyph], _G2GATE[gglyph], _unesc(wit)
        crossings.append({
            "glyph": f"{dglyph}{gglyph}«{wit}»",
            "direction": direction,
            "gate": gate,
            "witness": witness,
            "boundary": f"{GATES[gate]['frm']}→{GATES[gate]['to']}",
            "voice_hz": _voice(direction, gate),
            "bits": _bits(direction, gate),
            "gloss": _gloss(direction, gate, witness),
        })
    out = {"input": line, "count": len(crossings), "crossings": crossings, "carrier": CARRIER_BITS}
    canonical = json.dumps({"input": line, "crossings": crossings},
                           sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    out["trace"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    out["deterministic"] = True
    return out


EXAMPLE = "↑◐«truth» ↓⊘«mirror» ↑◇«question» ↓⟳«rest»"

def reference() -> dict:
    """The LIMEN vocabulary, for discovery (GET /v1/limen with no line)."""
    return {
        "usage": "POST {\"line\":\"↑◐«truth» …\"} or GET ?line=… — parse a LIMEN line into reconstructed crossings",
        "word": "<direction><gate>«witness»",
        "directions": {DIRS[d]["glyph"]: f"{d} ({DIRS[d]['law']})" for d in DIRS},
        "gates": {n: {"glyph": g["glyph"], "boundary": f"{g['frm']}→{g['to']}",
                      "gate": g["gate"], "tone_hz": g["tone"]} for n, g in GATES.items()},
        "example": EXAMPLE,
        "example_decoded": decode_line(EXAMPLE),
    }
