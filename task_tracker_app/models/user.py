from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .task import Task

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Verknüpfung zu den Tasks
    tasks: List["Task"] = Relationship(back_populates="user")