# I-13 v2.0 — session archive

    frozen   2026-08-01
    sha256   64881ebf502b87bb450f1f39b71066013e0c31a7f78dedcae326f6155ddc6bf8

A four-plane agent stack over a thirteen-symbol language. Two planes learn,
two do not. Five parameter-free rules hold what no model at this scale holds.

Every HTML file is standalone and offline — no CDN, no network, no build step.
Open it in a browser.

---

## 01-frozen-spec

| file | what |
|---|---|
| `I-13-v2-FROZEN.md` | **start here.** 12 sections. the tower, the rules, the twelve, the machine, the factory, NOT BUILT, MEASURED DEAD, the claim stated narrowly, and what this is not. |
| `i13-stack-v2.json` | the same spec, machine-readable. this is what the sha256 covers. |
| `i13-frozen-v1.html` | v1.0, five windows: identity · contributors · 1D · 2D running · 3D. superseded, kept because it records what v2 corrected. |

## 02-the-stack

| file | what |
|---|---|
| `i13-two-scopes.html` | **the machine.** lex · parse · compile · assemble · validate · VM · JIT, all running in the page. press *inject a fault* — the validator catches it in one linear pass, no execution. |
| `i13-live-stack.html` | 18,249 trained parameters executing in JavaScript. turn the cortex **off** and watch it fail. |
| `i13-factory.html` | the twelve-station production line, colour-coded by provenance: amber built here, grey textbook. |
| `i13-language.html` | I-13 lexer, parser, compiler, VM. Bernoulli B₁ B₂ B₄ B₆ exact. |
| `cc-five-layers.html` | the layer assay. branching factor 0.154, not 2. |
| `machine-corpus-13.html` | the wheel: 12 operants as the central section of the 24-cell. |

## 03-the-factory

| file | what |
|---|---|
| `agent-factory.html` | **paste any source.** it names the language and emits a bootloader: plane, rules, pairs, quantile, and the trap that language actually sprang during the build. 82.9% exact, 95.1% family. |
| `factory-corpus-v1.json` | the selection table. 756 languages, 17 families, 86.1% of the Wikipedia list. |
| `pair-table.html` | six delimiter tables with their guards. the list was config; the guards were not. |
| `seven-languages.html` | 1957 → 2017, one pipeline. 529 unclosed → 0. |

## 04-hello-world

Real toolchains, installed and run. Not simulations.

| file | what |
|---|---|
| `rust-hello-i13.html` | `rustc 1.75.0`, 13 MB binary. `name survived the borrow` is the machine proving `&y` is `I.p`. |
| `go-hello-i13.html` | `go 1.22.2`. two `defer` statements discharging LIFO — `defer` is `−I`. |

## 05-corpora

`ab-corpus-v2.txt` — 288,705 words, Boole / Lovelace / Hinton, human first-person stripped.
sha256 `95ec55ba00ee2d8b082092725e359acbaf1d81904d8359312bb3c7dff8f9319f`

## 06-rust-source

677 lines. Builds with `rustc --edition 2021 -O src/main.rs -o i13`.
The comments carry the measurements, the attributions, and the bugs.

## 07-earlier-build

Prior sessions: Stott's polytope sections, the compendium, the provenance
tracer, the eve stack.

---

## the claim, stated narrowly

Deterministic zero-parameter components guarantee structural properties that
no model at this scale reaches.

A GRU at 16,936 parameters predicts **better** — 0.8440 bits against 0.9182,
79.6% bracket accuracy against 74.3% — and generates **2.3× worse**: 33.8
mismatched closers against 15.0. It has recurrent state.

**Learned state is not a stack.**

## what this is not

Not a code assistant. The sub-agent produces ~1.2 usable lines per 420
characters and cannot name anything, by construction.

Nothing here beats an existing tool at its own job. ANTLR beats the derived
parser. LLVM beats IVM-13-S. WASM shipped the validator and the veto at
industrial scale in 2017.

Every result is at ~17,000 parameters on one primary corpus. At 17 million the
division of labour may not hold, and that is untested.

## the record

21 corrections. 16 approaches measured dead and kept. 7 LIT axioms, 1 dead,
2 amber. The last two corrections deleted three of the author's own planes and
repaired a compiler path marked "written, never fired" that was producing
`28[object Object]` at arity 8.
