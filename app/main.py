from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="WorkForceIQ API",
    description="Backend API for the AI Workforce Intelligence Platform",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "application": "WorkForceIQ API",
        "status": "running",
        "version": "0.1.0",
    }