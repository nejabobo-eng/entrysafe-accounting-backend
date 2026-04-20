"""
MongoDB connection and initialization
Motor async driver for FastAPI
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Global client reference
client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    """Initialize MongoDB connection on app startup"""
    global client, db

    mongo_uri = settings.MONGO_URI

    try:
        client = AsyncIOMotorClient(
            mongo_uri, 
            serverSelectionTimeoutMS=3000,  # 3 second timeout
            connectTimeoutMS=3000,
            socketTimeoutMS=3000
        )
        db = client["entrysafe"]

        # Verify connection with short timeout
        await client.admin.command("ping")
        logger.info("[OK] MongoDB connected successfully")
    except Exception as e:
        logger.warning(f"[WARNING] MongoDB connection timeout/failed: {e}")
        logger.info("[INFO] Backend will run without MongoDB persistence")
        db = None
        client = None


async def close_mongo_connection() -> None:
    """Close MongoDB connection on app shutdown"""
    global client

    if client:
        client.close()
        logger.info("[OK] MongoDB connection closed")


def get_database() -> Optional[AsyncIOMotorDatabase]:
    """Get the database instance"""
    global db
    return db
