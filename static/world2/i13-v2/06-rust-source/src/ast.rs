//! THE TWELVE.  counted over 649,634 AST nodes across 504 stdlib files.
//! 83.27% coverage.  not designed — ranked and cut.
//! plus `I`, the referent, which is the only one that is not a verb.
#[derive(Debug, Clone, PartialEq)]
pub enum Node {
    // ── I DESIGNATE ──────────────────────────────── 53.55% of node traffic
    Name(String),                          // Lovelace 1843   29.67%
    Constant(f64),                         // Lovelace 1843   14.25%
    Attribute(Box<Node>, String),          // Hoare    1966    9.63%
    Call(Box<Node>, Vec<Node>),            // Church   1936    7.50%
    // ── II BIND ──────────────────────────────────── 11.13%
    Assign { name: String, value: Box<Node>, osmotic: bool },  // Lovelace 1843
    Arg(String),                           // Frege    1879    4.08%
    Return(Box<Node>),                     // Wheeler  1949    1.82%
    // ── III DECIDE ────────────────────────────────── 7.78%
    If { cond: Box<Node>, then: Vec<Node>, els: Option<Vec<Node>> },  // Lovelace 1843
    Compare(Box<Node>, String, Box<Node>), // Lovelace 1843    2.01%
    // ── IV TRANSFORM ─────────────────────────────── 10.80%
    BinOp(Box<Node>, String, Box<Node>),   // Lovelace 1843    1.38%
    Expr(Box<Node>),                       // Backus   1957    3.01%
    FunctionDef { name: String, params: Vec<String>, body: Vec<Node> }, // Church 1936
    Block(Vec<Node>),
}
