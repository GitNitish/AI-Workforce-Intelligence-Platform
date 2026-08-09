from fastapi import FastAPI

app = FastAPI(
    title="WorkForceIQ API",
    description="Backend API for the AI Workforce Intelligence Platform",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "application": "WorkForceIQ API",
        "status": "running",
        "version": "0.1.0",
    }