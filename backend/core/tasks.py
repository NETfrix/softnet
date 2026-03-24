from __future__ import annotations

import asyncio
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskRecord:
    id: str
    project_id: str
    task_type: str
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None
    progress: float = 0.0


class TaskManager:
    def __init__(self, max_workers: int = 4) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: dict[str, TaskRecord] = {}

    async def submit(
        self,
        project_id: str,
        task_type: str,
        fn: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        task_id = uuid.uuid4().hex[:12]
        record = TaskRecord(
            id=task_id, project_id=project_id, task_type=task_type
        )
        self._tasks[task_id] = record

        loop = asyncio.get_event_loop()
        record.status = TaskStatus.RUNNING

        def _run() -> Any:
            try:
                result = fn(*args, **kwargs)
                record.result = result
                record.status = TaskStatus.COMPLETED
                record.progress = 1.0
                return result
            except Exception as e:
                record.error = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
                record.status = TaskStatus.FAILED
                raise

        loop.run_in_executor(self._executor, _run)
        return task_id

    def get(self, task_id: str) -> TaskRecord | None:
        return self._tasks.get(task_id)

    def cancel(self, task_id: str) -> bool:
        record = self._tasks.get(task_id)
        if record and record.status == TaskStatus.RUNNING:
            record.status = TaskStatus.FAILED
            record.error = "Cancelled by user"
            return True
        return False


# Singleton
task_manager = TaskManager()
