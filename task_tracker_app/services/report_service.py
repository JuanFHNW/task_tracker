"""Productivity reporting service (Developer 2).

Aggregates TaskInstance data for a given user and serialises it to CSV
so the UI can offer a "Download Report" button.
"""

import csv
import io
from datetime import datetime

from task_tracker_app.data_access.db import Database
from task_tracker_app.data_access.dao import TaskDAO, TaskInstanceDAO
from task_tracker_app.models.task import Task
from task_tracker_app.models.task_instance import TaskInstance
from task_tracker_app.services.task_service import is_overdue, duration_seconds


CSV_HEADER: tuple[str, ...] = (
    "task_id",
    "description",
    "priority",
    "instance_id",
    "due_date",
    "started_at",
    "completed_at",
    "status",
    "duration_seconds",
    "is_overdue",
)


class ReportService:
    """Builds CSV reports of a user's task history."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def generate_report(self, user_id: int) -> tuple[bytes, str]:
        """Return a (csv_bytes, filename) pair for the given user."""
        rows = self._collect_rows(user_id)

        buffer = io.StringIO(newline="")
        writer = csv.writer(buffer)
        writer.writerow(CSV_HEADER)
        writer.writerows(rows)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"task_report_user{user_id}_{timestamp}.csv"
        return buffer.getvalue().encode("utf-8"), filename

    # ---------- internals ----------

    def _collect_rows(self, user_id: int) -> list[tuple]:
        with self.database.session_scope() as session:
            task_dao = TaskDAO(session)
            instance_dao = TaskInstanceDAO(session)
            tasks = task_dao.get_tasks_by_user(user_id)

            rows: list[tuple] = []
            for task in tasks:
                instances = instance_dao.get_full_history(task.id)
                for inst in instances:
                    rows.append(_row_for(task, inst))
            return rows


def _row_for(task: Task, inst: TaskInstance) -> tuple:
    return (
        task.id,
        task.description,
        task.priority.value,
        inst.id,
        _fmt(inst.due_date),
        _fmt(inst.started_at),
        _fmt(inst.completed_at),
        inst.status.value,
        duration_seconds(inst),
        is_overdue(inst),
    )


def _fmt(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.isoformat(timespec="seconds")
