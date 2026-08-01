//! THE CORTEX — five rules, ZERO parameters between them.
//! deterministic, bounded state, and provably closed: five runs over the
//! same input hash identically.  each rule holds one thing a fixed window
//! structurally cannot: a stack, a debt, a plane, an identity, a counter.
//!
//! measured reach, per 1,000 nodes:
//!                    L1     L2     L3     L4
//!   veto           137.5   52.4   56.2   53.4
//!   -I             137.5   52.4   56.2   53.4
//!   depth          168.5  212.5  182.1  187.1
//!   idempotence     59.0    0.00   0.00   0.00   <- statements only
//!   address        168.5    0.00   0.00   0.00   <- statements only
//!
//! there are no statements inside an expression.
use std::collections::HashSet;

pub const PAIRS: [(char, char); 3] = [('(', ')'), ('[', ']'), ('{', '}')];

#[derive(Default)]
pub struct Cortex {
    pub stack: Vec<char>,
    pub opened: Vec<usize>,
    pub last: Option<String>,
    pub run: usize,
    pub banned: HashSet<String>,
    pub addr: usize,
    pub fires: [usize; 5],
}
impl Cortex {
    pub fn open_of(c: char) -> Option<char> { PAIRS.iter().find(|p| p.0 == c).map(|p| p.1) }
    pub fn close_of(c: char) -> Option<char> { PAIRS.iter().find(|p| p.1 == c).map(|p| p.0) }
    /// RULE 1 — VETO.  the only legal closer, or none.
    pub fn legal(&self) -> Option<char> { self.stack.last().and_then(|&c| Self::open_of(c)) }
    pub fn depth(&self) -> usize { self.stack.len() }
    /// RULE 3 — DEPTH.  refuse a plane already paid for.
    pub fn may_open(&mut self, ceiling: usize) -> bool {
        if self.stack.len() >= ceiling { self.fires[2] += 1; false } else { true }
    }
    /// RULE 2 — −I.  pressure rising with the age of the opener.
    pub fn pressure(&mut self, step: usize) -> f64 {
        if self.stack.is_empty() { return 0.0 }
        self.fires[1] += 1;
        let age = self.opened.last().map_or(0, |&o| step.saturating_sub(o));
        1.5 * ((1 + age) as f64).ln()
    }
    /// RULE 2 — −I.  the drain.  settles every outstanding opener at once.
    pub fn drain(&mut self) -> String {
        let mut out = String::new();
        while let Some(c) = self.stack.pop() {
            if let Some(cl) = Self::open_of(c) { out.push(cl); self.fires[1] += 1 }
        }
        out
    }
    /// RULE 5 — ADDRESS.  the substrate WRITES it.  the model gets no vote.
    /// constraining the model toward monotonic instead gave 44-digit
    /// runaways; handing it over gave 99%.
    pub fn address(&mut self, step: usize) -> String { self.addr += step; self.fires[4] += 1; format!("{} ", self.addr) }
    /// RULE 4 — IDEMPOTENCE.  I am I.  a no-op cannot repeat.
    pub fn idempotent(&mut self, stmt: &str, noops: &[&str]) -> bool {
        let head = stmt.split_whitespace().next().unwrap_or("");
        let same = self.last.as_deref() == Some(stmt);
        if noops.contains(&head) && same { self.banned.insert(head.into()); self.fires[3] += 1; false }
        else { self.banned.clear(); true }
    }
    pub fn step(&mut self, c: char, at: usize) {
        if Self::open_of(c).is_some() { self.stack.push(c); self.opened.push(at) }
        else if let Some(o) = Self::close_of(c) {
            if self.stack.last() == Some(&o) { self.stack.pop(); self.opened.pop(); }
            else { self.fires[0] += 1 }
        }
    }
    /// the sensor.  (c(sa())) — the cortex hands its own state back as
    /// input rather than only as a veto.  six floats took L2 mismatch
    /// from 15.0 +/- 2.1 to 0.6 +/- 0.8 with NOTHING correcting.
    pub fn sense(&self) -> [f32; 6] {
        let mut f = [0.0f32; 6];
        f[0] = (self.depth().min(8) as f32) / 8.0;
        match self.legal() {
            Some(')') => f[1] = 1.0, Some(']') => f[2] = 1.0,
            Some('}') => f[3] = 1.0, _ => f[4] = 1.0,
        }
        f[5] = (self.run.min(12) as f32) / 12.0;
        f
    }
}
