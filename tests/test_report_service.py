"""Tests for ReportService."""

from task_tracker_app.models.enums import Priority
from task_tracker_app.services.report_service import ReportService, CSV_HEADER
from task_tracker_app.services.task_service import TaskService


def test_generate_report_returns_csv_bytes_with_header(database, user):
    task_service = TaskService(database)
    task_service.create_task("First", Priority.MEDIUM, user.id)
    task_service.create_task("Second", Priority.HIGH, user.id)

    report = ReportService(database)
    payload, filename = report.generate_report(user_id=user.id)

    assert isinstance(payload, bytes)
    assert filename.endswith(".csv")
    text = payload.decode("utf-8")
    first_line = text.splitlines()[0]
    assert first_line == ",".join(CSV_HEADER)


def test_generate_report_has_one_row_per_instance(database, user):
    task_service = TaskService(database)
    task_service.create_task("A", Priority.LOW, user.id)
    task_service.create_task("B", Priority.LOW, user.id)

    report = ReportService(database)
    payload, _ = report.generate_report(user_id=user.id)

    lines = payload.decode("utf-8").strip().splitlines()
    # 1 header + 2 instances (one per task on creation)
    assert len(lines) == 3


def test_summary_counts_completed_and_total(database, user):
    task_service = TaskService(database)
    t1 = task_service.create_task("A", Priority.LOW, user.id)
    task_service.create_task("B", Priority.LOW, user.id)
    task_service.mark_completed(t1.id, user_id=user.id)

    report = ReportService(database)
    stats = report.summary(user_id=user.id)

    assert stats["total_tasks"] == 2
    assert stats["total_instances"] == 2
    assert stats["completed"] == 1
