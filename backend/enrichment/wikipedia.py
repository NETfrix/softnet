from __future__ import annotations

import httpx


async def enrich_from_wikipedia(node_id: str) -> dict:
    """Query Wikipedia API for a node identifier."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": node_id,
        "srlimit": 1,
        "format": "json",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    results = data.get("query", {}).get("search", [])
    if not results:
        return {"source": "wikipedia", "found": False, "node_id": node_id}

    page = results[0]
    page_id = page["pageid"]
    title = page["title"]

    # Get extract
    extract_params = {
        "action": "query",
        "pageids": page_id,
        "prop": "extracts|pageimages",
        "exintro": True,
        "explaintext": True,
        "pithumbsize": 200,
        "format": "json",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=extract_params)
        resp.raise_for_status()
        data = resp.json()

    page_data = data.get("query", {}).get("pages", {}).get(str(page_id), {})

    return {
        "source": "wikipedia",
        "found": True,
        "node_id": node_id,
        "title": title,
        "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
        "extract": page_data.get("extract", ""),
        "thumbnail": page_data.get("thumbnail", {}).get("source"),
    }
