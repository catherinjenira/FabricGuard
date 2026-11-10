"""
FabricGuard-AI FastAPI Application Entry Point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import inspection, batch, history, review, evaluation

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure directories and database tables exist
    settings.init_storage()
    await init_db()
    print(f"[*] {settings.PROJECT_NAME} initialized successfully.")
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Automated Fabric Defect Detection & HITL Quality Inspection API",
    version="1.4.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permissive for local development across Vite ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static file storage for uploads and annotated results
storage_dir = Path("./storage")
storage_dir.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(storage_dir)), name="storage")

# Include Routers
app.include_router(inspection.router, prefix=settings.API_V1_STR)
app.include_router(batch.router, prefix=settings.API_V1_STR)
app.include_router(history.router, prefix=settings.API_V1_STR)
app.include_router(review.router, prefix=settings.API_V1_STR)
app.include_router(evaluation.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "system": settings.PROJECT_NAME,
        "status": "ONLINE",
        "version": "1.4.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "timestamp": "OK"
    }

