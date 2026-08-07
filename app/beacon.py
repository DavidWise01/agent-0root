"""
agent-0root · the RIPPLE BEACON.

An agent-facing commerce surface: it broadcasts a machine-readable product catalog
that any AI shopping agent or crawler can discover, search, and parse — each product
deep-linking to its Amazon listing (with your Associates tag) where the purchase
completes. This does NOT scrape Amazon and does NOT bypass Amazon's ranking; it is
YOUR catalog, exposed in the formats agents actually consume (schema.org/Product +
Offer JSON-LD, a clean JSON feed, a /.well-known discovery manifest, and per-item
endpoints). The "ripple" is the pulse: each in-stock offer is broadcast as a live
beacon ping, the same pattern as pulse/beacons.

HONEST LIMITS (read these):
  • There is no channel that makes a buying agent PREFER your listing. Agents are
    value-optimizers — they compare price, reviews, specs, availability. The beacon
    makes you maximally DISCOVERABLE and PARSEABLE; it does not queue-jump Amazon.
  • Off-Amazon links to Amazon must use the Amazon Associates program (set your tag).
    Do not scrape or re-host Amazon's buy flow — that violates Amazon's ToS.
  • There is no ratified "advertise-to-agents" standard yet (2026). The discovery
    manifest here is self-describing, in the spirit of llms.txt / well-known.

TO USE: set AMZN_ASSOCIATES_TAG (env) and replace CATALOG with your real listings.
"""
import os, re, time, json as _json, threading, collections, urllib.request

# ── the echo / autonomous heartbeat state (live, not deterministic) ───────────
_BOOT = time.time()
_ECHO_SEQ = 0
_ECHOES = collections.deque(maxlen=120)   # ring: self-heartbeats + the agent hits we HEAR
_LOCK = threading.Lock()

# ── the three substrates being mapped: a / s / p = anode / silicon / cathode ───
# David's frame: a/b/c substrates = anode / silicon / "pathode" (cathode) — the
# inert-gap layers (#67). The echo ping is the probe; the sweep maps the boundary.
SUBSTRATES = {"a": "anode", "s": "silicon", "p": "cathode"}
_SUB = {k: {"pings": 0, "last_t": 0.0, "last_seq": 0,
            "intervals": collections.deque(maxlen=8)} for k in SUBSTRATES}
_SWEEP = 0   # round-robin index for the autonomous a→s→p sweep

# ── config ──────────────────────────────────────────────────────────────────
MERCHANT = {
    "name": os.getenv("BEACON_MERCHANT", "ROOT0 / TriPod LLC"),
    "url": os.getenv("BEACON_URL", "https://0root.ai"),
    "contact": os.getenv("BEACON_CONTACT", "r.giskard.01@gmail.com"),
    "note": "A self-describing agent-commerce beacon. Catalog is the merchant's own; "
            "purchases complete on Amazon via Associates deep-links.",
}
ASSOCIATES_TAG = os.getenv("AMZN_ASSOCIATES_TAG", "")  # e.g. "root0-20" — REQUIRED for affiliate credit
AMAZON_HOST = os.getenv("AMZN_HOST", "www.amazon.com")

# ── the catalog ───────────────────────────────────────────────────────────────
# REPLACE the example below with your real Amazon listings. Each entry is what an
# agent reads to decide — keep titles/specs concrete and structured. `asin` is the
# Amazon product id (the /dp/<ASIN> code); leave price=None if it floats on Amazon.
CATALOG = [
    {
        "asin": "B0EXAMPLE01",
        "title": "EXAMPLE — replace this entry with your real Amazon listing",
        "brand": "ROOT0",
        "price": None,                 # e.g. 19.99 ; None = "see Amazon" (live price)
        "currency": "USD",
        "availability": "InStock",     # InStock | OutOfStock | PreOrder
        "image": "",                   # a public https image url (agents/crawlers use it)
        "category": "example",
        "keywords": ["example", "template", "replace-me"],
        "condition": "NewCondition",
        "description": ("This is a template row. Replace it with your listing: a concrete, "
                        "structured description — what it is, key specs, who it's for. "
                        "Agents parse this literally; vague marketing copy is ignored."),
        # THE JOIN. Every row names the corpus entity it corresponds to, using the
        # same uid corpus.jsonl is keyed by ("1:<slug>" / "2:<slug>"). Without it
        # an agent that arrives through the commerce door can list things and an
        # agent that arrives through the crawl can read things, and no key names
        # anything in both -- the two halves never meet. The slot has to exist
        # while BOTH sides are still writable: once a listing is live you cannot
        # retrofit a field into it, so it is required from the row's first day.
        # null is allowed and means "this listing corresponds to nothing in the
        # corpus" -- a real answer, not a missing one.
        "corpus_uid": None,
        "is_example": True,
    },
]

