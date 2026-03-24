from pydantic import BaseModel


class GraphDataParams(BaseModel):
    layout: str = "default"
    size_attr: str | None = None
    color_attr: str | None = None
