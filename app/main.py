
from fastapi import FastAPI
from .api.endpoints import router
from .database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Healthcare Provider Analysis API",
    description="API for analyzing healthcare provider data with natural language queries",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Healthcare Cost Provider API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}