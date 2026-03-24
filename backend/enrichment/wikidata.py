from __future__ import annotations

import httpx


async def enrich_from_wikidata(node_id: str) -> dict:
    """Query Wikidata API for a node identifier."""
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": node_id,
        "language": "en",
        "limit": 1,
        "format": "json",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    results = data.get("search", [])
    if not results:
        return {"source": "wikidata", "found": False, "node_id": node_id}

    entity = results[0]
    entity_id = entity["id"]

    # Get entity details
    detail_params = {
        "action": "wbgetentities",
        "ids": entity_id,
        "languages": "en",
        "props": "labels|descriptions|claims",
        "format": "json",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=detail_params)
        resp.raise_for_status()
        data = resp.json()

    entity_data = data.get("entities", {}).get(entity_id, {})
    label = entity_data.get("labels", {}).get("en", {}).get("value", "")
    description = entity_data.get("descriptions", {}).get("en", {}).get("value", "")

    return {
        "source": "wikidata",
        "found": True,
        "node_id": node_id,
        "entity_id": entity_id,
        "label": label,
        "description": description,
        "url": f"https://www.wikidata.org/wiki/{entity_id}",
    }
