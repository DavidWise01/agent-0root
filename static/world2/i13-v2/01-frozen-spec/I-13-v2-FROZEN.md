# I-13 · v2.0 · FROZEN SPECIFICATION

    frozen      2026-08-01
    sha256      64881ebf502b87bb450f1f39b71066013e0c31a7f78dedcae326f6155ddc6bf8
    supersedes  v1.0 · 074733e1d7de4f2c4df89c3ccf82f128...

A four-plane agent stack over a thirteen-symbol language, where two planes learn, two do not, and five parameter-free rules hold what no model at this scale holds.

---

## 1 · WHAT CHANGED FROM v1.0

### CORRECTION 18 — the tower is FOUR planes, not seven

**Evidence.** two-proportion tests on the leaf fraction: L5 vs L6 p=0.5407, L5 vs L7 p=0.9362, L6 vs L7 p=0.7403, and L4 vs L5 p=0.0795. separating L6 from L5 at the observed 2.99 points needs 1,426 nodes; L6 has 73 and L7 has 17.

**Action.** L5, L6 and L7 deleted. L4 absorbs them: 6,662 nodes, 7,143 chars, one cortex, error 0.97+/-0.45 pts, KS 0.0490 < 0.0729, five seeds.

### CORRECTION 19 — the RISC-13 spill path was silently wrong from arity 8

**Evidence.** forced spill at 8 arguments returned 28[object Object] instead of 36; every spilled argument reloaded into R-1, so only the last survived, and CALL then read past an 8-slot register file.

**Action.** replaced with a calling convention: up to R-1 args in registers, the rest in named memory slots with a fetch flag on CALL. verified arity 4 to 45, no regression. the generic spill in ex() was deleted as unfixable in principle.

### ARCHITECTURE — (c(sa())) — the cortex became a SENSOR as well as a governor

**Evidence.** feeding the cortex's own state back as input features: L2 mismatch 15.0+/-2.1 -> 0.6+/-0.8 with no correction running; L1 stray-close 65.0 -> 1.0. six floats at L2, five at L1.

**Action.** locked into both trained planes. the cortex still verifies at the end: a feature is advice, a veto is a wall.

### BASELINE CONTROL — BASELINE CONTROL run — the missing number from v1

**Evidence.** GRU 16,936 params: 0.8440 bits, 79.6% brackets, 33.8 mismatch, 16.6/40 clean. transformer 14,944 params: 0.9299 bits, 78.0%, 65.6 mismatch, 7.8/40. locked sa+cortex 18,921 params: 0.9118 bits, 80.6%, 0.0 mismatch, 40.0/40.

**Action.** the GRU BEATS the sub-agent on prediction and produces 2.3x the mismatched closers. learned recurrent state is not a stack. the cortex is orthogonal to model quality, not a substitute for it.

---

## 2 · THE TOWER

| plane | name | nodes | bits | kind | alphabet |
|---|---|---|---|---|---|
| **L1** | FIELD | 395,162 | 19 | trained | 30 |
| **L2** | SUBAGENT HOST | 209,068 | 18 | trained | 66 |
| **L3** | COMPOSE | 38,742 | 16 | rewrite | — |
| **L4** | DEEP OPERAND | 6,662 | 13 | cortex-only | 18 |

### L1 · FIELD

    metric    1.6628 bits vs bigram 2.1784 - 60.4% - run-length KS 0.0099 < 0.0266
    (c(sa())) 5 features: depth, open, terminator, header, run
    rules     veto · -I · depth · idempotence · address · run-pressure a=0.3

**Verified.** 5 seeds x 20 samples. stray-close 65.0 -> 1.0 with features. unclosed 91.6 -> 0.0 with -I ONLY: a sensor tells you where you are, a discharge brings you back.

