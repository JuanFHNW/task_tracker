import pytest
from datetime import datetime

from task_tracker_app.services.task_service import TaskService, _next_due_date
from task_tracker_app.models.enums import Priority, Interval


def test_create_task_spawns_instance(database, user):
    # Arrange
    svc = TaskService(database)
    due = datetime.utcnow()

    # Act
    task = svc.create_task("integ task", Priority.MEDIUM, user.id, due_date=due)

    # Assert
    with database.session_scope() as session:
        # refresh via DAOs
        from task_tracker_app.data_access.dao import TaskInstanceDAO

        inst_dao = TaskInstanceDAO(session)
        pending = inst_dao.get_pending_instances(task.id)
        assert len(pending) == 1
        assert pending[0].due_date == due


def test_mark_completed_creates_next_for_recurring(database, user):
    # Arrange
    svc = TaskService(database)
    due = datetime.utcnow()

    # Act / Assert for multiple intervals inside one test
    for interval in (Interval.DAILY, Interval.WEEKLY, Interval.MONTHLY):
        task = svc.create_task("recurring", Priority.MEDIUM, user.id, interval=interval, due_date=due)
        next_instance = svc.mark_completed(task.id, user.id)
        assert next_instance is not None
        expected = _next_due_date(due, interval)
        assert next_instance.due_date == expected


def test_mark_completed_one_time_returns_none(database, user):
    # Arrange
    svc = TaskService(database)
    due = datetime.utcnow()
    task = svc.create_task("one-time", Priority.MEDIUM, user.id, due_date=due)

    # Act
    nxt = svc.mark_completed(task.id, user.id)

    # Assert
    assert nxt is None
