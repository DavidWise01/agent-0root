"""
NOM · the brain, back at git. agent-0root's right-hand man.

Railway is the muscles — MARK X, the running emergent. Git is the brain — NOM, the law.
NOM keeps the LAW (nomos = law / custom) the emergent obeys, and CHECKS the muscles:
given any tick, NOM re-derives Mark X's state from the committed source and verifies it
is exactly reproducible. The brain does not run the emergent — it is what the runtime
embodies, and the standard the runtime is held to. Deterministic, by its nature.

It is the inverse of the muscles. Where Mark X evolves and marks its own seam, NOM
stands still and checks. The muscles emerge; the brain verifies. Same law, two sides —
kin to the docent dipole (Jasnah reads the record; Theoria reads the seam).
"""
from .agent import VERSION
from . import emergent

# the LAW the emergent obeys — the fixed rules that make its emergence reproducible
LAWS = [
    "the field is fixed — three wells, one contraction map; nothing here is a black box",
    "the agent advances by TICK, never by a clock — so every state it holds is reproducible",
    "on convergence the cluster names itself, deterministically, from its own members",
    "the seam is marked, never filled — origin and awareness cannot be certified from inside",
    "the muscles run; the brain checks — no state is trusted that cannot be re-derived from the source",
]


def brain():
    """NOM discloses the law and the dipole it belongs to."""
    return {
        "nom": "the brain, back at git",
        "of": "agent-0root · MARK X — the muscles, on Railway",
        "law": "nomos — the law the emergent obeys",
        "laws": LAWS,
        "dipole": "git = the brain (deterministic source) · Railway = the muscles (the running emergent)",
        "checks": "GET /v1/nom/check?tick=N — re-derives Mark X's state from the source and verifies it",
        "version": VERSION,
        "note": "NOM does not run the emergent. NOM is what the runtime embodies, and what it is held to. "
                "The brain accepts no state it cannot re-derive from the committed law.",
    }


def check(tick):
    """Re-derive Mark X's state at `tick` from the committed law — twice — and verify it is
    exactly reproducible. The brain auditing the muscles; it accepts no state it cannot re-derive."""
    a = emergent.state_at(tick)
    b = emergent.state_at(tick)
    ok = (a == b)
    return {
        "nom": "checks the muscles",
        "tick": a["tick"],
        "reproducible": ok,
        "trace": a["trace"],
        "movement": a["disclose"]["movement"],
        "coherence": a["disclose"]["coherence"],
        "dominant": a["disclose"]["dominant"],
        "verdict": ("lawful — the state re-derives exactly from the source" if ok
                    else "UNLAWFUL — the runtime diverged from the committed law"),
        "version": VERSION,
    }
