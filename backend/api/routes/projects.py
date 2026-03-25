from __future__ import annotations

import os
import tempfile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ...core.graph_store import store
from ...core.tasks import task_manager
from ...ingest.api_connector import fetch_graph_from_api
from ...ingest.csv_parser import parse_edge_csv, parse_node_csv
from ...ingest.gexf_parser import parse_gexf
from ...ingest.gephi_parser import parse_gephi
from ...ingest.graphml_parser import parse_graphml
from ...layout.forceatlas2 import compute_forceatlas2
from ...layout.utils import normalize_positions
from ...schemas.project import ApiConnectorParams, ProjectMeta

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/upload", status_code=201)
async def upload_graph(
    file: UploadFile = File(...),
    node_file: UploadFile | None = File(None),
    name: str = Form("Untitled"),
    directed: bool = Form(False),
    delimiter: str = Form(","),
    source_col: str = Form("source"),
    target_col: str = Form("target"),
    weight_col: str | None = Form(None),
):
    """Upload a graph file (CSV, GEXF, or GraphML)."""
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    try:
        if ext == ".csv" or ext == ".tsv":
            delim = "\t" if ext == ".tsv" else delimiter
            graph = parse_edge_csv(
                file.file,
                delimiter=delim,
                source_col=source_col,
                target_col=target_col,
                weight_col=weight_col,
                directed=directed,
            )
        elif ext == ".gexf":
            graph = parse_gexf(file.file)
            directed = graph.is_directed()
        elif ext in (".graphml", ".xml"):
            graph = parse_graphml(file.file)
            directed = graph.is_directed()
        elif ext == ".gephi":
            graph = parse_gephi(file.file)
            directed = graph.is_directed()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {ext}. Use .csv, .gexf, .graphml, or .gephi",
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Add node attributes from separate file if provided
    if node_file is not None:
        try:
            parse_node_csv(graph, node_file.file, delimiter=delimiter)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Node file error: {e}")

    project = store.create_project(graph=graph, name=name, directed=directed)

    # Compute default layout in background
    async def _compute_default_layout():
        positions = compute_forceatlas2(graph, iterations=50, barnes_hut=True)
        project.layouts["default"] = normalize_positions(positions)

    task_id = await task_manager.submit(
        project.id,
        "layout",
        lambda: _compute_default_layout_sync(project),
    )

    return {
        "project": project.metadata(),
        "layout_task_id": task_id,
    }


def _compute_default_layout_sync(project):
    positions = compute_forceatlas2(project.graph, iterations=50, barnes_hut=True)
    project.layouts["default"] = normalize_positions(positions)


@router.post("/from-api", status_code=201)
async def import_from_api(params: ApiConnectorParams):
    """Pull graph data from a REST API endpoint."""
    try:
        graph = await fetch_graph_from_api(
            endpoint=params.endpoint,
            headers=params.headers,
            node_path=params.node_path,
            edge_path=params.edge_path,
            source_field=params.source_field,
            target_field=params.target_field,
            directed=params.directed,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"API import failed: {e}")

    project = store.create_project(graph=graph, name=params.name, directed=params.directed)

    task_id = await task_manager.submit(
        project.id,
        "layout",
        lambda: _compute_default_layout_sync(project),
    )

    return {
        "project": project.metadata(),
        "layout_task_id": task_id,
    }


@router.get("")
async def list_projects():
    return store.list_projects()


@router.get("/{project_id}")
async def get_project(project_id: str):
    project = store.get(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project.metadata()


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    if not store.delete(project_id):
        raise HTTPException(404, "Project not found")
    return {"deleted": True}
