import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import get_db
from .routers import stats, subjects, topics

APP_VERSION = os.getenv("APP_VERSION", "dev")

app = FastAPI(
    title="Syllabus Tracker API",
    description="Track syllabus completion across subjects and topics.",
    version=APP_VERSION,
)

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(subjects.router)
app.include_router(topics.router)
app.include_router(stats.router)

Instrumentator(
    excluded_handlers=["/metrics", "/health", "/ready"],
).instrument(app).expose(app, include_in_schema=False)


@app.get("/", tags=["meta"])
def root():
    return {"service": "syllabus-tracker-api", "version": APP_VERSION, "docs": "/docs"}


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


@app.get("/ready", tags=["meta"])
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not ready", "database": "unreachable"})
    return {"status": "ready", "database": "ok"}
