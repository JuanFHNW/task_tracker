from typing import Generic, TypeVar, Type, List, Optional
from sqlmodel import Session, select, SQLModel

# T is a type placeholder for any class that inherits from SQLModel
T = TypeVar("T", bound=SQLModel)

class BaseDAO(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        """
        Initialize the DAO with a database session and the target model type.
        """
        self.session = session
        self.model = model

    def get_by_id(self, obj_id: int) -> Optional[T]:
        """Fetch a single record by its primary key ID."""
        return self.session.get(self.model, obj_id)

    def get_all(self) -> List[T]:
        """Fetch all records for this model from the database."""
        statement = select(self.model)
        return self.session.exec(statement).all()

    def create(self, obj: T) -> T:
        """
        Add a new object to the session. 
        Note: The commit is handled by the session_scope in db.py.
        """
        self.session.add(obj)
        return obj

    def delete(self, obj_id: int) -> bool:
        """Delete a record by its ID. Returns True if successful."""
        obj = self.get_by_id(obj_id)
        if obj:
            self.session.delete(obj)
            return True
        return False