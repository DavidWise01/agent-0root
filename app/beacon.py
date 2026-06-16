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
def echo(msg="", source="ping"):
    """Echo ping: returns the message back with live beacon metadata, and logs the ping.
    A real ping/pong — any agent or monitor can hit it for proof-of-life; the
    background loop calls it on its own (no user input). The beacon's breath."""
    global _ECHO_SEQ
    with _LOCK:
        _ECHO_SEQ += 1
        seq = _ECHO_SEQ
        _ECHOES.append({"seq": seq, "t": round(time.time(), 3), "source": source,
                        "echo": msg, "kind": "echo"})
    return {"beacon": "ripple", "pong": True, "echo": msg, "seq": seq,
            "uptime_s": round(time.time() - _BOOT, 1), "merchant": MERCHANT["name"],
            "cadence": "3-2-1-0", "note": "echo ping — the beacon is live and listening; this is its breath."}

def record_hit(path, ua=""):
    """Log an incoming agent/crawler hit — the echo the beacon HEARS (autonomous)."""
    with _LOCK:
        _ECHOES.append({"t": round(time.time(), 3), "source": "heard", "path": path,
                        "ua": (ua or "")[:140], "kind": "hit"})

def heartbeat():
    """The autonomous self-echo the background loop fires — no user input."""
    return echo(msg="∿", source="auto")

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