### L2 · SUBAGENT HOST

    metric    18,921 params - 0.9118 bits - 80.6% brackets - 98.90% of all lines
    (c(sa())) 6 features: depth, owed x4, run
    rules     veto · -I · depth · idempotence · address · indent cap 16

**Verified.** 40/40 clean, 5 seeds, ZERO VARIANCE. 9 languages 1957-2017, 529 unclosed to 0.

### L3 · COMPOSE

    metric    three-address transform - 0 parameters - no model
    rules     depth n -> 1

**Verified.** 200 generated programs: correctness 200/200, termination 200/200 (stress-tested to depth 20), idempotence 200/200 (fixpoint in ONE pass), validation 200/200. cost +37.6% statements, +16.8% steps.

### L4 · DEEP OPERAND

    metric    7,143 chars = 0.48x crossover - NO MODEL - n-gram turns around at order 3
    rules     veto · -I · depth(2)

**Verified.** absorbs former L5/L6/L7. leaf 78.24%, reach 15.77%, container 5.99%. error 0.97+/-0.45 pts, mismatch 0.0, unclosed 0.0, KS 0.0490 < 0.0729, five seeds. 0 params beat a 15,089-param model by 10x on proportions.

---

## 3 · THE FIVE RULES

| # | rule | holds | params |
|---|---|---|---|
| 1 | **veto** — forbid the wrong closer | a stack | 0 |
| 2 | **-I** — supply the owed closer | a debt across a sequence | 0 |
| 3 | **depth** — refuse a plane already paid for | a nesting level | 0 |
| 4 | **idempotence** — a no-op cannot repeat | an identity: I am I | 0 |
| 5 | **address** — the substrate writes the position | a counter | 0 |

### Reach per plane, per 1,000 nodes

| rule | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| veto | 137.5 | 52.4 | 56.2 | 53.4 |
| −I | 137.5 | 52.4 | 56.2 | 53.4 |
| depth | 168.5 | 212.5 | 182.1 | 187.1 |
| idempotence | 59.0 | **0.0** | **0.0** | **0.0** |
| address | 168.5 | **0.0** | **0.0** | **0.0** |

per 1,000 nodes. idempotence and address are 0.0 above L1 because there are no statements inside an expression.

---

## 4 · THE TWELVE

Counted over 649,634 AST nodes across 504 stdlib files. Not designed — ranked and cut at 83.27% coverage. Attributed to first formal appearance.

| # | operant | year | attributed | share |
|---|---|---|---|---|
| 1 | `NAME` | 1843 | Lovelace | 29.67% |
| 2 | `CONSTANT` | 1843 | Lovelace | 14.25% |
| 3 | `ATTRIBUTE` | 1966 | Hoare | 9.63% |
| 4 | `CALL` | 1936 | Church | 7.50% |
| 5 | `ASSIGN` | 1843 | Lovelace | 5.23% |
| 6 | `ARG` | 1879 | Frege | 4.08% |
| 7 | `EXPR` | 1957 | Backus | 3.01% |
| 8 | `IF` | 1843 | Lovelace | 2.76% |
| 9 | `COMPARE` | 1843 | Lovelace | 2.01% |
| 10 | `FUNCTIONDEF` | 1936 | Church | 1.92% |
| 11 | `RETURN` | 1949 | Wheeler | 1.82% |
| 12 | `BINOP` | 1843 | Lovelace | 1.38% |

Six are Lovelace's. Her notes were buried from 1843 to 1953, so nothing downstream read them — the overlap with modern code is convergence, not descent.

---

## 5 · THE MACHINE

    ISA        IVM-13-S · 17 opcodes
    law        net = binds - k
    validate   one linear pass per region, no execution, no control-flow graph
    jit        2.1x over the tree-walking interpreter

**Components.** lexer · parser (DERIVED from containment, provably identical) · compiler · assembler · disassembler · validator · IVM-13 stack · IVM-13-S structured · RISC-13 register R=8 arity 1-45 · JIT

