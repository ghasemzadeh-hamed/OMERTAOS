from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import settings
from .registry import Base, Model, Route
from .schemas import ModelOut, ModelRegister, RouteRule

engine = create_engine(
    settings.DB_URL,
    connect_args={"check_same_thread": False} if settings.DB_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="AION Model Registry", version="1.0.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.post("/models", response_model=ModelOut)
def register_model(payload: ModelRegister, db: Session = Depends(get_db)) -> ModelOut:
    if db.query(Model).filter(Model.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Model already exists")
    obj = Model(
        name=payload.name,
        parent=payload.parent,
        path=payload.path,
        score=payload.score,
        metadata_json=payload.metadata,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/models", response_model=List[ModelOut])
def list_models(db: Session = Depends(get_db)) -> List[ModelOut]:
    return db.query(Model).order_by(Model.score.desc()).all()


@app.post("/routes")
def set_route(rule: RouteRule, db: Session = Depends(get_db)) -> dict:
    model = db.query(Model).filter(Model.name == rule.model_name, Model.active.is_(True)).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found or inactive")
    route = db.query(Route).filter(Route.agent_id == rule.agent_id).first()
    if route:
        route.model_name = rule.model_name
    else:
        route = Route(agent_id=rule.agent_id, model_name=rule.model_name)
        db.add(route)
    db.commit()
    return {"status": "ok"}


@app.get("/routes/{agent_id}")
def get_route(agent_id: str, db: Session = Depends(get_db)) -> dict:
    route = db.query(Route).filter(Route.agent_id == agent_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="No route for this agent")
    return {"agent_id": agent_id, "model_name": route.model_name}
