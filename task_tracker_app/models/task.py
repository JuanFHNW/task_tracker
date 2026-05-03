from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from .enums import Priority, Interval

if TYPE_CHECKING:
    from .user import User
    from .task_instance import TaskInstance

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    priority: Priority = Field(default=Priority.MEDIUM)
    interval: Optional[Interval] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    is_visible: bool = Field(default=True)
    
    user_id: int = Field(foreign_key="user.id")
    
    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    instances: List["TaskInstance"] = Relationship(back_populates="task")