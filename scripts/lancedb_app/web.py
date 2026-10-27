"""Loopback-only FastAPI management UI. No arbitrary SQL or local-file serving endpoints."""
from __future__ import annotations

import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .records import DEFAULT_HOME, RecordError
from .store import Store

STATIC = Path(__file__).parent / "static"


class UpdateBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    record: dict
    revision: int = Field(ge=1)


class RevisionBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision: int = Field(ge=1)


def create_app(home: Path = DEFAULT_HOME) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.store = Store(home)
        app.state.write_token = secrets.token_urlsafe(32)
        try:
            yield
        finally:
            app.state.store.close()

    app = FastAPI(title="本地 LanceDB 数据管理", version="0.1.0", lifespan=lifespan,
                  docs_url=None, redoc_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]"])

    @app.exception_handler(RecordError)
    async def record_error(request: Request, exc: RecordError):
        return JSONResponse({"detail": str(exc)}, status_code=exc.status_code)

    @app.middleware("http")
    async def local_request(request: Request, call_next):
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            if request.headers.get("x-write-token") != getattr(app.state, "write_token", None):
                return JSONResponse({"detail": "写入令牌无效，请刷新本地页面。"}, status_code=403)
            if not request.headers.get("content-type", "").startswith("application/json"):
                return JSONResponse({"detail": "仅接受 application/json。"}, status_code=415)
            # Bound actual streamed bytes, not just a caller-controlled Content-Length.
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > 3 * 1024 * 1024:
                    return JSONResponse({"detail": "请求不能超过 3 MiB。"}, status_code=413)
            request._body = bytes(body)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        )
        return response

    app.mount("/static", StaticFiles(directory=STATIC), name="static")

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/api/session")
    def session():
        return {"write_token": app.state.write_token}

    @app.get("/api/stats")
    def stats():
        return app.state.store.stats()

    @app.get("/api/sources")
    def sources():
        return [{"source_id": item["source_id"], "organization": item.get("organization", ""),
                 "license_status": item.get("license_status", "unknown")}
                for item in app.state.store.validator.sources]

    @app.get("/api/records")
    def records(limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0),
                q: str = Query("", max_length=500), record_type: str = Query("", max_length=64),
                license_status: str = Query("", max_length=32), source_id: str = Query("", max_length=160),
                include_deleted: bool = False):
        return app.state.store.list_records(limit=limit, offset=offset, q=q, record_type=record_type,
                                            license_status=license_status, source_id=source_id,
                                            include_deleted=include_deleted)

    @app.post("/api/records", status_code=201)
    def create(record: dict):
        return app.state.store.create(record)

    @app.get("/api/records/{record_id}")
    def detail(record_id: str):
        return app.state.store.get(record_id)

    @app.put("/api/records/{record_id}")
    def update(record_id: str, body: UpdateBody):
        return app.state.store.update(record_id, body.record, body.revision)

    @app.delete("/api/records/{record_id}")
    def withdraw(record_id: str, body: RevisionBody):
        return app.state.store.set_deleted(record_id, body.revision, True)

    @app.post("/api/records/{record_id}/restore")
    def restore(record_id: str, body: RevisionBody):
        return app.state.store.set_deleted(record_id, body.revision, False)

    @app.get("/api/records/{record_id}/history")
    def history(record_id: str):
        return {"items": app.state.store.history(record_id)}

    return app
