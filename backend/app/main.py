
from fastapi import FastAPI

from app.api.routes import incidents, logs, investigation


app = FastAPI(
    title="FaultLens API",
    description="AI-powered Incident Intelligence Platform",
    version="1.0.0"
)

app.include_router(incidents.router)
app.include_router(logs.router)
app.include_router(investigation.router)

@app.get("/")
def home():
    return {
        "message": "Welcome to FaultLens!",
        "status": "Running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "FaultLens"
    }
