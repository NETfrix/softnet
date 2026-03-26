from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...api.deps import get_project
from ...core.graph_store import store
from ...core.tasks import task_manager
from ...analysis.bipartite import detect_bipartite, project_bipartite
from ...layout.forceatlas2 import compute_forceatlas2
from ...layout.utils import normalize_positions

router = APIRouter(prefix="/projects/{project_id}/bipartite", tags=["bipartite"])


@router.get("")
async def check_bipartite(project_id: str):
    """Check if the graph is bipartite."""
    project = get_project(project_id)
    result = detect_bipartite(project.graph)
    return result


class ProjectionRequest(BaseModel):
    which: int = 0  # 0 or 1


@router.post("/project")
async def project_graph(project_id: str, req: ProjectionRequest):
    """Project a bipartite graph onto one node type, creating a new project."""
    project = get_project(project_id)

    if not project.graph.is_bipartite():
        raise HTTPException(400, "Graph is not bipartite")

    projected = project_bipartite(project.graph, which=req.which)
    new_project = store.create_project(
        graph=projected,
        name=f"{project.name} (projection {req.which})",
        directed=False,
    )

    # Compute layout for the new project
    task_id = await task_manager.submit(
        new_project.id,
        "layout",
        lambda: _layout(new_project),
    )

    return {
        "project": new_project.metadata(),
        "layout_task_id": task_id,
    }


def _layout(project):
    positions = compute_forceatlas2(project.graph, iterations=50, barnes_hut=True)
    project.layouts["default"] = normalize_positions(positions)
