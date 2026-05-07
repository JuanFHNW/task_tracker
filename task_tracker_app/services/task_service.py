"""Task lifecycle service (Developer 2).

Owns the business rules for tasks and their execution instances:
creation (master + first instance in one transaction), starting and
finishing instances, and automatic renewal of recurring tasks.
"""

from datetime import datetime, timedelta

from task_tracker_app.data_access.db import Database
from task_tracker_app.data_access.dao import TaskDAO, TaskInstanceDAO
from task_tracker_app.models.task import Task
from task_tracker_app.models.task_instance import TaskInstance
from task_tracker_app.models.enums import Priority, Interval, Status


# ---- module-level helpers ----------------------------------------------------

def _next_due_date(current: datetime, interval: Interval) -> datetime:
    """Return the due date of the next instance in a recurring series."""
    if interval == Interval.DAILY:
        return current + timedelta(days=1)
    if interval == Interval.WEEKLY:
        return current + timedelta(weeks=1)
    if interval == Interval.MONTHLY:
        # 30-day approximation keeps us inside the standard library
        return current + timedelta(days=30)
    raise ValueError(f"Unsupported interval: {interval}")


def is_overdue(instance: TaskInstance, now: datetime | None = None) -> bool:
    """An instance is overdue if not completed and its due date has passed."""
    reference = now or datetime.utcnow()
    return instance.completed_at is None and instance.due_date < reference


def duration_seconds(instance: TaskInstance) -> float | None:
    """Return how long the instance took, or None if not yet finished."""
    if instance.started_at is None or instance.completed_at is None:
        return None
    return (instance.completed_at - instance.started_at).total_seconds()


# ---- service ----------------------------------------------------------------

class TaskService:
    """Coordinates Task and TaskInstance operations through DAOs."""

    def __init__(self, database: Database) -> None:
        self.database = database

    # ---------- create ----------

    def create_task(
        self,
        description: str,
        priority: Priority,
        user_id: int,
        interval: Interval | None = None,
        end_date: datetime | None = None,
        due_date: datetime | None = None,
    ) -> Task:
        """Create the master Task and its first TaskInstance in one transaction."""
        first_due = due_date or datetime.utcnow()

        with self.database.session_scope() as session:
            task_dao = TaskDAO(session)
            instance_dao = TaskInstanceDAO(session)

            task = Task(
                description=description,
                priority=priority,
                interval=interval,
                end_date=end_date,
                user_id=user_id,
            )
            task_dao.create(task)
            session.flush()  # populates task.id before building the instance

            first_instance = TaskInstance(
                task_id=task.id,
                due_date=first_due,
                status=Status.TODO,
            )
            instance_dao.create(first_instance)
            session.flush()
            session.refresh(task)
            return task

    # ---------- read ----------

    def list_tasks(self, user_id: int) -> list[Task]:
        """Return the user's visible master tasks."""
        with self.database.session_scope() as session:
            task_dao = TaskDAO(session)
            tasks = task_dao.get_tasks_by_user(user_id)
            return [t for t in tasks if t.is_visible]

    def get_task(self, task_id: int) -> Task | None:
        with self.database.session_scope() as session:
            task_dao = TaskDAO(session)
            return task_dao.get_by_id(task_id)

    def get_task_with_history(self, task_id: int) -> dict:
        """Return {'task': Task, 'instances': list[TaskInstance]} for master-detail."""
        with self.database.session_scope() as session:
            task_dao = TaskDAO(session)
            instance_dao = TaskInstanceDAO(session)
            task = task_dao.get_by_id(task_id)
            if task is None:
                return {"task": None, "instances": []}
            instances = instance_dao.get_full_history(task_id)
            return {"task": task, "instances": instances}

    # ---------- update / delete ----------

    def update_task(
        self,
        task_id: int,
        user_id: int,
        description: str | None = None,
        priority: Priority | None = None,
        interval: Interval | None = None,
        end_date: datetime | None = None,
        is_visible: bool | None = None,
    ) -> bool:
        """Update mutable master-task fields. Returns True on success."""
        with self.database.session_scope() as session:
            task_dao = TaskDAO(session)
            task = task_dao.get_by_id(task_id)
            if task is None or task.user_id != user_id:
                return False

            if description is not None:
                task.description = description
            if priority is not None:
                task.priority = priority
            if interval is not None:
                task.interval = interval
            if end_date is not None:
                task.end_date = end_date
            if is_visible is not None:
                task.is_visible = is_visible

            session.add(task)
            return True

    def delete_task(self, task_id: int, user_id: int) -> None:
        """Soft-delete: hide the task. Raises PermissionError if not the owner."""
        with self.database.session_scope() as session:
            task_dao = TaskDAO(session)
            task = task_dao.get_by_id(task_id)
            if task is None:
                raise ValueError(f"Task {task_id} does not exist.")
            if task.user_id != user_id:
                raise PermissionError("You do not own this task.")
            task.is_visible = False
            session.add(task)

    # ---------- execution lifecycle ----------

    def mark_started(self, task_id: int, user_id: int) -> TaskInstance:
        """Mark the current pending instance as in progress."""
        with self.database.session_scope() as session:
            task_dao = TaskDAO(session)
            instance_dao = TaskInstanceDAO(session)

            task = task_dao.get_by_id(task_id)
            if task is None or task.user_id != user_id:
                raise PermissionError("Task not found or not owned by user.")

            pending = instance_dao.get_pending_instances(task_id)
            if not pending:
                raise ValueError(f"No pending instance for task {task_id}.")

            current = pending[0]
            current.started_at = datetime.utcnow()
            current.status = Status.IN_PROGRESS
            session.add(current)
            session.flush()
            session.refresh(current)
            return current

    def mark_completed(self, task_id: int, user_id: int) -> TaskInstance | None:
        """Finish the current instance and, for recurring tasks, queue the next.

        Returns the newly created next instance, or None for one-time tasks.
        """
        now = datetime.utcnow()
        with self.database.session_scope() as session:
            task_dao = TaskDAO(session)
            instance_dao = TaskInstanceDAO(session)

            task = task_dao.get_by_id(task_id)
            if task is None or task.user_id != user_id:
                raise PermissionError("Task not found or not owned by user.")

            pending = instance_dao.get_pending_instances(task_id)
            if not pending:
                raise ValueError(f"No pending instance for task {task_id}.")

            current = pending[0]
            current.completed_at = now
            current.status = Status.DONE
            if current.started_at is None:
                current.started_at = now
            session.add(current)

            if task.interval is None:
                return None

            next_due = _next_due_date(current.due_date, task.interval)
            if task.end_date is not None and next_due > task.end_date:
                return None

            next_instance = TaskInstance(
                task_id=task.id,
                due_date=next_due,
                status=Status.TODO,
            )
            instance_dao.create(next_instance)
            session.flush()
            session.refresh(next_instance)
            return next_instance
