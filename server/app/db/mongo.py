from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongo_db = MongoDB()

async def connect_to_mongo():
    # In production, pull this from settings
    mongo_url = getattr(settings, "mongo_url", "mongodb://admin:adminpassword@localhost:27017")
    mongo_db.client = AsyncIOMotorClient(mongo_url)
    mongo_db.db = mongo_db.client.edupress_read

async def close_mongo_connection():
    if mongo_db.client:
        mongo_db.client.close()

def get_database():
    return mongo_db.db
