from fastapi import FastAPI

try:
    from app.routes import (
        admin_onboarding_router,
        ai_chat_router,
        agent_router,
        kernel_router,
        memory_router,
        models_router,
        rag_router,
    )
except Exception:  # pragma: no cover - fallback for local execution
    from routes import (  # type: ignore
        admin_onboarding_router,
        ai_chat_router,
        agent_router,
        kernel_router,
        memory_router,
        models_router,
        rag_router,
    )

app = FastAPI()


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(admin_onboarding_router)
app.include_router(ai_chat_router)
app.include_router(agent_router)
app.include_router(kernel_router)
app.include_router(memory_router)
app.include_router(models_router)
app.include_router(rag_router)
