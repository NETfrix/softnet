from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...core.tasks import task_manager

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}")
async def get_task_status(task_id: str):
    record = task_manager.get(task_id)
    if record is None:
        raise HTTPException(404, "Task not found")

    response = {
        "id": record.id,
        "project_id": record.project_id,
        "task_type": record.task_type,
        "status": record.status.value,
        "progress": record.progress,
    }

    if record.status.value == "completed" and record.result is not None:
        # Only include serializable result data
        if isinstance(record.result, dict):
            response["result"] = record.result
    elif record.status.value == "failed":
        response["error"] = record.error

    return response


@router.delete("/{task_id}")
async def cancel_task(task_id: str):
    if not task_manager.cancel(task_id):
        raise HTTPException(404, "Task not found or not running")
    return {"cancelled": True}
