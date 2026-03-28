from __future__ import annotations

import io
import os

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ...core.graph_store import store
from ...core.tasks import task_manager
from ...ingest.api_connector import fetch_graph_from_api
from ...ingest.csv_parser import parse_csv_auto, parse_node_csv
from ...ingest.gexf_parser import parse_gexf
from ...ingest.gephi_parser import parse_gephi
from ...ingest.excel_parser import parse_excel
from ...ingest.graphml_parser import parse_graphml
from ...layout.forceatlas2 import compute_forceatlas2
from ...layout.utils import normalize_positions
from ...schemas.project import ApiConnectorParams

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/upload", status_code=201)
async def upload_graph(
    file: UploadFile = File(...),
    node_file: UploadFile | None = File(None),
    name: str = Form("Untitled"),
    directed: bool = Form(False),
):
    """Upload a graph file. Supports CSV, TSV, GEXF, GraphML, and Gephi formats.
    CSV format is auto-detected: edge list, adjacency matrix, or adjacency list.
    Source/target columns are auto-detected from headers.
    Node attribute file is optional."""
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    try:
        if ext in (".csv", ".tsv", ".txt"):
            graph = parse_csv_auto(file.file, directed=directed)
        elif ext == ".gexf":
            graph = parse_gexf(file.file)
            directed = graph.is_directed()
        elif ext in (".graphml", ".xml"):
            graph = parse_graphml(file.file)
            directed = graph.is_directed()
        elif ext == ".gephi":
            graph = parse_gephi(file.file)
            directed = graph.is_directed()
        elif ext in (".xlsx", ".xls"):
            file.file.seek(0)
            raw = file.file.read()
            graph = parse_excel(io.BytesIO(raw), directed=directed)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {ext}. Use .csv, .xlsx, .gexf, .graphml, or .gephi",
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Add node attributes from separate file if provided
    if node_file is not None and node_file.filename:
        try:
            parse_node_csv(graph, node_file.file)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Node file error: {e}")

    project = store.create_project(graph=graph, name=name, directed=directed)

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
