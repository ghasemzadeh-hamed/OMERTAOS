from fastapi import APIRouter

router = APIRouter(prefix="/v1/setup", tags=["setup"])


@router.post("/bootstrap")
async def bootstrap(payload: dict | None = None):
    return {
        "ok": True,
        "status": "initialized",
        "profile": (payload or {}).get("profile", "lite"),
        "message": "OMERTAOS bootstrap completed",
    }
