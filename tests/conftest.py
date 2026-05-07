"""Shared pytest fixtures for service-layer tests.

Each test gets a fresh in-memory SQLite database. The Database facade
is a Singleton, so we reset its class attribute between tests.
"""

import pytest

from task_tracker_app.data_access.db import Database
from task_tracker_app.models.user import User
from task_tracker_app.data_access.dao import UserDAO


@pytest.fixture
def database(tmp_path) -> Database:
    """Return a fresh file-backed SQLite Database for one test."""
    Database._instance = None
    db_path = tmp_path / "test.db"
    db = Database(database_url=f"sqlite:///{db_path}", echo=False)
    yield db
    Database._instance = None


@pytest.fixture
def user(database: Database) -> User:
    """Insert a baseline user so tests can attach tasks to a real user_id."""
    with database.session_scope() as session:
        user_dao = UserDAO(session)
        new_user = User(username="alice", password="secret")
        user_dao.create(new_user)
        session.flush()
        session.refresh(new_user)
        return new_user