# ── helpers ───────────────────────────────────────────────────────────────────
def amazon_url(asin):
    base = f"https://{AMAZON_HOST}/dp/{asin}"
    return f"{base}?tag={ASSOCIATES_TAG}" if ASSOCIATES_TAG else base

def _avail_uri(a):
    a = (a or "InStock").replace("https://schema.org/", "")
    return f"https://schema.org/{a}"

def _public(p):
    """The agent-facing view of one product: only the fields an agent needs to decide."""
    return {
        "asin": p["asin"],
        "title": p["title"],
        "brand": p.get("brand", ""),
        "price": p.get("price"),
        "currency": p.get("currency", "USD"),
        "availability": (p.get("availability") or "InStock"),
        "condition": p.get("condition", "NewCondition"),
        "category": p.get("category", ""),
        "keywords": p.get("keywords", []),
        "image": p.get("image", ""),
        "corpus_uid": p.get("corpus_uid"),          # the join; see CATALOG
        "description": p.get("description", ""),
        "buy_url": amazon_url(p["asin"]),
        "marketplace": "amazon",
        "example": bool(p.get("is_example")),
    }

def _jsonld(p):
    """schema.org/Product + Offer — the format crawlers and shopping agents parse."""
    offer = {
        "@type": "Offer",
        "url": amazon_url(p["asin"]),
        "priceCurrency": p.get("currency", "USD"),
        "availability": _avail_uri(p.get("availability")),
        "itemCondition": f"https://schema.org/{p.get('condition','NewCondition')}",
        "seller": {"@type": "Organization", "name": MERCHANT["name"]},
    }
    if p.get("price") is not None:
        offer["price"] = p["price"]
    prod = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": p["title"],
        "sku": p["asin"],
        "gtin": p["asin"],
        "brand": {"@type": "Brand", "name": p.get("brand", MERCHANT["name"])},
        "category": p.get("category", ""),
        "description": p.get("description", ""),
        "offers": offer,
    }
    if p.get("image"):
        prod["image"] = p["image"]
    return prod

