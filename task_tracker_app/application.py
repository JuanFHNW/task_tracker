"""TaskTracker application – Composition Root (Developer 4)."""

from __future__ import annotations

from nicegui import ui

from .data_access.db import Database
from .data_access.dao import UserDAO, TaskDAO, TaskInstanceDAO
from .services.auth_service import AuthService
from .services.report_service import ReportService
from .services.task_service import TaskService
from .ui.controllers import AuthController, TaskController
from .ui.pages import Pages


class TaskApplication:
    """Main application wiring following clean architecture."""

    def __init__(self) -> None:
        # 1. Database
        self.database = Database()
        self.database.init_schema()

        # 2. Service Layer
        self.auth_service = AuthService(database=self.database)
        self.task_service = TaskService(database=self.database)
        self.report_service = ReportService(database=self.database)

        # 3. Controller Layer 
        self.auth_controller = AuthController(auth_service=self.auth_service)
        self.task_controller = TaskController(
            task_service=self.task_service,
            report_service=self.report_service,
        )

        # 4. UI Layer 
        self.pages = Pages(
            auth_controller=self.auth_controller,
            task_controller=self.task_controller
        )

    def run(self, host: str = "0.0.0.0", port: int = 8080, reload: bool = True) -> None:
        """Start the NiceGUI web application."""
        self.pages.register()
        ui.run(
            host=host,
            port=port,
            reload=reload,
            title="Task Tracker Pro",
            storage_secret="your-super-secret-key-change-in-production"
        )