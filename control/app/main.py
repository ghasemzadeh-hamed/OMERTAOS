from fastapi import FastAPI
# ⬇️ افزودن روتر راه‌انداز
try:
    from app.routes import admin_onboarding
except Exception:
    # اگر ساختار import شما متفاوت است، مسیر را اصلاح کنید
    from routes import admin_onboarding  # type: ignore

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"ok": True}

# ثبت روتر
app.include_router(admin_onboarding.router)
