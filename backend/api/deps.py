from fastapi import HTTPException

from ..core.graph_store import store
from ..core.project import ProjectState


def get_project(project_id: str) -> ProjectState:
    project = store.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return project
