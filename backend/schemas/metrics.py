from __future__ import annotations

from pydantic import BaseModel
from typing import Any


class DensityResponse(BaseModel):
    density: float
    directed: bool


class ErgmRequest(BaseModel):
    terms: list[str]  # e.g. ["edges", "mutual", "gwesp(0.5, fixed=TRUE)"]
    burnin: int = 10000
    samplesize: int = 10000
    interval: int = 1024
    seed: int = 42


class ErgmResponse(BaseModel):
    coefficients: dict[str, float]
    aic: float
    bic: float
    formula: str


class ComponentInfo(BaseModel):
    rank: int
    component_id: int
    size: int


class ConnectedComponentsResponse(BaseModel):
    count: int
    largest_size: int
    largest_id: int | None
    directed: bool
    mode: str
    components: list[ComponentInfo]


class ClusteringCoefficientRequest(BaseModel):
    mode: str = "global"  # "global" or "local"


class ClusteringCoefficientResponse(BaseModel):
    clustering_coefficient: float
    mode: str


class ReciprocityResponse(BaseModel):
    reciprocity: float | None
    directed: bool
    error: str | None = None
