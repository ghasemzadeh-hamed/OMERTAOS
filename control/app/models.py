from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    role: str = Field(default='user', index=True)
    image: Optional[str] = None
    password_hash: Optional[str] = Field(default=None, alias='passwordHash')
    provider: Optional[str] = None
    provider_id: Optional[str] = Field(default=None, alias='providerId')
    created_at: datetime = Field(default_factory=datetime.utcnow, alias='createdAt')
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias='updatedAt')


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    owner_id: int = Field(foreign_key='user.id')
    created_at: datetime = Field(default_factory=datetime.utcnow, alias='createdAt')


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key='project.id')
    title: str
    description: Optional[str] = None
    status: str = Field(default='todo', index=True)
    priority: str = Field(default='medium')
    assignee_id: Optional[int] = Field(default=None, foreign_key='user.id')
    due_date: Optional[datetime] = Field(default=None, alias='dueDate')
    created_at: datetime = Field(default_factory=datetime.utcnow, alias='createdAt')
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias='updatedAt')


class ActivityLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    actor_id: int = Field(foreign_key='user.id')
    entity_type: str
    entity_id: int
    action: str
    meta: dict | None = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, alias='createdAt')


class File(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(default=None, foreign_key='project.id')
    task_id: Optional[int] = Field(default=None, foreign_key='task.id')
    key: str
    url: str
    size: int
    mime: str
    created_at: datetime = Field(default_factory=datetime.utcnow, alias='createdAt')
