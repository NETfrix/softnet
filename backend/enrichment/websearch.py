from __future__ import annotations

import httpx


async def enrich_from_websearch(node_id: str) -> dict:
    """Search the web for information about a node using DuckDuckGo Instant Answer API."""
    url = "https://api.duckduckgo.com/"
    params = {
        "q": node_id,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    abstract = data.get("Abstract", "")
    abstract_url = data.get("AbstractURL", "")
    heading = data.get("Heading", "")
    image = data.get("Image", "")

    # Check related topics if no abstract
    related = []
    for topic in data.get("RelatedTopics", [])[:5]:
        if isinstance(topic, dict) and "Text" in topic:
            related.append(topic["Text"])

    if not abstract and not related:
        return {"source": "websearch", "found": False, "node_id": node_id}

    result = {
        "source": "websearch",
        "found": True,
        "node_id": node_id,
        "title": heading or node_id,
        "url": abstract_url,
        "extract": abstract or "; ".join(related[:3]),
    }
    if image:
        result["thumbnail"] = f"https://duckduckgo.com{image}" if image.startswith("/") else image

    return result
