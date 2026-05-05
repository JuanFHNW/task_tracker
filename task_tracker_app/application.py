"""TaskTracker application – Composition Root (Developer 4)."""

from __future__ import annotations

from nicegui import ui

from .data_access.db import Database
from .data_access.dao import TaskDAO, UserDAO  
from .services.task_service import TaskService
from .services.auth_service import AuthService   
from .ui.controllers import TaskController, AuthController
from .ui.pages import Pages


class TaskApplication:
    """Main application wiring following clean architecture."""

    def __init__(self) -> None:
        self.database = Database()
        self.database.init_schema_and_seed()

        engine = self.database.engine

        # Persistence Layer
        self.user_dao = UserDAO(engine)
        self.task_dao = TaskDAO(engine)

        # Service Layer
        self.auth_service = AuthService(user_dao=self.user_dao)
        self.task_service = TaskService(task_dao=self.task_dao)

        # Controller Layer (You)
        self.auth_controller = AuthController(auth_service=self.auth_service)
        self.task_controller = TaskController(task_service=self.task_service)

        # UI Layer
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
            title="TaskTracker",
            storage_secret="your-super-secret-key-change-in-production"
        )