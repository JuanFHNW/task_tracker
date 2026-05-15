import pytest
from datetime import datetime, timedelta

from task_tracker_app.services.task_service import (
    _next_due_date,
    is_overdue,
    duration_seconds,
)
from task_tracker_app.models.task_instance import TaskInstance
from task_tracker_app.models.enums import Interval


@pytest.mark.parametrize(
    "interval,days",
    [
        (Interval.DAILY, 1),
        (Interval.WEEKLY, 7),
        (Interval.MONTHLY, 30),
    ],
)
def test_next_due_date_intervals(interval, days):
    # Arrange
    now = datetime(2026, 5, 1, 12, 0, 0)

    # Act
    next_due = _next_due_date(now, interval)

    # Assert
    assert next_due - now == timedelta(days=days)


def test_next_due_date_unsupported_raises():
    # Arrange
    now = datetime.utcnow()

    # Act / Assert
    with pytest.raises(ValueError):
        _next_due_date(now, object())


def test_is_overdue_true_and_false():
    # Arrange
    now = datetime(2026, 5, 15, 12, 0, 0)
    past = now - timedelta(days=1)
    equal = now

    overdue_instance = TaskInstance(due_date=past, completed_at=None)
    equal_time_instance = TaskInstance(due_date=equal, completed_at=None)
    completed_instance = TaskInstance(due_date=past, completed_at=now)

    # Act / Assert
    assert is_overdue(overdue_instance, now) is True
    assert is_overdue(equal_time_instance, now) is False
    assert is_overdue(completed_instance, now) is False


def test_duration_seconds_none_when_incomplete():
    # Arrange
    inst = TaskInstance(due_date=datetime.utcnow(), started_at=None, completed_at=None)

    # Act
    dur = duration_seconds(inst)

    # Assert
    assert dur is None


def test_duration_seconds_positive_and_negative():
    # Arrange
    start = datetime(2026, 5, 15, 9, 0, 0)
    end = datetime(2026, 5, 15, 10, 30, 0)
    inst_pos = TaskInstance(due_date=start, started_at=start, completed_at=end)

    # Negative duration (bug/edge) — allowed but should compute correctly
    inst_neg = TaskInstance(due_date=start, started_at=end, completed_at=start)

    # Act
    dur_pos = duration_seconds(inst_pos)
    dur_neg = duration_seconds(inst_neg)

    # Assert
    assert dur_pos == 90 * 60  # 1.5 hours in seconds
    assert dur_neg == -90 * 60


def test_is_overdue_equal_time_not_overdue():
    # Arrange
    now = datetime(2026, 5, 15, 12, 0, 0)
    inst = TaskInstance(due_date=now, completed_at=None)

    # Act
    result = is_overdue(inst, now)

    # Assert
    assert result is False
