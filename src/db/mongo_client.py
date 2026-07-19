from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import MONGODB_URL, MONGODB_DB_NAME

client = AsyncIOMotorClient(MONGODB_URL)
db = client[MONGODB_DB_NAME]
chat_collection = db["chat_history"]
