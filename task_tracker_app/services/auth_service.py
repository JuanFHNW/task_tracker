"""Authentication service (Developer 2)."""

from task_tracker_app.data_access.db import Database
from task_tracker_app.data_access.dao import UserDAO
from task_tracker_app.models.user import User


class AuthService:
    """Verifies credentials and registers users."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def authenticate(self, username: str, password: str) -> User | None:
        """Return the user if credentials match, otherwise None."""
        with self.database.session_scope() as session:
            user_dao = UserDAO(session)
            user = user_dao.get_by_username(username)
            if user is None:
                return None
            if user.password != password:
                return None
            # Force load of all simple fields before the session closes
            session.refresh(user)
            return user

    def register(self, username: str, password: str) -> User:
        """Create a new user. Raises ValueError if the username is taken."""
        with self.database.session_scope() as session:
            user_dao = UserDAO(session)
            if user_dao.get_by_username(username) is not None:
                raise ValueError(f"Username '{username}' is already registered.")
            user = User(username=username, password=password)
            user_dao.create(user)
            session.flush()
            session.refresh(user)
            return user
