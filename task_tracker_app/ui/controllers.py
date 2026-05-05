"""UI Controllers – Orchestration layer (Developer 4)."""

from __future__ import annotations
from datetime import date
from typing import Optional

from nicegui import app

from domain.models import Task
from services.task_service import TaskService
from services.auth_service import AuthService

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

    def logout(self) -> None:
        app.storage.user.clear()

    def is_authenticated(self) -> bool:
        return app.storage.user.get("authenticated", False)

    def get_current_username(self) -> str:
        return app.storage.user.get("username", "Guest")


class TaskController:
    """Orchestrates task operations between UI and business logic."""

    def __init__(self, task_service: TaskService) -> None:
        self.task_service = task_service

    def create_task(self, title: str, description: str | None = None,
                    due_date: date | None = None, priority: str = "Medium",
                    task_type: str = "OneTime") -> Task:
        """Create a new task."""
        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            task_type=task_type,
            # user_id will be set in service or here using current user
        )
        return self.task_service.create_task(task)

    def list_tasks(self) -> list[Task]:
        return self.task_service.list_tasks()

    def get_task(self, task_id: int) -> Task | None:
        return self.task_service.get_task(task_id)

    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update task with flexible keyword arguments."""
        task = self.task_service.get_task(task_id)
        if not task:
            return False

        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)

        self.task_service.update_task(task)
        return True

    def delete_task(self, task_id: int) -> bool:
        try:
            self.task_service.delete_task(task_id)
            return True
        except Exception:
            return False

    def mark_completed(self, task_id: int) -> bool:
        try:
            self.task_service.mark_completed(task_id)
            return True
        except Exception:
            return False

    def generate_report(self) -> tuple[bytes, str]:
        """Returns (csv_bytes, filename)"""
        return self.task_service.generate_report()