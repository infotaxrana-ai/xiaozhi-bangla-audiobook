"""MCP server for a curated Bengali literary audio catalog."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any
from fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = Path(os.getenv("AUDIO_CATALOG", ROOT / "data" / "catalog.json"))
EXAMPLE_PATH = ROOT / "data" / "catalog.example.json"
AUTHORS_PATH = ROOT / "data" / "authors.json"
mcp = FastMCP("Xiaozhi Bangla Audio Library")

def load_catalog() -> list[dict[str, Any]]:
    """Load imported records plus the hand-curated catalog."""
    items: list[dict[str, Any]] = []
    for path in (ROOT / "data" / "commons-import.json", ROOT / "data" / "podcast-import.json", CATALOG_PATH):
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            raise ValueError(f"Catalog root must be a JSON array: {path}")
        items.extend(item for item in data if isinstance(item, dict))
    if not items and EXAMPLE_PATH.exists():
        with EXAMPLE_PATH.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        items.extend(item for item in data if isinstance(item, dict))
    unique: dict[str, dict[str, Any]] = {}
    for item in items:
        unique[str(item.get("audio_url") or item.get("id") or "")] = item
    return list(unique.values())

def load_authors() -> list[dict[str, Any]]:
    if not AUTHORS_PATH.exists():
        return []
    with AUTHORS_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data.get("authors", []) if isinstance(data, dict) else []

def author_matches(item: dict[str, Any], author: dict[str, Any]) -> bool:
    if item.get("author_id") == author["id"]:
        return True
    haystack = " ".join(str(item.get(k, "")) for k in
                        ("title", "author", "performer", "description", "tags")).casefold()
    return any(alias.casefold() in haystack for alias in author.get("aliases", []))

def playable(item: dict[str, Any]) -> bool:
    url = item.get("audio_url", "")
    return item.get("verified") is True and isinstance(url, str) and url.startswith(("https://", "http://"))

def public_item(item: dict[str, Any]) -> dict[str, Any]:
    result = {k: v for k, v in item.items() if k != "internal_notes"}
    if not playable(item):
        result.pop("audio_url", None)
        result["playable"] = False
        result["verification_notice"] = "Direct audio URL has not been verified."
    else:
        result["playable"] = True
    return result

@mcp.tool()
def search_bangla_audio(query: str = "", category: str = "", author: str = "", limit: int = 10) -> dict[str, Any]:
    """Search Bengali audio by title, author, genre, or poet/writer alias."""
    terms = [x.casefold().strip() for x in (query, category) if x.strip()]
    author_term = author.casefold().strip()
    authors = load_authors()
    matched_authors = [a for a in authors if author_term and
                       (author_term == a["id"].casefold() or
                        any(author_term in alias.casefold() or alias.casefold() in author_term
                            for alias in a.get("aliases", [])))]
    limit = max(1, min(int(limit), 30))
    found = []
    for item in load_catalog():
        haystack = " ".join(str(item.get(k, "")) for k in
                            ("title", "author", "performer", "category", "description", "tags")).casefold()
        text_ok = all(term in haystack for term in terms)
        author_ok = not author_term or any(author_matches(item, a) for a in matched_authors) or author_term in haystack
        if text_ok and author_ok:
            found.append(public_item(item))
        if len(found) >= limit:
            break
    return {"count": len(found), "items": found}

@mcp.tool()
def list_authors(query: str = "") -> dict[str, Any]:
    """List the author/poet directory with catalog item counts; filter by name or alias."""
    items = load_catalog()
    term = query.casefold().strip()
    results = []
    for author in load_authors():
        if term and not any(term in value.casefold() for value in
                            [author["id"], author["name_bn"], author["name_en"], *author.get("aliases", [])]):
            continue
        count = sum(1 for item in items if author_matches(item, author))
        results.append({"id": author["id"], "name_bn": author["name_bn"],
                        "name_en": author["name_en"], "aliases": author.get("aliases", []),
                        "categories": author.get("categories", []), "catalog_item_count": count})
    return {"count": len(results), "authors": results}

@mcp.tool()
def get_audio_item(item_id: str) -> dict[str, Any]:
    """Get one catalog item by ID; direct audio URL is returned only if verified."""
    for item in load_catalog():
        if str(item.get("id", "")) == item_id:
            return public_item(item)
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
            "author_count": len(load_authors()),
            "note": "Only verified=true entries with HTTP(S) audio_url are playable."}

if __name__ == "__main__":
    mcp.run(transport="stdio")
