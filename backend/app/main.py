from fastapi import FastAPI
from app.api.routes import incidents

app = FastAPI(
    title="Faultlens API",
    description="AI powered Incident Intelligence Platform",
    version="1.0.0"
)

app.include_router(incidents.router)

@app.get("/")
def home():
    return{
        "message": "Welcome to FaultLens",
        "description": "AI powered Incident Intelligence Platform",
        "status": "Running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "FaultLens"
    }