**Verified.** B1 B2 B4 B6 exact on interpreter, stack VM, register machine, and JIT. no unverified component remains.

---

## 6 · THE FACTORY

    languages indexed   756
    families            17
    list coverage       86.1%
    identification      82.9% exact, 95.1% family
    corpora measured    32

**Quantile law.** quantile is PER-CORPUS: measure H(depth), read it off. <0.7->0.50, <1.0->0.90, else 0.99. always round UP on an unseen key.

---

## 7 · NOT BUILT

Deliberate absences. Each has a reason, and the reason is measured.

| what | status |
|---|---|
| **ORCHESTRATOR** | not derivable — a boundary, not a task |
| **VISUAL LANGUAGE FAMILY** | indexed so the factory REFUSES rather than guesses |
| **SCALE BEYOND ~17k PARAMETERS** | untested — the largest open question |
| **L6 / L7 AS PLANES** | deleted in v2, absorbed into L4 |

**ORCHESTRATOR.** 61% of naming information is not in the corpus in any form a counter reaches. structure explains 5.1% of the choice, arguments explain 64.2%, and the residual 2.033 bits is where meaning lives.

**VISUAL LANGUAGE FAMILY.** 4.7% of the Wikipedia list has no text form: Scratch, Simulink, Max, Grasshopper, Prograph, NXT-G, App Inventor. a language whose source is a picture has no I to collapse.

**SCALE BEYOND ~17k PARAMETERS.** every result here is at 17k params on one primary corpus. a 17M-parameter model may learn an exact stack, in which case the division of labour changes.

**L6 / L7 AS PLANES.** 73 and 17 nodes. statistically indistinguishable from L4 at p=0.92 and p=0.94.

---

## 8 · MEASURED DEAD

Sixteen things built, measured, and killed. Kept in the record because the
measurement is the useful part — each one cost real work and none of them
should be repeated.

