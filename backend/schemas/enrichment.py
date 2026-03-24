from __future__ import annotations

from pydantic import BaseModel
from typing import Any


class EnrichmentRequest(BaseModel):
    node_ids: list[str]
    sources: list[str] = ["wikipedia"]  # wikipedia, wikidata


class EnrichmentResult(BaseModel):
    node_id: str
    source: str
    data: dict[str, Any]


class EnrichmentResponse(BaseModel):
    results: list[EnrichmentResult]
