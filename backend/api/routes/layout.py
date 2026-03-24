from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...api.deps import get_project
from ...core.tasks import task_manager
from ...layout.forceatlas2 import compute_forceatlas2
from ...layout.yifan_hu import compute_yifan_hu
from ...layout.utils import normalize_positions
from ...schemas.layout import LayoutRequest, LayoutResponse

router = APIRouter(prefix="/projects/{project_id}/layout", tags=["layout"])


@router.post("", status_code=202)
async def compute_layout(project_id: str, req: LayoutRequest):
    project = get_project(project_id)

    def _compute():
        if req.algorithm == "forceatlas2":
            positions = compute_forceatlas2(
                project.graph,
                iterations=req.iterations,
                scaling=req.scaling,
                gravity=req.gravity,
                strong_gravity=req.strong_gravity,
                barnes_hut=req.barnes_hut,
            )
        elif req.algorithm == "yifan_hu":
            positions = compute_yifan_hu(project.graph)
        else:
            raise ValueError(f"Unknown layout algorithm: {req.algorithm}")

        normalized = normalize_positions(positions)
        key = req.algorithm
        project.layouts[key] = normalized
        return {"algorithm": req.algorithm, "key": key, "node_count": len(normalized)}

    task_id = await task_manager.submit(project_id, f"layout_{req.algorithm}", _compute)
    return {"task_id": task_id, "algorithm": req.algorithm}


@router.get("")
async def list_layouts(project_id: str):
    project = get_project(project_id)
    return {"layouts": list(project.layouts.keys())}


@router.get("/{key}")
async def get_layout(project_id: str, key: str):
    project = get_project(project_id)
    layout = project.layouts.get(key)
    if layout is None:
        raise HTTPException(404, f"Layout '{key}' not computed yet")
    return LayoutResponse(algorithm=key, key=key, node_count=len(layout))
