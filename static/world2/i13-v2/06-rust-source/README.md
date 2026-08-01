# I-13 v2.0 — the full stack, in Rust

    build   rustc --edition 2021 -O src/main.rs -o i13
    run     ./i13
    (cargo build --release also works if you have cargo)

Verified output:

    parse      ok
    flatten    max depth 0   (three-address, fixpoint in one pass)
    compile    31 top instrs + 3 function regions
    validate   VALID   peak height 4   one linear pass per region
    execute    71 steps

      total      = 10      I.p x4 osmotic, 0+1+2+3+4
      lossless   = 3       5 then 3, REPLACED
      nested     = 6       binom(4,2) flattened

    CORTEX     depth 3   owes Some('}')   sensor [0.375, 0, 0, 1, 0, 0]
               drain -> "}])"   depth now 0   fires [0, 3, 0, 0, 0]

## the files

| file | station | what |
|---|---|---|
| `lex.rs` | 01 | lexer. standard. |
| `ast.rs` | 02 | THE TWELVE, with attribution and node share |
| `parse.rs` | 03 | parser DERIVED from measured containment |
| `flatten.rs` | L3 | three-address rewrite. 0 params. fixpoint in one pass. |
| `isa.rs` | 07–09 | IVM-13-S, compiler, and the 1−k validator |
| `vm.rs` | 08 | structured stack machine. no loop: iteration is recursion. |
| `cortex.rs` | — | the five rules. zero parameters. |

## the law

    net = binds − k

`br` targets a **depth**, never an address. That single constraint is what
makes validation possible in one linear pass — with absolute jumps the stack
height at an instruction depends on how you arrived, so there is no single
number to check. The same correction is required for .NET CIL, whose
`finally` handler starts with a fresh stack, and whose declared `.maxstack`
this validator reproduces exactly.

## the claim, stated narrowly

Deterministic zero-parameter components guarantee structural properties that
no model at this scale reaches.

A GRU at 16,936 parameters predicts **better** — 0.8440 bits against the
sub-agent's 0.9182, 79.6% bracket accuracy against 74.3% — and generates
**2.3× worse**: 33.8 mismatched closers against 15.0, 16.6/40 clean against
24.0. It has recurrent state. Learned state is not a stack.

## I.p

`x.p <- v` desugars to `x <- x + v`. The operand is on **both sides**;
nothing is replaced. 16.28% of all binding in the Python stdlib is already
this shape and had no name. It costs the alphabet nothing — ATTRIBUTE +
ASSIGN + BINOP + NAME, four of the twelve, composed one plane down.

    I <- J        LOSSLESS   the operand is REPLACED.   detectable.
    I.p <- v      OSMOTIC    on both sides.             not detectable
                                                        without the prior value.
