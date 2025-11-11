from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, init_db

app = FastAPI(title="AION Memory Service", version="1.0.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.post("/interactions", response_model=schemas.InteractionOut)
def create_interaction(payload: schemas.InteractionCreate, db: Session = Depends(get_db)) -> schemas.InteractionOut:
    obj = models.Interaction(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/interactions/{interaction_id}", response_model=schemas.InteractionOut)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)) -> schemas.InteractionOut:
    obj = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return obj


@app.post("/self-edits", response_model=schemas.SelfEditOut)
def create_self_edit(payload: schemas.SelfEditCreate, db: Session = Depends(get_db)) -> schemas.SelfEditOut:
    interaction = db.query(models.Interaction).filter(models.Interaction.id == payload.interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    obj = models.SelfEdit(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/self-edits/top", response_model=List[schemas.SelfEditOut])
def get_top_self_edits(
    min_reward: float = 0.7, limit: int = 256, db: Session = Depends(get_db)
) -> List[schemas.SelfEditOut]:
    query = (
        db.query(models.SelfEdit)
        .filter(models.SelfEdit.reward >= min_reward)
        .order_by(models.SelfEdit.reward.desc(), models.SelfEdit.created_at.desc())
        .limit(limit)
    )
    return query.all()
