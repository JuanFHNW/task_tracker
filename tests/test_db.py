from task_tracker_app.data_access.db import Database
from task_tracker_app.data_access.dao import UserDAO, TaskDAO, TaskInstanceDAO
from task_tracker_app.models.user import User
from task_tracker_app.models.task import Task
from task_tracker_app.models.enums import Priority
from task_tracker_app.models.task_instance import TaskInstance
from datetime import datetime


def test_init_schema_and_user_creation(database: Database):
    # Arrange (database fixture ensures fresh DB)
    with database.session_scope() as session:
        user_dao = UserDAO(session)

        # Act
        new_user = User(username="bob", password="pass")
        user_dao.create(new_user)
        session.flush()
        session.refresh(new_user)

        # Assert
        assert new_user.id is not None
        found = user_dao.get_by_username("bob")
        assert found is not None and found.id == new_user.id


def test_daos_save_and_retrieve(database: Database, user: User):
    # Arrange
    with database.session_scope() as session:
        task_dao = TaskDAO(session)
        inst_dao = TaskInstanceDAO(session)

        # Act
        task = Task(description="DB test", priority=Priority.MEDIUM, user_id=user.id)
        task_dao.create(task)
        session.flush()
        session.refresh(task)

        inst = TaskInstance(task_id=task.id, due_date=datetime.utcnow())
        inst_dao.create(inst)
        session.flush()

        # Assert
        tasks = task_dao.get_tasks_by_user(user.id)
        assert any(t.id == task.id for t in tasks)
        pending = inst_dao.get_pending_instances(task.id)
        assert any(i.task_id == task.id for i in pending)


def test_transaction_rollback_on_exception(database: Database):
    # Arrange
    try:
        with database.session_scope() as session:
            user_dao = UserDAO(session)
            user = User(username="temp", password="x")
            user_dao.create(user)
            session.flush()
            # Simulate failure
            raise RuntimeError("boom")
    except RuntimeError:
        pass

    # Assert: user was not persisted
    with database.session_scope() as session:
        user_dao = UserDAO(session)
        assert user_dao.get_by_username("temp") is None
