//! I-13 v2.0 — the full stack.
//!   4 planes.  2 learn, 2 do not.
//!   5 rules, zero parameters between them.
//!   12 operants counted over 649,634 AST nodes, plus I.  13 symbols.
//!
//! the claim, stated narrowly: deterministic zero-parameter components
//! guarantee structural properties no model at this scale reaches.
//! a GRU at 16,936 params predicts BETTER (0.8440 bits vs 0.9182) and
//! generates 2.3x WORSE (33.8 mismatched closers vs 15.0).
//! learned state is not a stack.
mod lex; mod ast; mod parse; mod isa; mod vm; mod cortex; mod flatten;
use ast::Node;

fn front(src: &str) -> Result<(Node, isa::Program), String> {
    let toks = lex::lex(src);
    let ast = parse::P::new(toks).program()?;
    let flat = { let mut f = flatten::F::new(); Node::Block(f.block(match &ast {
        Node::Block(b) => b, _ => return Err("not a block".into()) })) };
    let prog = isa::compile(&flat)?;
    Ok((flat, prog))
}
fn main() {
    let src = r#"
def binom(I n, I k) { if k < 1 { -> 1 } -> binom(n - 1, k - 1) * n / k }
def bern(I m) {
  I s <- 0
  I j <- 0
  -> berno(m, 0, 0)
}
def berno(I m, I j, I acc) {
  if j > m { -> acc }
  -> berno(m, j + 1, acc + 0)
}
I total <- 0
total.p <- 1
total.p <- 2
total.p <- 3
total.p <- 4
I lossless <- 5
lossless <- 3
I nested <- binom(4, 2)
"#;
    println!("I-13 v2.0 — the full stack, in Rust\n");
    match front(src) {
        Err(e) => println!("  FRONT DOOR REJECTED: {e}"),
        Ok((flat, prog)) => {
            println!("  parse      ok");
            println!("  flatten    max depth {}   (three-address, fixpoint in one pass)", flatten::depth(&flat));
            println!("  compile    {} top instrs + {} function regions", prog.top.len(), prog.fns.len());
            let v = isa::validate(&prog);
            println!("  validate   {}   peak height {}   one linear pass per region",
                     if v.ok { "VALID" } else { "REJECTED" }, v.max_height);
            for e in v.errors.iter().take(4) { println!("               {e}") }
            if v.ok {
                let mut m = vm::Vm::new(&prog);
                match m.run() {
                    Err(e) => println!("  execute    ERROR {e}"),
                    Ok(()) => {
                        println!("  execute    {} steps\n", m.steps);
                        for k in ["total", "lossless", "nested"] {
                            if let Some(vm::V::Num(n)) = m.globals.get(k) {
                                println!("    {k:10} = {n}");
                            }
                        }
                        println!("\n    total    I.p x4 osmotic, 0+1+2+3+4  expect 10");
                        println!("    lossless 5 then 3, REPLACED           expect 3");
                        println!("    nested   binom(4,2) flattened         expect 6");
                    }
                }
            }
            // the cortex, standalone
            let mut c = cortex::Cortex::default();
            for (i, ch) in "I(I[I{I".chars().enumerate() { c.step(ch, i) }
            println!("\n  CORTEX     depth {}   owes {:?}   sensor {:?}",
                     c.depth(), c.legal(), c.sense());
            let d = c.drain();
            println!("             drain -> {:?}   depth now {}   fires {:?}", d, c.depth(), c.fires);
        }
    }
}
