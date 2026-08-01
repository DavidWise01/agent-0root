//! Stations 07–09 — IVM-13-S, the STRUCTURED ISA, and the 1−k VALIDATOR.
//!
//! the law:            net = binds − k
//! the design rule:    `br` targets a DEPTH, never an address.
//!
//! that single constraint is what makes validation possible in one linear
//! pass.  with absolute jumps the stack height at an instruction depends on
//! how you arrived, so there is no single number to check — measured the
//! hard way: the flat validator rejected a program known to be correct.
//! the same correction was needed for .NET CIL, whose `finally` handler
//! starts with a fresh stack, and whose declared .maxstack this validator
//! reproduces exactly.
use crate::ast::Node;
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq)]
pub enum Op {
    Const(f64), Ask(String), Answer(String), Attr(String),
    Bin(String), Cmp(String),
    Block, If, Else, End,
    Call(usize), Ret, Drop, Func(String), Halt,
}
impl Op {
    /// (k consumed, binds produced).  the whole arithmetic of the machine.
    pub fn effect(&self) -> (i32, i32) {
        match self {
            Op::Const(_) | Op::Ask(_)      => (0, 1),   // bind, pay nothing        +1
            Op::Attr(_) | Op::Ret          => (1, 1),   // bind one, pay one         0
            Op::Answer(_) | Op::Drop       => (1, 0),   // pay one, bind NOWHERE    −1
            Op::Bin(_) | Op::Cmp(_)        => (2, 1),   // bind one, pay two        −1
            Op::If                         => (1, 0),
            Op::Call(n)                    => (*n as i32 + 1, 1),
            _                              => (0, 0),
        }
    }
}
#[derive(Debug, Clone)]
pub struct Region { pub params: Vec<String>, pub code: Vec<Op> }
#[derive(Debug, Clone, Default)]
pub struct Program { pub top: Vec<Op>, pub fns: HashMap<String, Region> }

// ── COMPILER ────────────────────────────────────────────────────────────
pub fn compile(ast: &Node) -> Result<Program, String> {
    let mut p = Program::default();
    let mut top = Vec::new();
    if let Node::Block(b) = ast { for s in b { stmt(s, &mut top, &mut p.fns)? } }
    top.push(Op::Halt);
    p.top = top;
    Ok(p)
}
fn stmt(n: &Node, out: &mut Vec<Op>, fns: &mut HashMap<String, Region>) -> Result<(), String> {
    match n {
        Node::Block(b) => { for s in b { stmt(s, out, fns)? } }
        Node::Assign { name, value, .. } => { ex(value, out)?; out.push(Op::Answer(name.clone())) }
        Node::Return(v) => { ex(v, out)?; out.push(Op::Ret) }
        Node::Expr(e)   => { ex(e, out)?; out.push(Op::Drop) }
        Node::Name(_)   => {}
        Node::If { cond, then, els } => {
            ex(cond, out)?; out.push(Op::If);
            for s in then { stmt(s, out, fns)? }
            if let Some(e) = els { out.push(Op::Else); for s in e { stmt(s, out, fns)? } }
            out.push(Op::End);
        }
        Node::FunctionDef { name, params, body } => {
            // a function is its OWN REGION with declared params.  popping
            // arguments off the caller's stack makes entry height depend on
            // the caller, and then no region can be checked alone.
            let mut c = Vec::new();
            for s in body { stmt(s, &mut c, fns)? }
            c.push(Op::Const(0.0)); c.push(Op::Ret);
            fns.insert(name.clone(), Region { params: params.clone(), code: c });
            out.push(Op::Func(name.clone()));
        }
        _ => return Err(format!("stmt {n:?}")),
    }
    Ok(())
}
fn ex(n: &Node, out: &mut Vec<Op>) -> Result<(), String> {
    match n {
        Node::Constant(v) => out.push(Op::Const(*v)),
        Node::Name(s)     => out.push(Op::Ask(s.clone())),
        Node::Attribute(o, f) => { ex(o, out)?; out.push(Op::Attr(f.clone())) }
        Node::BinOp(l, o, r)  => { ex(l, out)?; ex(r, out)?; out.push(Op::Bin(o.clone())) }
        Node::Compare(l, o, r)=> { ex(l, out)?; ex(r, out)?; out.push(Op::Cmp(o.clone())) }
        Node::Call(f, a)      => { for x in a { ex(x, out)? } ex(f, out)?; out.push(Op::Call(a.len())) }
        _ => return Err(format!("ex {n:?}")),
    }
    Ok(())
}
// ── VALIDATOR ───────────────────────────────────────────────────────────
#[derive(Debug)]
pub struct Verdict { pub ok: bool, pub errors: Vec<String>, pub max_height: i32 }
pub fn validate(p: &Program) -> Verdict {
    let mut errs = Vec::new(); let mut mx = 0;
    let mut regions: Vec<(String, &Vec<Op>)> = vec![("<top>".into(), &p.top)];
    for (k, r) in &p.fns { regions.push((format!("fn {k}"), &r.code)) }
    for (label, code) in regions {
        let (mut h, mut ctrl, mut unreachable) = (0i32, Vec::<i32>::new(), false);
        for (i, op) in code.iter().enumerate() {
            match op {
                Op::Block => ctrl.push(h),
                Op::If    => { h -= 1; if h < 0 { errs.push(format!("{label}[{i}] underflow")) }
                               ctrl.push(h); unreachable = false }
                Op::Else  => match ctrl.last() {
                    Some(&f) => { if h != f && !unreachable {
                                    errs.push(format!("{label}[{i}] arms disagree {h} vs {f}")) }
                                  h = f; unreachable = false }
                    None => errs.push(format!("{label}[{i}] ELSE with no label")),
                },
                Op::End => match ctrl.pop() {
                    Some(f) => { if h != f && !unreachable {
                                   errs.push(format!("{label}[{i}] block leaves {h}, entered {f}")) }
                                 h = f; unreachable = false }
                    None => errs.push(format!("{label}[{i}] END with no label")),
                },
                Op::Ret => { if h < 1 { errs.push(format!("{label}[{i}] return, empty stack")) }
                             unreachable = true }
                _ => { let (k, b) = op.effect(); h += b - k;
                       if h < 0 { errs.push(format!("{label}[{i}] underflow, height {h}")) } }
            }
            if h > mx { mx = h }
        }
        if !ctrl.is_empty() { errs.push(format!("{label}: {} label(s) never closed", ctrl.len())) }
    }
    Verdict { ok: errs.is_empty(), errors: errs, max_height: mx }
}
