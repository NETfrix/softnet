from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from ...api.deps import get_project
from ...core.serializers import serialize_graph_for_sigma

router = APIRouter(prefix="/projects/{project_id}", tags=["visualization"])


@router.get("/graph")
async def get_graph_data(
    project_id: str,
    layout: str = Query("default"),
    size_attr: str | None = Query(None),
    color_attr: str | None = Query(None),
):
    """Return full graph data as MessagePack binary for Sigma.js rendering."""
    project = get_project(project_id)

    data = serialize_graph_for_sigma(
        project,
        layout_key=layout,
        node_size_attr=size_attr,
        color_attr=color_attr,
    )

    return Response(
        content=data,
        media_type="application/x-msgpack",
        headers={
            "Content-Encoding": "identity",
            "Cache-Control": "no-cache",
        },
    )
