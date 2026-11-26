"""MCP server for a curated Bengali literary audio catalog."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any
from fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = Path(os.getenv("AUDIO_CATALOG", ROOT / "data" / "catalog.json"))
EXAMPLE_PATH = ROOT / "data" / "catalog.example.json"
mcp = FastMCP("Xiaozhi Bangla Audio Library")

def load_catalog() -> list[dict[str, Any]]:
    """Load catalog entries. Missing user catalog means an empty catalog."""
    path = CATALOG_PATH if CATALOG_PATH.exists() else EXAMPLE_PATH
    if not path.exists(): return []
    with path.open("r", encoding="utf-8") as handle: data = json.load(handle)
    if not isinstance(data, list): raise ValueError("Catalog root must be a JSON array")
    return [item for item in data if isinstance(item, dict)]

def playable(item: dict[str, Any]) -> bool:
    url = item.get("audio_url", "")
    return item.get("verified") is True and isinstance(url, str) and url.startswith(("https://", "http://"))

def public_item(item: dict[str, Any]) -> dict[str, Any]:
    """Never expose unverified URLs as playable links."""
    result = {k: v for k, v in item.items() if k != "internal_notes"}
    if not playable(item):
        result.pop("audio_url", None)
        result["playable"] = False
        result["verification_notice"] = "Direct audio URL has not been verified."
    else: result["playable"] = True
    return result

@mcp.tool()
def search_bangla_audio(query: str = "", category: str = "", author: str = "", limit: int = 10) -> dict[str, Any]:
    """Search Bengali audiobook, story podcast, poetry and recitation entries."""
    terms = [x.casefold().strip() for x in (query, category, author) if x.strip()]
    limit = max(1, min(int(limit), 30))
    found = []
    for item in load_catalog():
        haystack = " ".join(str(item.get(k, "")) for k in ("title","author","performer","category","description","tags")).casefold()
        if all(term in haystack for term in terms): found.append(public_item(item))
        if len(found) >= limit: break
    return {"count": len(found), "items": found}

@mcp.tool()
def get_audio_item(item_id: str) -> dict[str, Any]:
    """Get one catalog item by ID; direct audio URL is returned only if verified."""
    for item in load_catalog():
        if str(item.get("id", "")) == item_id: return public_item(item)
    return {"error": "not_found", "message": f"No audio item with id: {item_id}"}

@mcp.tool()
def list_audio_categories() -> dict[str, Any]:
    """List categories present in the current catalog and their item counts."""
    counts: dict[str, int] = {}
    for item in load_catalog():
        category = str(item.get("category", "uncategorized"))
        counts[category] = counts.get(category, 0) + 1
    return {"categories": [{"name": k, "count": v} for k, v in sorted(counts.items())]}

@mcp.tool()
def get_catalog_status() -> dict[str, Any]:
    """Show catalog size and count of verified direct audio URLs."""
    items = load_catalog()
    return {"catalog_path": str(CATALOG_PATH), "total_items": len(items),
            "verified_playable_items": sum(1 for item in items if playable(item)),
            "note": "Only verified=true entries with HTTP(S) audio_url are playable."}

if __name__ == "__main__":
    mcp.run(transport="stdio")
