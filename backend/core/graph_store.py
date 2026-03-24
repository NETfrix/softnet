from __future__ import annotations

import threading
from typing import Optional

import igraph as ig

from .project import ProjectState


class GraphStore:
    """Thread-safe in-memory registry of loaded graph projects."""

    def __init__(self) -> None:
        self._projects: dict[str, ProjectState] = {}
        self._lock = threading.Lock()

    def create_project(
        self, graph: ig.Graph, name: str, directed: bool
    ) -> ProjectState:
        project_id = ProjectState.new_id()
        project = ProjectState(
            id=project_id, name=name, graph=graph, directed=directed
        )
        with self._lock:
            self._projects[project_id] = project
        return project

    def get(self, project_id: str) -> Optional[ProjectState]:
        with self._lock:
            return self._projects.get(project_id)

    def list_projects(self) -> list[dict]:
        with self._lock:
            return [p.metadata() for p in self._projects.values()]

    def delete(self, project_id: str) -> bool:
        with self._lock:
            return self._projects.pop(project_id, None) is not None

    def exists(self, project_id: str) -> bool:
        with self._lock:
            return project_id in self._projects


# Singleton
store = GraphStore()
