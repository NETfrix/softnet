from pydantic import BaseModel


class LayoutRequest(BaseModel):
    algorithm: str  # forceatlas2, yifan_hu
    iterations: int = 100
    scaling: float = 2.0
    gravity: float = 1.0
    strong_gravity: bool = False
    barnes_hut: bool = True


class LayoutResponse(BaseModel):
    algorithm: str
    key: str
    node_count: int
