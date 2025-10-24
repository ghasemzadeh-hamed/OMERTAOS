from datetime import datetime
from typing import Optional
from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    role: str = Field(default='user')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tasks: list['Task'] = Relationship(back_populates='owner')


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str | None = None
    owner_id: int = Field(foreign_key='user.id')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tasks: list['Task'] = Relationship(back_populates='project')


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: str = Field(index=True)
    intent: str
    params: dict = Field(sa_column=Column(JSON))
    preferred_engine: str | None = None
    priority: int = 1
    status: str = Field(default='queued')
    result: dict | None = Field(default=None, sa_column=Column(JSON))
    owner_id: int = Field(foreign_key='user.id')
    project_id: int | None = Field(default=None, foreign_key='project.id')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: Optional[User] = Relationship(back_populates='tasks')
    project: Optional[Project] = Relationship(back_populates='tasks')
    activity_logs: list['ActivityLog'] = Relationship(back_populates='task')


class ActivityLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key='task.id')
    actor_id: int | None = Field(default=None, foreign_key='user.id')
    action: str
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    task: Task = Relationship(back_populates='activity_logs')


class File(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key='project.id')
    owner_id: int = Field(foreign_key='user.id')
    path: str
    mime_type: str
    size: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentManifest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    version: str
    manifest: dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
