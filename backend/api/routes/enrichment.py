from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException

from ...api.deps import get_project
from ...enrichment.cache import enrichment_cache
from ...enrichment.websearch import enrich_from_websearch
from ...enrichment.wikipedia import enrich_from_wikipedia
from ...enrichment.wikidata import enrich_from_wikidata
from ...schemas.enrichment import EnrichmentRequest, EnrichmentResponse, EnrichmentResult

router = APIRouter(prefix="/projects/{project_id}/enrich", tags=["enrichment"])

_SOURCES = {
    "wikipedia": enrich_from_wikipedia,
    "wikidata": enrich_from_wikidata,
    "websearch": enrich_from_websearch,
}


@router.post("")
async def enrich_nodes(project_id: str, req: EnrichmentRequest):
    project = get_project(project_id)

    # Validate node IDs exist
    valid_ids = set(project.node_ids)
    invalid = [nid for nid in req.node_ids if nid not in valid_ids]
    if invalid:
        raise HTTPException(400, f"Unknown node IDs: {invalid[:5]}")

    results: list[EnrichmentResult] = []

    for source_name in req.sources:
        if source_name not in _SOURCES:
            raise HTTPException(400, f"Unknown source: {source_name}. Options: {list(_SOURCES)}")

        fn = _SOURCES[source_name]
        tasks = []
        for node_id in req.node_ids:
            cache_key = f"{source_name}:{node_id}"
            cached = enrichment_cache.get(cache_key)
            if cached:
                results.append(EnrichmentResult(node_id=node_id, source=source_name, data=cached))
            else:
                tasks.append((node_id, cache_key))

        # Fetch uncached in parallel (limited concurrency)
        sem = asyncio.Semaphore(5)

        async def _fetch(nid: str, ckey: str):
            async with sem:
                data = await fn(nid)
                enrichment_cache.set(ckey, data)
                return EnrichmentResult(node_id=nid, source=source_name, data=data)

        if tasks:
            fetched = await asyncio.gather(*[_fetch(nid, ck) for nid, ck in tasks])
            results.extend(fetched)

    # Update project enrichment cache
    for r in results:
        project.enrichment_cache[r.node_id] = r.data

    return EnrichmentResponse(results=results)


@router.get("/{node_id}")
async def get_enrichment(project_id: str, node_id: str):
    project = get_project(project_id)
    data = project.enrichment_cache.get(node_id)
    if data is None:
        raise HTTPException(404, f"No enrichment data for node '{node_id}'")
    return data
