"""UI Controllers – Orchestration layer"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from nicegui import app

from task_tracker_app.models.task import Task
from task_tracker_app.models.user import User
from task_tracker_app.models.enums import Priority, Interval

from task_tracker_app.services.task_service import TaskService
from task_tracker_app.services.auth_service import AuthService
from task_tracker_app.services.report_service import ReportService


class AuthController:
    """Handles all authentication-related logic for the UI."""

    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def login(self, username: str, password: str) -> bool:
        """Authenticate user and set session."""
        user = self.auth_service.authenticate(username, password)
        if user:
            app.storage.user.update({
                "authenticated": True,
                "user_id": user.id,
                "username": user.username
            })
            return True
        return False

    def register(self, username: str, password: str) -> User:
        """Create a user account through the auth service."""
        return self.auth_service.register(username, password)

    def logout(self) -> None:
        app.storage.user.clear()

    def is_authenticated(self) -> bool:
        return app.storage.user.get("authenticated", False)

    def get_current_user_id(self) -> Optional[int]:
        """Helper used by TaskController."""
        return app.storage.user.get("user_id")

    def get_current_username(self) -> str:
        return app.storage.user.get("username", "Guest")


class TaskController:
    """Orchestrates task operations between UI and business logic."""

    def __init__(self, task_service: TaskService, report_service: ReportService) -> None:
        self.task_service = task_service
        self.report_service = report_service

    def get_current_user_id(self) -> int:
        user_id = app.storage.user.get("user_id")
        if not user_id:
            raise PermissionError("User not authenticated")
        return user_id

    # ==================== CREATE ====================
    def create_task(
        self,
        description: str,
        priority: str = "MEDIUM",
        interval: str | None = None,           # "DAILY", "WEEKLY", etc. or None
        end_date: datetime | None = None,      # For recurring series end
        due_date: datetime | None = None       # For first instance (one-time or initial)
    ) -> Task:
        """Create a new master Task + first TaskInstance."""
        user_id = self.get_current_user_id()

        return self.task_service.create_task(
            description=description,
            priority=Priority(priority.upper()),
            user_id=user_id,
            interval=Interval(interval) if interval else None,
            end_date=end_date,
            due_date=due_date
        )

    # ==================== READ ====================
    def list_tasks(self) -> List[Task]:
        """List only the current user's visible master tasks."""
        user_id = self.get_current_user_id()
        return self.task_service.list_tasks(user_id=user_id)

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a single task (with ownership check in service)."""
        return self.task_service.get_task(task_id)

    def get_task_with_history(self, task_id: int) -> dict:
        """Useful for master-detail view: task + all its instances."""
        return self.task_service.get_task_with_history(task_id)

    # ==================== UPDATE / DELETE ====================
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update task fields (description, priority, interval, etc.)."""
        user_id = self.get_current_user_id()
        return self.task_service.update_task(task_id, user_id=user_id, **kwargs)

    def delete_task(self, task_id: int) -> bool:
        user_id = self.get_current_user_id()
        try:
            self.task_service.delete_task(task_id, user_id=user_id)
            return True
        except Exception:
            return False

    # ==================== EXECUTION (Instances) ====================
    def mark_started(self, task_id: int) -> bool:
        """Start working on the current pending instance."""
        user_id = self.get_current_user_id()
        try:
            self.task_service.mark_started(task_id, user_id=user_id)
            return True
        except Exception:
            return False

    def mark_completed(self, task_id: int) -> bool:
        """Finish current instance. Handles recurring logic if needed."""
        user_id = self.get_current_user_id()
        try:
            self.task_service.mark_completed(task_id, user_id=user_id)
            return True
        except Exception:
            return False

    # ==================== REPORTING ====================
    def generate_report(self) -> tuple[bytes, str]:
        """Returns (csv_bytes, filename)"""
        user_id = self.get_current_user_id()
        return self.report_service.generate_report(user_id=user_id)