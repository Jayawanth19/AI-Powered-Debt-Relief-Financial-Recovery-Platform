import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import engine, Base
import models  # noqa: F401 - ensures models are registered with Base metadata
from routers import borrowers, loans, negotiation, dashboard

load_dotenv()

app = FastAPI(
    title="AI-Powered Debt Relief & Financial Recovery Platform",
    description=(
        "Backend API for managing loans, generating AI-powered settlement "
        "recommendations, and drafting negotiation letters using Google Gemini."
    ),
    version="1.0.0",
)

# Create tables on startup (SQLite - fine for dev; use Alembic migrations in prod)
Base.metadata.create_all(bind=engine)

origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(borrowers.router)
app.include_router(loans.router)
app.include_router(negotiation.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "service": "AI-Powered Debt Relief & Financial Recovery Platform API",
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
