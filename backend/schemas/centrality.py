from __future__ import annotations

from pydantic import BaseModel


class CentralityRequest(BaseModel):
    algorithm: str  # degree, betweenness, closeness, pagerank
    directed: bool = True
    mode: str = "all"  # all, in, out (for degree)
    damping: float = 0.85  # for pagerank
    normalized: bool = True
    cutoff: int | None = None  # for betweenness


class CentralityResponse(BaseModel):
    algorithm: str
    values: dict[str, float]
    min: float
    max: float
    mean: float
