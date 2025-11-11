from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(128), index=True, nullable=False)
    user_id = Column(String(256), index=True, nullable=True)
    model_version = Column(String(256), index=True, nullable=False)
    input_text = Column(Text, nullable=False)
    output_text = Column(Text, nullable=False)
    channel = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    self_edits = relationship(
        "SelfEdit", back_populates="interaction", cascade="all, delete-orphan"
    )


class SelfEdit(Base):
    __tablename__ = "self_edits"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=False)
    original_output = Column(Text, nullable=False)
    edited_output = Column(Text, nullable=False)
    reason = Column(String(256), nullable=True)
    reward = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    interaction = relationship("Interaction", back_populates="self_edits")
