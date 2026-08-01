//! Station 08 — the VM.  an ordinary structured stack machine.
//! no loop instruction: the twelve have no For or While, so iteration is
//! recursion.  the unboundedness did not disappear — it moved.  operand
//! depth is bounded (Sethi-Ullman = 8 over 117,013 stdlib expressions);
//! call depth is not.  choose the twelve and you choose where your
//! infinity lives.
use crate::isa::{Op, Program};
use std::collections::HashMap;
use std::rc::Rc;

#[derive(Clone, Debug)]
pub enum V { Num(f64), Fun(String), Nil }
impl V { pub fn truthy(&self) -> bool { matches!(self, V::Num(n) if *n != 0.0) } }

pub struct Vm<'a> { p: &'a Program, pub steps: usize, pub globals: HashMap<String, V> }
impl<'a> Vm<'a> {
    pub fn new(p: &'a Program) -> Self {
        Vm { p, steps: 0, globals: HashMap::new() }
    }
    pub fn run(&mut self) -> Result<(), String> {
        let code = self.p.top.clone();
        let mut env: HashMap<String, V> = HashMap::new();
        self.exec(&code, &mut env, Rc::new(HashMap::new()))?;
        for (k, v) in env { self.globals.insert(k, v); }
        Ok(())
    }
    fn exec(&mut self, code: &[Op], env: &mut HashMap<String, V>,
            outer: Rc<HashMap<String, V>>) -> Result<V, String> {
        let mut st: Vec<V> = Vec::new();
        let mut i = 0usize;
        while i < code.len() {
            self.steps += 1;
            if self.steps > 8_000_000 { return Err("step limit".into()) }
            match &code[i] {
                Op::Const(v)  => { st.push(V::Num(*v)); i += 1 }
                Op::Ask(n)    => {
                    let v = env.get(n).or_else(|| outer.get(n)).cloned()
                        .unwrap_or_else(|| if self.p.fns.contains_key(n) { V::Fun(n.clone()) } else { V::Nil });
                    st.push(v); i += 1
                }
                Op::Answer(n) => { let v = st.pop().ok_or("answer: empty")?; env.insert(n.clone(), v); i += 1 }
                Op::Attr(_)   => { i += 1 }
                Op::Bin(o)    => {
                    let r = num(st.pop())?; let l = num(st.pop())?;
                    st.push(V::Num(match o.as_str() {
                        "+" => l + r, "-" => l - r, "*" => l * r,
                        "/" => l / r, "%" => l % r, _ => return Err(format!("bin {o}")) }));
                    i += 1
                }
                Op::Cmp(o) => {
                    let r = num(st.pop())?; let l = num(st.pop())?;
                    let b = match o.as_str() {
                        "<" => l < r, ">" => l > r, "<=" => l <= r,
                        ">=" => l >= r, "==" => l == r, "!=" => l != r,
                        _ => return Err(format!("cmp {o}")) };
                    st.push(V::Num(if b { 1.0 } else { 0.0 })); i += 1
                }
                Op::If => {
                    let c = st.pop().ok_or("if: empty")?;
                    if c.truthy() { i += 1 } else { i = skip(code, i, true) }
                }
                Op::Else  => { i = skip(code, i, false) }
                Op::End | Op::Block => { i += 1 }
                Op::Func(_) => { i += 1 }
                Op::Drop  => { st.pop(); i += 1 }
                Op::Ret   => { return st.pop().ok_or_else(|| "ret: empty".into()) }
                Op::Halt  => break,
                Op::Call(n) => {
                    let f = st.pop().ok_or("call: empty")?;
                    let mut args = Vec::new();
                    for _ in 0..*n { args.push(st.pop().ok_or("call: args")?) }
                    args.reverse();
                    let name = match f { V::Fun(s) => s, _ => return Err("call: not a function".into()) };
                    let r = self.p.fns.get(&name).ok_or(format!("no fn {name}"))?.clone();
                    let mut e2 = HashMap::new();
                    for (k, v) in r.params.iter().zip(args) { e2.insert(k.clone(), v); }
                    let mut snap: HashMap<String, V> = (*outer).clone();
                    for (k, v) in env.iter() { snap.insert(k.clone(), v.clone()); }
                    let v = self.exec(&r.code, &mut e2, Rc::new(snap))?;
                    st.push(v); i += 1
                }
            }
        }
        Ok(st.pop().unwrap_or(V::Nil))
    }
}
fn num(v: Option<V>) -> Result<f64, String> {
    match v { Some(V::Num(n)) => Ok(n), Some(_) => Err("not a number".into()), None => Err("empty".into()) }
}
/// land on the instruction AFTER the matching terminator.
fn skip(code: &[Op], from: usize, stop_at_else: bool) -> usize {
    let (mut d, mut j) = (1i32, from + 1);
    while j < code.len() {
        match &code[j] {
            Op::If | Op::Block => d += 1,
            Op::Else if d == 1 && stop_at_else => return j + 1,
            Op::End => { d -= 1; if d == 0 { return j + 1 } }
            _ => {}
        }
        j += 1;
    }
    j
}
