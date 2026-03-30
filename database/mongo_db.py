from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client = AsyncIOMotorClient(settings.DATABASE_MONGO_URL)
mongo_db = client[settings.MONGO_NAME]

def get_mongo_collection(collection_name: str):
    return mongo_db[collection_name]

comments_col = get_mongo_collection("comments")


