from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from .enums import Status

if TYPE_CHECKING:
    from .task import Task

class TaskInstance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    
    due_date: datetime
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    status: Status = Field(default=Status.TODO)
    
    # Relationship zurück zum Master
    task: "Task" = Relationship(back_populates="instances")