//! Station 01 — LEXER.  standard.
pub fn lex(src: &str) -> Vec<String> {
    let mut out = Vec::new();
    let b: Vec<char> = src.chars().collect();
    let mut i = 0;
    while i < b.len() {
        let c = b[i];
        if c.is_whitespace() { i += 1; continue }
        if c == '/' && i + 1 < b.len() && b[i + 1] == '/' {
            while i < b.len() && b[i] != '\n' { i += 1 }
            continue;
        }
        // two-character forms first: <- -> <= >= == !=
        if i + 1 < b.len() {
            let two: String = b[i..i + 2].iter().collect();
            if matches!(two.as_str(), "<-" | "->" | "<=" | ">=" | "==" | "!=") {
                out.push(two); i += 2; continue;
            }
        }
        if c.is_ascii_digit() {
            let s = i;
            while i < b.len() && (b[i].is_ascii_digit() || b[i] == '.') { i += 1 }
            out.push(b[s..i].iter().collect()); continue;
        }
        if c.is_alphabetic() || c == '_' {
            let s = i;
            while i < b.len() && (b[i].is_alphanumeric() || b[i] == '_') { i += 1 }
            out.push(b[s..i].iter().collect()); continue;
        }
        out.push(c.to_string()); i += 1;
    }
    out
}
