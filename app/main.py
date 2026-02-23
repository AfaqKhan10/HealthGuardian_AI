# app/main.py
from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.routers import cases

app = FastAPI(
    title="HealthGuardian AI",
    description="AI-powered medical triage system with supervisor agents",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Development only – production mein Alembic use karo
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": "HealthGuardian AI backend is running",
        "status": "healthy",
        "version": app.version
    }


app.include_router(cases.router, prefix="/api")  # optional: /api prefix add kar diya