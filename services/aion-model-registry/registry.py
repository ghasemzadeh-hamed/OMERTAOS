from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), unique=True, index=True, nullable=False)
    parent = Column(String(256), nullable=True)
    path = Column(String(512), nullable=False)
    score = Column(Float, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(128), index=True, nullable=False)
    model_name = Column(String(256), nullable=False)
