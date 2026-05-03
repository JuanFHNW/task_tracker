from typing import List, Optional
from sqlmodel import Session, select
from .base_dao import BaseDAO
from task_tracker_app.models.user import User
from task_tracker_app.models.task import Task
from task_tracker_app.models.task_instance import TaskInstance


class UserDAO(BaseDAO[User]):
    """DAO for User-related database operations."""
    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_by_username(self, username: str) -> Optional[User]:
        """Find a user by their unique username."""
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()

class TaskDAO(BaseDAO[Task]):
    """DAO for Task (Master) database operations."""
    def __init__(self, session: Session):
        super().__init__(session, Task)

    def get_tasks_by_user(self, user_id: int) -> List[Task]:
        """Fetch all master tasks belonging to a specific user."""
        statement = select(Task).where(Task.user_id == user_id)
        return self.session.exec(statement).all()

class TaskInstanceDAO(BaseDAO[TaskInstance]):
    """DAO for TaskInstance (Execution) database operations."""
    def __init__(self, session: Session):
        super().__init__(session, TaskInstance)

    def get_pending_instances(self, task_id: int) -> List[TaskInstance]:
        """Retrieve all instances of a task that are not yet completed."""
        statement = select(TaskInstance).where(
            TaskInstance.task_id == task_id,
            TaskInstance.completed_at == None
        )
        return self.session.exec(statement).all()
    
    def get_full_history(self, task_id: int) -> List[TaskInstance]:
        """Get every execution record for a specific task master."""
        statement = select(TaskInstance).where(TaskInstance.task_id == task_id)
        return self.session.exec(statement).all()