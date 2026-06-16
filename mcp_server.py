"""
Ripple Beacon · MCP server (optional).

Exposes the merchant catalog to MCP-native agents as two tools — search_products
and get_product — so any MCP client (Claude, etc.) can discover the listings and
follow the Amazon buy_url. This is the agent-native twin of the HTTP /v1/beacon/*
endpoints; it reads the SAME catalog from app/beacon.py (single source of truth).

Run (stdio):   pip install "mcp[cli]"   then   python mcp_server.py
Honest scope:  discovery only. Purchase completes on Amazon via the buy_url; this
server does not (and must not) transact on Amazon on an agent's behalf. See
RIPPLE_BEACON.md for the 2026 reality (Amazon blocks external buying agents).
"""
try:
    from mcp.server.fastmcp import FastMCP
except Exception as e:  # pragma: no cover
    raise SystemExit("MCP SDK not installed. Run:  pip install \"mcp[cli]\"\n(" + str(e) + ")")

from app import beacon

mcp = FastMCP("ripple-beacon")


@mcp.tool()
def search_products(query: str, limit: int = 20) -> dict:
    """Search the merchant's catalog by keywords. Returns ranked products, each with a
    `buy_url` deep-linking to the Amazon listing where the purchase completes.
    Re-rank by your own value criteria — this order is keyword relevance only."""
    return beacon.search(query, limit)


@mcp.tool()
def get_product(asin: str) -> dict:
    """Get one product by its Amazon ASIN — the agent view plus its schema.org/Product JSON-LD."""
    return beacon.get_product(asin)


@mcp.tool()
def list_catalog() -> dict:
    """The full machine feed of the merchant's catalog, with honest limits and the 2026 real-levers note."""
    return beacon.catalog_feed()


if __name__ == "__main__":
    mcp.run()
