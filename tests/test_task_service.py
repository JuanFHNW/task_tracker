"""Tests for TaskService — the heart of Dev 2's logic layer."""

from datetime import datetime, timedelta

import pytest

from task_tracker_app.data_access.dao import TaskInstanceDAO
from task_tracker_app.models.enums import Priority, Interval, Status
from task_tracker_app.services.task_service import (
    TaskService,
    is_overdue,
    duration_seconds,
    _next_due_date,
)


def test_create_task_persists_master_and_first_instance(database, user):
    service = TaskService(database)

    task = service.create_task(
        description="Buy groceries",
        priority=Priority.MEDIUM,
        user_id=user.id,
    )

    assert task.id is not None
    with database.session_scope() as session:
        instances = TaskInstanceDAO(session).get_full_history(task.id)
    assert len(instances) == 1
    assert instances[0].status == Status.TODO


def test_mark_completed_one_time_task_creates_no_followup(database, user):
    service = TaskService(database)
    task = service.create_task(
        description="Submit report",
        priority=Priority.HIGH,
        user_id=user.id,
    )

    next_inst = service.mark_completed(task.id, user_id=user.id)

    assert next_inst is None
    with database.session_scope() as session:
        instances = TaskInstanceDAO(session).get_full_history(task.id)
    assert len(instances) == 1
    assert instances[0].status == Status.DONE


def test_mark_completed_recurring_task_spawns_next_instance(database, user):
    """User case TC_012: completing a daily task creates the next-day instance."""
    service = TaskService(database)
    today = datetime.utcnow()
    task = service.create_task(
        description="Drink water",
        priority=Priority.LOW,
        user_id=user.id,
        interval=Interval.DAILY,
        due_date=today,
    )

    next_inst = service.mark_completed(task.id, user_id=user.id)

    assert next_inst is not None
    assert next_inst.status == Status.TODO
    expected = today + timedelta(days=1)
    assert abs((next_inst.due_date - expected).total_seconds()) < 1


def test_recurring_task_stops_when_end_date_reached(database, user):
    service = TaskService(database)
    today = datetime.utcnow()
    task = service.create_task(
        description="Short series",
        priority=Priority.MEDIUM,
        user_id=user.id,
        interval=Interval.DAILY,
        due_date=today,
        end_date=today + timedelta(hours=12),  # next due (+1d) would exceed
    )

    next_inst = service.mark_completed(task.id, user_id=user.id)
    assert next_inst is None


def test_mark_started_sets_status_and_timestamp(database, user):
    service = TaskService(database)
    task = service.create_task(
        description="Write tests",
        priority=Priority.HIGH,
        user_id=user.id,
    )

    started = service.mark_started(task.id, user_id=user.id)

    assert started.status == Status.IN_PROGRESS
    assert started.started_at is not None


def test_update_task_rejects_foreign_user(database, user):
    service = TaskService(database)
    task = service.create_task(
        description="Mine",
        priority=Priority.LOW,
        user_id=user.id,
    )

    ok = service.update_task(task.id, user_id=user.id + 999, description="Hacked")
    assert ok is False


def test_delete_task_rejects_foreign_user(database, user):
    service = TaskService(database)
    task = service.create_task(
        description="Mine",
        priority=Priority.LOW,
        user_id=user.id,
    )

    with pytest.raises(PermissionError):
        service.delete_task(task.id, user_id=user.id + 999)


def test_list_tasks_excludes_invisible(database, user):
    service = TaskService(database)
    keep = service.create_task("Keep", Priority.LOW, user.id)
    hide = service.create_task("Hide", Priority.LOW, user.id)
    service.delete_task(hide.id, user_id=user.id)

    listed = service.list_tasks(user.id)
    descriptions = [t.description for t in listed]
    assert "Keep" in descriptions
    assert "Hide" not in descriptions


def test_get_task_with_history_returns_task_and_instances(database, user):
    service = TaskService(database)
    task = service.create_task("Run", Priority.MEDIUM, user.id)

    bundle = service.get_task_with_history(task.id)

    assert bundle["task"].id == task.id
    assert len(bundle["instances"]) == 1


# ---- pure-function helpers ---------------------------------------------------

@pytest.mark.parametrize(
    "interval, days",
    [(Interval.DAILY, 1), (Interval.WEEKLY, 7), (Interval.MONTHLY, 30)],
)
def test_next_due_date(interval, days):
    base = datetime(2026, 1, 1, 12, 0)
    result = _next_due_date(base, interval)
    assert result == base + timedelta(days=days)


def test_is_overdue_true_for_past_uncompleted():
    """User case TC_011: a deadline in the past flags as overdue."""
    from task_tracker_app.models.task_instance import TaskInstance
    inst = TaskInstance(task_id=1, due_date=datetime(2020, 1, 1))
    assert is_overdue(inst) is True


def test_is_overdue_false_when_completed():
    from task_tracker_app.models.task_instance import TaskInstance
    inst = TaskInstance(
        task_id=1,
        due_date=datetime(2020, 1, 1),
        completed_at=datetime(2020, 1, 2),
    )
    assert is_overdue(inst) is False


def test_duration_seconds_none_when_not_finished():
    from task_tracker_app.models.task_instance import TaskInstance
    inst = TaskInstance(task_id=1, due_date=datetime(2026, 1, 1))
    assert duration_seconds(inst) is None


def test_duration_seconds_computes_difference():
    from task_tracker_app.models.task_instance import TaskInstance
    started = datetime(2026, 1, 1, 9, 0, 0)
    completed = datetime(2026, 1, 1, 9, 0, 30)
    inst = TaskInstance(
        task_id=1,
        due_date=started,
        started_at=started,
        completed_at=completed,
    )
    assert duration_seconds(inst) == pytest.approx(30.0)