**01 · SWITCHBOARD** — *routing (kind, #calls, #args) -> name*  
0.0% top-1 on real held-out functions. the aggregate 20.5% was carried by slots whose answer is 'self'.

**02 · 8 NAMED ATTENTION HEADS** — *prev-token, sink, same-char, class, delimiter, similarity, bigram, uniform*  
UNIFORM AVERAGING BEATS THEM: 0.9182 bits vs 0.9256. five of eight already had near-maximal entropy; the two that were sharp duplicated the one-hot features.

**03 · SEEDED CORPUS GENERATOR** — *600k synthetic tokens from a seed corpus*  
the pretraining gain was regularisation in disguise. once L2 and dropout were added it helped nothing.

**04 · WORD-BIGRAM FILTER** — *reject synthetic text with implausible adjacent pairs*  
+0.71 accuracy, noise level. the model already had that signal as an input feature.

**05 · LONG-RANGE COHERENCE GATE** — *JS divergence threshold on synthetic text*  
76% rejection for +0.2 perplexity and -0.14 accuracy. failed both metrics.

**06 · CONSTRAINED SAMPLING** — *bias -I fills toward the block centroid*  
both intrinsic statistics improved; downstream accuracy fell 0.67%.

**07 · CORPUS BLENDING** — *94k mixed-register words*  
lost to 29k pure by 17 perplexity units. register purity beats volume.

**08 · CLOSED-FORM READOUT** — *ridge solve instead of trained cross-entropy*  
0.86s, zero training, 73.8% top-1 — and 5.082 bits. unusable when sampled: no calibration, no sampling, diversity 1.000 on the generation test.

**09 · GREEDY DECODING** — *argmax instead of sampling*  
5-gram diversity 0.013. one 420-character line, never a newline.

**10 · WIDER WINDOW** — *CTX 26 and CTX 52*  
52 is WORSE than 13 (49.8% vs 52.9% on brackets). the window was never the bottleneck for prediction.

**11 · PATTERN IDEMPOTENCE** — *forbid a repeated k-statement block*  
would forbid 37.33% of real Python. real code repeats a 2-block a third of the time.

**12 · RUN-LENGTH HARD CAP** — *refuse a kind past N repeats*  
best cap improves KS by 42% and still differs. kills a genuine 0.23% tail to fix a 4.10% one. replaced by run PRESSURE a=0.3, which agrees at D=0.0099.

**13 · DENSITY METRIC** — *z-distance of construct densities from real code*  
shuffled characters scored 0.749 against real code's 0.996. distance-from-average rewards being suspiciously average.

**14 · BURSTINESS METRIC** — *within-sample density variation*  
AUC 0.33-0.43 — every condition including noise looked more real than real code.

**15 · 'CLEAN' AS A QUALITY METRIC** — *zero mismatched, zero unclosed*  
20/20 on pure noise. it measured the substrate, never the model. every 30/30 quoted across nine languages was a claim about the veto.

**16 · GENERIC REGISTER SPILL** — *evaluate into R-1 and park in memory*  
unfixable in principle: reloading every spilled value into one register loses all but the last. deleted, not repaired. the calling convention handles arity; nothing needs more than 8 registers for depth.

### The pattern across all sixteen

Twelve of the sixteen are the same failure: **a metric computed inside the
system improved, and nothing outside the system moved.** The word-bigram
filter, the coherence gate, constrained sampling, the density metric, the
burstiness metric, `clean` itself. Every time, the intrinsic number went the
right way and the held-out number did not follow.

The three interventions that *did* work were all corrections to something set
up early and never re-read: the loss weighting, the card columns, and the
attention block that turned out to be decorative.

---

## 9 · BOUNDARIES

Not tasks. Measured limits.

- naming: 61% of the information is not in the corpus. the orchestrator is not built and not derivable by counting.
- visual languages: 4.7% of the Wikipedia list has no text form. nothing for a 13-symbol window to see.
- closing: per-sequence, not per-step. no readout improvement reaches it, and neither does recurrent state - the GRU baseline proves it. -I is permanent.
- scale: every result is at ~17k parameters on one primary corpus. at 17M the division of labour may not hold.

---

## 10 · REPRODUCTION

**corpus.** Python 3.12 stdlib, 504 files, comments and string literals stripped, every identifier collapsed to I

**split.** 90/10 by position, no shuffling

**seeds.** 5 seeds minimum for any generation claim. single-seed comparisons caused three of the nineteen corrections.

**crossover.** ~15,000 tokens. below it a trained stack does not beat a bigram and no model should be placed.

---

## 11 · THE CLAIM, STATED NARROWLY

Deterministic components with **zero parameters** can guarantee structural properties that no model at this scale reaches — including models that beat them at prediction.

The baseline control is the evidence. A GRU at 16,936 parameters achieves **0.8440 bits** against the sub-agent's 0.9182 and **79.6% bracket accuracy** against 74.3% — and produces **33.8 mismatched closers** against 15.0, with **16.6/40** clean samples against 24.0. It has recurrent state. It predicts better. It generates worse.

Learned state is not a stack. It encodes what helps the next symbol, and a stack is a different object.

## 12 · WHAT THIS IS NOT

Not a code assistant. The sub-agent produces roughly 1.2 usable lines per 420 characters and cannot name anything, by construction — the I-collapse removes 61% of the information and naming is what it removes.

Nothing here beats an existing tool at its own job. ANTLR beats the derived parser. LLVM beats IVM-13-S. WASM shipped the validator and the veto at industrial scale in 2017. This build re-derived good ideas from measurement; it did not advance past them.

Every result is at ~17,000 parameters on one primary corpus. At 17 million the division of labour may not hold, and that is untested.

---

*19 corrections recorded. 16 approaches measured dead and kept. The last two deleted three of the author's own planes and repaired a compiler path that had been marked "written, never fired" while producing `28[object Object]` at arity 8.*
