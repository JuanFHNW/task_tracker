from __future__ import annotations
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, Session, create_engine

class Database:
    """Database facade as a Singleton."""
    _instance: Optional[Database] = None # Stores the single instance of the class

    def __new__(cls, *args, **kwargs) -> Database:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, database_url: Optional[str] = None, *, echo: bool = False) -> None:
        if getattr(self, "_initialized", False): # Skip if already initialized
            return
            
        self._database_url = database_url or os.getenv("DATABASE_URL") or self._default_sqlite_url()
        
        self._engine: Engine = create_engine(
            self._database_url, 
            echo=echo, 
            connect_args={"check_same_thread": False} #check_same_thread=False for NiceGUI
        )
        self.init_schema() # Automatically create tables on first startup
        self._initialized = True # Mark singleton as fully set up

    @staticmethod
    def _default_sqlite_url() -> str:
        """Create folder data if not exist."""
        Path("data").mkdir(parents=True, exist_ok=True)
        return "sqlite:///data/task_tracker.db"

    @property
    def engine(self) -> Engine:
        """Provides read-only access to the database engine"""
        return self._engine

    def init_schema(self) -> None:
        """Create all table"""
        SQLModel.metadata.create_all(self._engine)

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        """
        Facade for session. Initialize commit, rollback and close only here
        """
        session = Session(self._engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()