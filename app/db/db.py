import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    """Mirror connectDB() from db/db.ts — connect, log, exit on failure."""
    global _client, _db
    try:
        print("🔗 Connecting to MongoDB...")
        mongo_uri = os.environ.get("MONGO_URI")
        if not mongo_uri:
            raise RuntimeError("MONGO_URI is not set")
        _client = AsyncIOMotorClient(mongo_uri)
        # Mongoose picks the DB name from the URI; replicate via get_default_database.
        _db = _client.get_default_database()
        # Force a connection check (Motor is lazy).
        await _client.admin.command("ping")
        print("✅ MongoDB connected successfully")
    except Exception as error:
        print(f"❌ MongoDB connection failed: {error}")
        sys.exit(1)


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("DB not initialized. Call connect_db() first.")
    return _db


async def close_db() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
