"""
Entry Safe AI Accounting API - Backend v3
Proper async patterns, lazy initialization, stable startup
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description="AI-powered accounting platform for farming businesses",
    version=settings.API_VERSION
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fast health checks (no dependencies)
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {
        "message": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running"
    }

# MongoDB lifecycle
@app.on_event("startup")
async def startup():
    """Initialize MongoDB on startup"""
    logger.info("🚀 Starting backend...")
    try:
        await connect_to_mongo()
        logger.info("✅ Backend ready (MongoDB connected)")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB connection failed: {e}")
        logger.info("✅ Backend ready (in-memory mode)")

@app.on_event("shutdown")
async def shutdown():
    """Close MongoDB on shutdown"""
    logger.info("🛑 Shutting down...")
    await close_mongo_connection()

# Include routes (lazy - only imported when needed)
def include_routers():
    """Load routes after app is ready"""
    try:
        from app.routes import transactions as transactions_routes
        app.include_router(transactions_routes.router)
        logger.info("✅ Transactions router loaded")
    except Exception as e:
        logger.warning(f"⚠️ Transactions router failed: {e}")

    try:
        from app.routes import settings as settings_routes
        app.include_router(settings_routes.router)
        logger.info("✅ Settings router loaded")
    except Exception as e:
        logger.warning(f"⚠️ Settings router failed: {e}")

# Load routes after app initialization
include_routers()

