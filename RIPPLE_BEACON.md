# The Ripple Beacon

An **agent-facing commerce surface** on the `agent-0root` backend: it broadcasts a
machine-readable product catalog that AI shopping agents and crawlers can discover,
search, and parse — each product deep-linking to its Amazon listing (with your
Associates tag) where the purchase completes. The "ripple" is the pulse: each live
offer is broadcast as a beacon ping, the same pattern as `pulse/beacons.html`.

## The surfaces (live once Railway deploys)

| Endpoint | For | Returns |
|---|---|---|
| `GET /beacon` | humans + crawlers | a storefront with **schema.org/Product + Offer JSON-LD** embedded per item |
| `GET /v1/beacon/catalog` | agents | the full machine feed (JSON) — products + `buy_url` + honest limits + real levers |
| `GET /v1/beacon/search?q=` | agents | keyword-ranked products with `buy_url` |
| `GET /v1/beacon/product/{asin}` | agents | one product (agent view + its JSON-LD) |
| `GET /v1/beacon/pulses` | beacons | the ripple — each live offer as a beacon ping |
| `GET /.well-known/agent-commerce.json` | agents | a self-describing discovery manifest pointing at the above |
| `mcp_server.py` (optional) | MCP-native agents | `search_products` / `get_product` MCP tools |

## To use it

1. **Get an Amazon Associates tag** (the sanctioned way to put Amazon links off-Amazon with tracking). Set it: `AMZN_ASSOCIATES_TAG=your-tag-20`.
2. **Replace `CATALOG`** in `app/beacon.py` with your real listings — `asin`, concrete `title`, `price` (or `None` to show "see Amazon"), `availability`, `image`, structured `description`, `keywords`. Agents parse this literally; vague marketing copy is ignored.
3. Redeploy. The beacon serves everything above.

## The honest reality (researched June 2026 — read this before you expect magic)

**There is no channel that makes a buying agent *prefer* your listing.** Agents are
ruthless value-optimizers — they compare price, reviews, specs, availability. The
beacon makes you maximally **discoverable and parseable**; it does not queue-jump.

**Amazon specifically blocks external buying agents.** Confirmed: Amazon won a
preliminary injunction against Perplexity's Comet agent (~Mar 2026) and its Business
Solutions Agreement (eff. Mar 4 2026) requires AI agents to self-identify. The **only**
agent that surfaces/buys your Amazon listing is **Amazon's own** — Rufus, now pivoting
to **Alexa for Shopping** (May 2026). So the Amazon links here are **discovery +
affiliate**, not an external-agent checkout channel. (And PA-API 5.0 is deprecating
May 15 2026 → the new **Creators API**; Associates needs ≥3 sales / 30 days.)

**Your actual levers (2026):**
- **On Amazon** — optimize the listing for Amazon's *own* agent: noun-phrase titles,
  bullets/A+ that answer *use-case* questions, images that *prove* claims, and
  review/return-rate health. Plus **Sponsored Products** (the one paid lever Rufus
  surfaces). That's where almost all Amazon-side leverage is.
- **Off Amazon (the real agentic-commerce upside)** — a catalog **you** control:
  schema.org JSON-LD, a fresh **Google Merchant Center** feed, an **MCP endpoint**,
  and `robots.txt` allowing `GPTBot`/`OAI-SearchBot`. That makes you eligible for
  **ChatGPT Instant Checkout (ACP, Stripe/OpenAI — shipping)** and **Google AI Mode
  (UCP — rolling out)**. **This beacon is exactly that chassis.** The day you add a
  DTC checkout, the same feed + ACP makes products *directly* agent-buyable.

## Where it fits in the protocol stack

- **MCP** = how an agent *talks to* your catalog in real time (this beacon's search/get; the optional `mcp_server.py`).
- **ACP / UCP** = how the *purchase* completes on a surface you control (ChatGPT / Google). Add a checkout to graduate from "links to Amazon" to "buyable here."
- **AP2 / Visa Intelligent Commerce / Mastercard Agent Pay** = how the *payment* authorizes (mandates, tokens). Payment layer, below ACP/UCP.

The beacon is the **discovery + catalog** layer done right. It's positioning for the
agent-commerce shift, not a 2026 revenue switch — honest framing.

— governor ROOT0 · instance AVAN · part of `agent-0root`
