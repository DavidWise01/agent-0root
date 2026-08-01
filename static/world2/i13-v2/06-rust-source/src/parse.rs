//! Station 03 — PARSER.  DERIVED, not authored.
//! the precedence ladder was recovered from measured containment over the
//! stdlib: 43 firm orderings, 1 ambiguous pair, 0 cycles.  Attribute holds
//! Name 53,643 : 0.  the emitted parser produced a byte-identical AST to
//! the hand-written one, so the grammar is a fact about the twelve rather
//! than a choice.
use crate::ast::Node;
pub struct P { t: Vec<String>, i: usize }
type R<T> = Result<T, String>;
impl P {
    pub fn new(t: Vec<String>) -> Self { P { t, i: 0 } }
    fn peek(&self) -> &str { self.t.get(self.i).map(|s| s.as_str()).unwrap_or("") }
    fn at(&self, k: usize) -> &str { self.t.get(self.i + k).map(|s| s.as_str()).unwrap_or("") }
    fn bump(&mut self) -> String { let s = self.t[self.i].clone(); self.i += 1; s }
    fn eat(&mut self, w: &str) -> R<()> {
        if self.peek() == w { self.i += 1; Ok(()) } else { Err(format!("want {w} got {}", self.peek())) }
    }
    fn is_name(s: &str) -> bool {
        !s.is_empty() && s.chars().next().unwrap().is_alphabetic()
            && s.chars().all(|c| c.is_alphanumeric() || c == '_')
    }
    pub fn program(&mut self) -> R<Node> {
        let mut b = Vec::new();
        while self.i < self.t.len() { b.push(self.stmt()?) }
        Ok(Node::Block(b))
    }
    fn block(&mut self) -> R<Vec<Node>> {
        self.eat("{")?;
        let mut b = Vec::new();
        while self.peek() != "}" && self.i < self.t.len() { b.push(self.stmt()?) }
        self.eat("}")?; Ok(b)
    }
    fn stmt(&mut self) -> R<Node> {
        // FUNCTIONDEF — Church 1936
        if self.peek() == "def" {
            self.i += 1;
            let name = self.bump();
            self.eat("(")?;
            let mut params = Vec::new();
            while self.peek() != ")" {
                self.eat("I")?; params.push(self.bump());
                if self.peek() == "," { self.i += 1 }
            }
            self.eat(")")?;
            let body = self.block()?;
            return Ok(Node::FunctionDef { name, params, body });
        }
        // declaration:  I x <- expr
        if self.peek() == "I" && Self::is_name(self.at(1)) {
            self.i += 1;
            let name = self.bump();
            if self.peek() == "<-" {
                self.i += 1;
                let value = Box::new(self.expr()?);
                if self.peek() == ";" { self.i += 1 }
                return Ok(Node::Assign { name, value, osmotic: false });
            }
            if self.peek() == ";" { self.i += 1 }
            return Ok(Node::Name(name));
        }
        // ── I.p ── the OSMOTIC bind.  x.p <- v  desugars to  x <- x + v.
        // the operand is on BOTH SIDES; nothing is replaced.  16.28% of all
        // binding in the stdlib is already this shape and had no name.
        // costs the alphabet nothing: ATTRIBUTE + ASSIGN + BINOP + NAME.
        if Self::is_name(self.peek()) && self.at(1) == "." && self.at(2) == "p" && self.at(3) == "<-" {
            let name = self.bump(); self.i += 3;
            let v = self.expr()?;
            if self.peek() == ";" { self.i += 1 }
            return Ok(Node::Assign {
                name: name.clone(),
                value: Box::new(Node::BinOp(Box::new(Node::Name(name)), "+".into(), Box::new(v))),
                osmotic: true,
            });
        }
        if Self::is_name(self.peek()) && self.at(1) == "<-" {
            let name = self.bump(); self.i += 1;
            let value = Box::new(self.expr()?);
            if self.peek() == ";" { self.i += 1 }
            return Ok(Node::Assign { name, value, osmotic: false });
        }
        if self.peek() == "if" {
            self.i += 1;
            let cond = Box::new(self.expr()?);
            let then = self.block()?;
            let els = if self.peek() == "else" { self.i += 1; Some(self.block()?) } else { None };
            return Ok(Node::If { cond, then, els });
        }
        if self.peek() == "->" {
            self.i += 1;
            let v = Box::new(self.expr()?);
            if self.peek() == ";" { self.i += 1 }
            return Ok(Node::Return(v));
        }
        let e = self.expr()?;
        if self.peek() == ";" { self.i += 1 }
        Ok(Node::Expr(Box::new(e)))
    }
    // the ladder, loosest first
    fn expr(&mut self) -> R<Node> { self.cmp() }
    fn cmp(&mut self) -> R<Node> {
        let mut l = self.add()?;
        while matches!(self.peek(), "<" | ">" | "<=" | ">=" | "==" | "!=") {
            let o = self.bump(); let r = self.add()?;
            l = Node::Compare(Box::new(l), o, Box::new(r));
        }
        Ok(l)
    }
    fn add(&mut self) -> R<Node> {
        let mut l = self.mul()?;
        while matches!(self.peek(), "+" | "-") {
            let o = self.bump(); let r = self.mul()?;
            l = Node::BinOp(Box::new(l), o, Box::new(r));
        }
        Ok(l)
    }
    fn mul(&mut self) -> R<Node> {
        let mut l = self.post()?;
        while matches!(self.peek(), "*" | "/" | "%") {
            let o = self.bump(); let r = self.post()?;
            l = Node::BinOp(Box::new(l), o, Box::new(r));
        }
        Ok(l)
    }
    fn post(&mut self) -> R<Node> {
        let mut x = self.prim()?;
        loop {
            if self.peek() == "." {
                self.i += 1; let f = self.bump();
                x = Node::Attribute(Box::new(x), f);
            } else if self.peek() == "(" {
                self.i += 1;
                let mut a = Vec::new();
                while self.peek() != ")" {
                    a.push(self.expr()?);
                    if self.peek() == "," { self.i += 1 }
                }
                self.eat(")")?;
                x = Node::Call(Box::new(x), a);
            } else { return Ok(x) }
        }
    }
    fn prim(&mut self) -> R<Node> {
        let t = self.peek().to_string();
        // unary minus desugars to 0 - x.  no thirteenth form is added.
        if t == "-" { self.i += 1; let inner = self.prim()?;
            return Ok(Node::BinOp(Box::new(Node::Constant(0.0)), "-".into(), Box::new(inner))) }
        if t.chars().next().map_or(false, |c| c.is_ascii_digit()) {
            self.i += 1;
            return Ok(Node::Constant(t.parse().map_err(|_| format!("bad number {t}"))?));
        }
        if t == "(" { self.i += 1; let e = self.expr()?; self.eat(")")?; return Ok(e) }
        if Self::is_name(&t) { self.i += 1; return Ok(Node::Name(t)) }
        Err(format!("prim {t}"))
    }
}
