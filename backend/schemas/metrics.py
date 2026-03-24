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