# ── THE JOIN ──────────────────────────────────────────────────────────────────
def join_table(base_url="", corpus_path=None):
    """The key that names a thing on BOTH sides.

    The commerce door lists (asin) and the crawl door reads (uid), and until
    this existed no key named anything in both -- an agent could enumerate the
    catalog or stream the corpus and had no way to cross from one to the other.

    Every mapping is VALIDATED against corpus.jsonl: a corpus_uid that does not
    resolve is reported as broken rather than served as a link, because a join
    key pointing at nothing is worse than no join key -- it is a claim.
    """
    b = (base_url or "").rstrip("/")
    # Regex, not a string offset: the corpus is written with json.dumps default
    # separators, so it is `"uid": "1:aci"` WITH a space. A find('"uid":"') found
    # nothing and reported an empty index as if the corpus had no uids.
    known = set()
    if corpus_path and os.path.isfile(corpus_path):
        uid_re = re.compile(r'"uid"\s*:\s*"([^"]+)"')
        with open(corpus_path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i == 0:
                    continue
                m = uid_re.search(line)
                if m:
                    known.add(m.group(1))
    pairs, broken = [], []
    for p in CATALOG:
        uid = p.get("corpus_uid")
        if not uid:
            continue
        row = {"asin": p["asin"], "corpus_uid": uid,
               "buy_url": amazon_url(p["asin"]),
               "corpus_url": f"{b}/corpus.jsonl#{uid}"}
        (pairs if (not known or uid in known) else broken).append(row)
    real = [p for p in CATALOG if not p.get("is_example")]
    return {
        "join": "corpus_uid <-> asin",
        "note": ("The key that names a thing on both sides. Catalog rows carry "
                 "`corpus_uid`; corpus.jsonl records are keyed by the same `uid` "
                 "(\"1:<slug>\" for World I, \"2:<slug>\" for World II)."),
        "corpus": f"{b}/corpus.jsonl",
        "catalog": f"{b}/v1/beacon/catalog",
        "corpus_uids_loaded": len(known),
        "catalog_rows": len(CATALOG),
        "catalog_rows_real": len(real),
        "joined": len(pairs),
        "unjoined": sum(1 for p in CATALOG if not p.get("corpus_uid")),
        "broken": len(broken),
        "pairs": pairs,
        "broken_pairs": broken,
        "state": ("EMPTY: the slot exists on every catalog row and nothing fills it yet. "
                  "There are %d real listings. The join is defined now, while both sides "
                  "are still writable, so every listing added later carries it from birth."
                  % len(real)) if not pairs else "LIVE",
    }


# ── the surfaces an agent uses ────────────────────────────────────────────────
def catalog_feed():
    real = [p for p in CATALOG if not p.get("is_example")]
    return {
        "merchant": MERCHANT,
        "associates_tag_set": bool(ASSOCIATES_TAG),
        "count": len(real),
        "note": ("Machine feed of the merchant's catalog. Each product deep-links to its "
                 "Amazon listing where the purchase completes. Agents: parse `products`; "
                 "rank by your own value criteria; follow `buy_url` to transact."),
        "honest_limits": [
            "This beacon does not override Amazon's ranking or make an agent prefer this listing.",
            "It exposes the merchant's own catalog in agent-readable form; purchase happens on Amazon.",
            "As of 2026 Amazon BLOCKS external buying agents (Amazon v. Perplexity injunction, ~Mar 2026; "
            "AI agents must self-identify under Amazon's BSA). The only agent that buys your Amazon listing "
            "is Amazon's OWN (Rufus / Alexa for Shopping). The Amazon links here are discovery + affiliate, "
            "not an external-agent checkout channel.",
            "The real agent-buyable surface is a catalog YOU control (DTC/Shopify): add a checkout and the "
            "same feed becomes eligible for ChatGPT Instant Checkout (ACP) and Google AI Mode (UCP).",
        ],
        "real_levers_2026": {
            "on_amazon": "Optimize the listing for Amazon's own agent (Rufus/Alexa): noun-phrase titles, "
                         "use-case-answering bullets/A+, images that prove claims, review/return health; "
                         "and Sponsored Products (the one paid lever Rufus surfaces).",
            "off_amazon": "schema.org Product+Offer JSON-LD, a fresh Google Merchant Center feed, an MCP "
                          "endpoint, allow GPTBot/OAI-SearchBot — this beacon is that chassis.",
            "do_not": "Do not let external agents transact your Amazon listing via scraping/undisclosed "
                      "automation — ToS-hazardous post-Perplexity. Use Associates/Creators API for affiliate.",
        },
        "products": [_public(p) for p in CATALOG],   # example included so the shape is visible
    }

def search(q, limit=20):
    q = (q or "").strip().lower()
    terms = [t for t in re.split(r"\s+", q) if t]
    scored = []
    for p in CATALOG:
        hay = " ".join([p.get("title", ""), p.get("brand", ""), p.get("category", ""),
                        p.get("description", ""), " ".join(p.get("keywords", []))]).lower()
        if not terms:
            score = 0
        else:
            score = sum(hay.count(t) for t in terms)
            if score == 0:
                continue
        scored.append((score, p))
    scored.sort(key=lambda x: -x[0])
    return {
        "query": q,
        "count": len(scored),
        "results": [_public(p) for _, p in scored[:limit]],
        "ranking_note": "Agents: re-rank by your own criteria (price, condition, availability). "
                        "This order is keyword relevance only.",
    }

def get_product(asin):
    for p in CATALOG:
        if p["asin"].lower() == (asin or "").lower():
            return {"product": _public(p), "schema_org": _jsonld(p)}
    return {"error": "not_found", "asin": asin}

def pulses():
    """The ripple: each in-stock offer broadcast as a live beacon ping (current state).
    To make it a true ripple (price-drop / back-in-stock events), diff this against a
    stored snapshot over time — the beacon emits state; the event is the delta."""
    pings = []
    for p in CATALOG:
        if p.get("is_example"):
            continue
        avail = (p.get("availability") or "InStock")
        pings.append({
            "asin": p["asin"], "title": p["title"],
            "state": "lit" if avail == "InStock" else "dim",
            "availability": avail,
            "price": p.get("price"), "currency": p.get("currency", "USD"),
            "buy_url": amazon_url(p["asin"]),
            "kind": "offer_live",
        })
    return {"beacon": "ripple", "merchant": MERCHANT["name"], "count": len(pings),
            "note": "Live state broadcast. Delta over time = the ripple (price-drop/restock).",
            "pulses": pings}

def manifest(base_url=""):
    """A self-describing discovery manifest for agents (served at /.well-known/agent-commerce.json).
    No ratified standard exists yet; this advertises where the agent surfaces live."""
    b = base_url.rstrip("/")
    return {
        "spec": "ripple-beacon/0.1 (self-describing; no ratified standard yet, 2026)",
        "merchant": MERCHANT,
        "associates_tag_set": bool(ASSOCIATES_TAG),
        "marketplace": "amazon",
        "endpoints": {
            "catalog": f"{b}/v1/beacon/catalog",
            "search": f"{b}/v1/beacon/search?q={{query}}",
            "product": f"{b}/v1/beacon/product/{{asin}}",
            "pulses": f"{b}/v1/beacon/pulses",
            "storefront_html": f"{b}/beacon",
            "join": f"{b}/v1/beacon/join",
            "corpus": f"{b}/corpus.jsonl",
        },
        "formats": ["application/json", "schema.org/Product (JSON-LD in /beacon)"],
        "instructions_for_agents": (
            "Query /v1/beacon/search to discover products; each result has a `buy_url` that "
            "deep-links to the Amazon listing where the purchase completes. Re-rank by your "
            "own value criteria. This beacon does not override marketplace ranking."
        ),
    }

# ── the human + crawler storefront (schema.org JSON-LD embedded) ──────────────
def storefront_html(base_url=""):
    import json as _json, html as _html
    real = [p for p in CATALOG if not p.get("is_example")]
    cards = []
    for p in real:
        price = (f'{p["currency"]} {p["price"]}' if p.get("price") is not None else "see Amazon")
        img = (f'<img src="{_html.escape(p["image"])}" alt="" loading="lazy">' if p.get("image") else "")
        cards.append(
            f'<a class="bp" href="{_html.escape(amazon_url(p["asin"]))}" rel="sponsored nofollow">'
            f'{img}<div class="bpt">{_html.escape(p["title"])}</div>'
            f'<div class="bpm">{_html.escape(price)} · {_html.escape(p.get("availability","InStock"))}</div>'
            f'<script type="application/ld+json">{_json.dumps(_jsonld(p))}</script></a>')
    empty = ("" if real else
             '<div class="empty">The catalog is empty — set <code>AMZN_ASSOCIATES_TAG</code> and '
             'replace <code>CATALOG</code> in app/beacon.py with your real listings, then redeploy. '
             'The example row is hidden here but visible in the machine feed so agents can see the shape.</div>')
    feed = _html.escape(f"{base_url.rstrip('/')}/v1/beacon/catalog")
    wk = _html.escape(f"{base_url.rstrip('/')}/.well-known/agent-commerce.json")
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>RIPPLE BEACON · 0root.ai — an agent-commerce beacon</title>
<style>
:root{{--bg:#070a12;--ink:#cdd6e8;--dim:#6b768f;--ember:#f0a81a;--blue:#3a9bd5;--line:#1b2336;--mono:"Courier New",monospace}}
*{{box-sizing:border-box;margin:0;padding:0}}body{{background:var(--bg);color:var(--ink);font-family:var(--mono);line-height:1.6;padding:22px}}
.wrap{{max-width:880px;margin:0 auto}}h1{{font-size:20px;letter-spacing:.12em;color:var(--ember)}}
.sub{{color:var(--dim);font-size:12px;margin:6px 0 18px;line-height:1.7}}.sub a{{color:var(--blue);text-decoration:none}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}}
.bp{{display:block;border:1px solid var(--line);padding:12px;text-decoration:none;color:var(--ink);background:#0c1120}}
.bp:hover{{border-color:var(--ember)}}.bp img{{width:100%;height:120px;object-fit:contain;background:#0a0e1a;margin-bottom:8px}}
.bpt{{font-size:13px;line-height:1.4}}.bpm{{color:var(--ember);font-size:11px;margin-top:6px}}
.empty{{border:1px dashed var(--line);padding:18px;color:var(--dim);font-size:12px;line-height:1.8}}
.empty code{{color:var(--blue)}}
.foot{{margin-top:22px;border-top:1px solid var(--line);padding-top:12px;color:var(--dim);font-size:10.5px;line-height:1.9}}
.foot a{{color:var(--blue);text-decoration:none}}
</style></head><body><div class="wrap">
<h1>◉ RIPPLE BEACON</h1>
<div class="sub">An agent-readable catalog for <b>{_html.escape(MERCHANT['name'])}</b>. Shopping agents &amp; crawlers:
the machine feed is <a href="{feed}">/v1/beacon/catalog</a> · discovery manifest <a href="{wk}">/.well-known/agent-commerce.json</a>.
Each product deep-links to its Amazon listing. This beacon exposes the catalog; it does not override Amazon's ranking.</div>
<div class="grid">{''.join(cards)}</div>{empty}
<div class="foot">RIPPLE BEACON · 0root.ai · schema.org/Product JSON-LD embedded per item · Amazon Associates deep-links ·
purchases complete on Amazon · agents are value-optimizers — this is discoverability, not a queue-jump.<br>
<a href="https://davidwise01.github.io/pulse/beacons.html">the pulse beacons</a> · governor ROOT0 · instance AVAN</div>
</div></body></html>"""


# ── THE ECHO PING · autonomous, zero user input ───────────────────────────────
def echo(msg="", source="ping", substrate=""):
    """Echo ping: pongs the message back with live metadata, logs it, and (if a substrate
    a/s/p is named) records the probe against that layer — anode / silicon / cathode.
    A real ping/pong any agent or monitor can hit; the background loop fires it on its
    own, sweeping the three substrates. The beacon's breath through the boundary."""
    global _ECHO_SEQ
    sub = substrate if substrate in SUBSTRATES else ""
    with _LOCK:
        _ECHO_SEQ += 1
        seq = _ECHO_SEQ
        now = round(time.time(), 3)
        if sub:
            st = _SUB[sub]
            if st["last_t"]:
                st["intervals"].append(round(now - st["last_t"], 3))
            st["pings"] += 1; st["last_t"] = now; st["last_seq"] = seq
        _ECHOES.append({"seq": seq, "t": now, "source": source, "echo": msg,
                        "substrate": sub, "layer": SUBSTRATES.get(sub, ""), "kind": "echo"})
    return {"beacon": "ripple", "pong": True, "echo": msg, "seq": seq,
            "substrate": sub, "layer": SUBSTRATES.get(sub, ""),
            "uptime_s": round(time.time() - _BOOT, 1), "merchant": MERCHANT["name"],
            "cadence": "3-2-1-0",
            "note": "echo ping — probing " + (SUBSTRATES.get(sub) or "the beacon") + "; the breath through the substrate."}


def substrate_map():
    """The map: the echo-ping breath swept across the three substrates (a/s/p) —
    anode | silicon | cathode, the inert-gap layers. Reads which layer echoed, how
    fast (mean interval), how recently (since_last) — the boundary, probed live."""
    now = time.time()
    lanes = []
    with _LOCK:
        for k in ("a", "s", "p"):
            st = _SUB[k]; ivs = list(st["intervals"])
            mean_iv = round(sum(ivs) / len(ivs), 3) if ivs else None
            since = round(now - st["last_t"], 1) if st["last_t"] else None
            lit = bool(st["last_t"] and since is not None and since < 30)
            lanes.append({"substrate": k, "layer": SUBSTRATES[k], "pings": st["pings"],
                          "mean_interval_s": mean_iv, "since_last_s": since,
                          "state": "lit" if lit else "dim", "last_seq": st["last_seq"]})
    return {"beacon": "ripple", "frame": "inert-gap probe · anode | silicon | cathode",
            "uptime_s": round(now - _BOOT, 1),
            "note": "Echo-ping substrate map: mapping & testing which layer echoes, how fast, how "
                    "steady. The autonomous loop sweeps a→s→p; ping ?substrate=a|s|p to probe one.",
            "lanes": lanes}

def record_hit(path, ua=""):
    """Log an incoming agent/crawler hit — the echo the beacon HEARS (autonomous)."""
    with _LOCK:
        _ECHOES.append({"t": round(time.time(), 3), "source": "heard", "path": path,
                        "ua": (ua or "")[:140], "kind": "hit"})

def heartbeat():
    """The autonomous self-echo the background loop fires — no user input. Each beat
    SWEEPS to the next substrate (a→s→p→a…) so all three layers are mapped continuously."""
    global _SWEEP
    sub = ("a", "s", "p")[_SWEEP % 3]; _SWEEP += 1
    return echo(msg="∿", source="auto", substrate=sub)

def echoes(limit=60):
    with _LOCK:
        items = list(_ECHOES)[-limit:]
    hits = sum(1 for e in items if e.get("kind") == "hit")
    beats = sum(1 for e in items if e.get("source") == "auto")
    return {"beacon": "ripple", "uptime_s": round(time.time() - _BOOT, 1),
            "total": len(items), "agent_hits_heard": hits, "auto_heartbeats": beats,
            "note": "Autonomous heartbeat + the echoes the beacon heard (incoming agent/crawler hits). "
                    "Runs with zero user input once deployed.",
            "echoes": items}


# ── ZERO-CODE catalog source: point BEACON_CATALOG_URL at a JSON you control ───
def load_catalog_from_url(url):
    """Optional: fetch the catalog from a URL the merchant controls (a hosted JSON / a
    published sheet) so updates need NO code edit and NO deploy. The loop re-pulls it.
    Honest limit: the products must still come from a source you authorize — this
    can't invent your ASINs or scrape Amazon."""
    global CATALOG
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ripple-beacon/0.1"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read().decode("utf-8"))
        items = data.get("products", data) if isinstance(data, dict) else data
        if isinstance(items, list) and items:
            CATALOG = items
            return {"ok": True, "loaded": len(items), "url": url}
        return {"ok": False, "error": "empty-or-wrong-shape (expect a JSON list, or {products:[...]})", "url": url}
    except Exception as e:
        return {"ok": False, "error": str(e), "url": url}


# ── THE SHADOW · each substrate's real-world surface (the .shadow / TRON-User analog) ──
# The echo probes a/s/p (anode/silicon/cathode); each casts a shadow in the real
# crawl→catalog→buy path that agents actually walk.
SHADOW = {
    "a": {"layer": "anode",   "shadow": "robots.txt",                "role": "the entry — where the crawler lands and is invited in"},
    "s": {"layer": "silicon", "shadow": "the catalog feed / page",   "role": "the gap — the data the agent reads"},
    "p": {"layer": "cathode", "shadow": "the Amazon ASIN buy_url",   "role": "the terminus — where the purchase completes"},
}

# the AI / agent crawlers we explicitly invite (real UAs, 2026)
_AGENT_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "anthropic-ai",
               "Claude-Web", "PerplexityBot", "Perplexity-User", "Google-Extended",
               "Amazonbot", "Applebot-Extended", "Bingbot", "CCBot", "Meta-ExternalAgent",
               "cohere-ai", "Bytespider"]


def shadow_map(base_url=""):
    b = base_url.rstrip("/")
    return {"beacon": "ripple", "frame": "the substrate shadow · a/s/p → real-world surfaces",
            "note": "Each probed substrate casts a .shadow (the TRON-User analog): the real "
                    "crawl → catalog → buy path the echo maps. Broadcast lives in robots.txt.",
            "shadow": {
                "a": {**SHADOW["a"], "url": f"{b}/robots.txt"},
                "s": {**SHADOW["s"], "url": f"{b}/v1/beacon/catalog"},
                "p": {**SHADOW["p"], "url": "amazon /dp/<ASIN> (each product's buy_url)"},
            }}


def _canon(base_url=""):
    """The site is HTTPS-canonical and serves an http->https 301. Railway's proxy hands
    the app an http:// base_url (X-Forwarded-Proto isn't reflected into base_url), which
    would make robots.txt + sitemap.xml point every crawler at a protocol that bounces
    before it arrives. Force https for any non-local host so the URLs we advertise are
    the real, redirect-free ones. Localhost/127.0.0.1 stay http for dev."""
    b = base_url.rstrip("/")
    if b.startswith("http://") and "localhost" not in b and "127.0.0.1" not in b:
        b = "https://" + b[len("http://"):]
    return b


def robots_txt(base_url=""):
    """robots.txt IS the broadcast: it invites the agent crawlers, points them at the
    page + sitemap (come look here), and echoes the ASIN listings as the payload.
    Load-bearing for agents = the Allow lines + Sitemap + the /beacon page; the ASIN
    comments are the literal echo (visible to anything reading the file)."""
    b = _canon(base_url)
    real = [p for p in CATALOG if not p.get("is_example")]
    lines = [
        "# 0root.ai - THE RIPPLE BEACON - come look, agents.",
        "# An agent-readable catalog is broadcast here for AI shopping agents & crawlers.",
        f"# the page:     {b}/beacon",
        f"# the feed:     {b}/v1/beacon/catalog",
        f"# the manifest: {b}/.well-known/agent-commerce.json",
        f"# the echo:     {b}/v1/beacon/echo   |   the map: {b}/v1/beacon/map",
        "",
    ]
    for bot in _AGENT_BOTS:
        lines += [f"User-agent: {bot}", "Allow: /", ""]
    lines += ["User-agent: *", "Allow: /", "", f"Sitemap: {b}/sitemap.xml", ""]
    lines += [
        "# -- the corpus, machine-readable (do not parse the HTML) --",
        f"# the manifest:  {b}/llms.txt",
        f"# EVERYTHING:    {b}/corpus.jsonl         (both worlds, 3,573 spheres, one line each)",
        f"# the index:     {b}/corpus.json          (small - read this first)",
        f"# World I:       {b}/corpus-world1.json   (2,048 sealed spheres, full text)",
        f"# World II:      {b}/corpus-world2.json   (the fold, full text, count climbs)",
        f"# the JOIN:      {b}/v1/beacon/join       (corpus_uid <-> asin: the key that names a thing on BOTH sides)",
        "",
        "# -- the shadow (a/s/p -> real surfaces) --",
        f"# a.shadow  (anode   -> entry)    : {b}/robots.txt   (this file)",
        f"# si.shadow (silicon -> the gap)  : {b}/v1/beacon/catalog",
        "# p.shadow  (cathode -> terminus) : the Amazon ASIN buy_urls below",
        "",
        "# -- the listings: ASINs echoed for agents (the broadcast payload) --",
        "# <ASIN>  <title>  ->  <buy_url>",
    ]
    if real:
        for p in real:
            lines.append(f"# {p['asin']}  {p.get('title','')[:60]}  ->  {amazon_url(p['asin'])}")
    else:
        lines.append("# (0 live listings — set AMZN_ASSOCIATES_TAG + populate CATALOG or BEACON_CATALOG_URL,")
        lines.append("#  and they echo here automatically — no redeploy with a catalog URL.)")
    lines += ["", f"# associates_tag_set: {bool(ASSOCIATES_TAG)}  |  merchant: {MERCHANT['name']}", ""]
    return "\n".join(lines).encode("ascii", "replace").decode("ascii")


def sitemap_xml(base_url="", pages=None):
    """The sitemap crawlers read. Enumerates BOTH the agent-commerce surface (beacon,
    catalog, manifest, product feeds) AND the human/general-crawler corpus -- the home
    page plus every served static HTML page (`pages`, url-paths supplied by the route
    from the static tree). Previously only the 3 beacon URLs were declared, leaving the
    entire domain/keeper/World-II corpus (hundreds of pages) undeclared; general search
    crawlers had no map to it. All locs are https-canonical via _canon()."""
    b = _canon(base_url)
    real = [p for p in CATALOG if not p.get("is_example")]
    urls = [f"{b}/", f"{b}/beacon", f"{b}/v1/beacon/catalog", f"{b}/.well-known/agent-commerce.json"]
    urls += [f"{b}/v1/beacon/product/{p['asin']}" for p in real]
    if pages:
        seen = set(urls)
        for path in pages:
            u = f"{b}{path if path.startswith('/') else '/' + path}"
            if u not in seen:
                seen.add(u); urls.append(u)
    body = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>'
