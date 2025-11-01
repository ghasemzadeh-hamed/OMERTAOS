"""Minimal HTTP server that exposes the command processor via forms for text browsers."""

from __future__ import annotations

import argparse
from collections import deque
from typing import Deque, List

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from .api import CommandProcessor, ControlAPI

HISTORY_LIMIT = 50

INDEX_TEMPLATE = """<!doctype html>
<html lang=fa>
<head>
  <meta charset="utf-8" />
  <title>aionOS Terminal Explorer</title>
  <style>
    body { font-family: monospace; background: #101010; color: #f5f5f5; }
    a { color: #4fd1c5; }
    .container { max-width: 900px; margin: 0 auto; padding: 1rem; }
    textarea, input { width: 100%; background: #1f1f1f; color: #f5f5f5; border: 1px solid #4fd1c5; }
    textarea { height: 6rem; }
    .history { white-space: pre-wrap; border: 1px solid #333; padding: 1rem; background: #0e0e0e; min-height: 14rem; }
    .tips { margin-top: 1rem; font-size: 0.9rem; }
  </style>
</head>
<body>
  <div class="container">
    <h1>aionOS Explorer (متنی)</h1>
    <p>فرمان خود را وارد کنید. نمونه: <code>add provider openai key=sk-...</code></p>
    <form method="post" action="/chat">
      <label for="command">فرمان:</label>
      <input type="text" name="command" id="command" autofocus />
      <button type="submit">ارسال</button>
    </form>
    <div class="history" role="log">{history}</div>
    <div class="tips">
      <p><strong>راهنما:</strong> <code>help</code> را ارسال کنید.</p>
      <p>بازنشانی لاگ: <a href="/reset">/reset</a></p>
    </div>
  </div>
</body>
</html>
"""


def build_app(api: ControlAPI) -> FastAPI:
    processor = CommandProcessor(api)
    history: Deque[str] = deque(maxlen=HISTORY_LIMIT)

    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"]
    )

    def render_history() -> str:
        if not history:
            return "هنوز پیامی ثبت نشده است."
        return "\n".join(history)

    @app.get("/", response_class=HTMLResponse)
    async def index() -> HTMLResponse:
        return HTMLResponse(INDEX_TEMPLATE.format(history=render_history()))

    @app.post("/chat")
    async def chat(command: str = Form(...)) -> RedirectResponse:
        result = processor.execute(command)
        history.append(f"> {command}\n{result}")
        return RedirectResponse("/", status_code=303)

    @app.get("/reset")
    async def reset() -> RedirectResponse:
        history.clear()
        return RedirectResponse("/", status_code=303)

    return app


def run_server(args: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="وب‌سرور متنی برای اکسپلورر aionOS")
    parser.add_argument("--api", default="http://127.0.0.1:8001", help="آدرس API کنترل")
    parser.add_argument("--token", default=None, help="توکن دسترسی")
    parser.add_argument("--host", default="127.0.0.1", help="آدرس گوش دادن")
    parser.add_argument("--port", type=int, default=3030, help="پورت سرویس")
    parser.add_argument("--no-verify", action="store_true", help="غیرفعال کردن بررسی TLS")
    parser.add_argument("--reload", action="store_true", help="اجرا با hot-reload (برای توسعه)")
    parsed = parser.parse_args(args=args)
    api = ControlAPI(parsed.api, token=parsed.token, verify=not parsed.no_verify)
    app = build_app(api)
    import uvicorn

    uvicorn.run(app, host=parsed.host, port=parsed.port, reload=parsed.reload)


if __name__ == "__main__":  # pragma: no cover
    run_server()
