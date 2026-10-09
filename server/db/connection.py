import logging
from typing import Optional
from pymongo import AsyncMongoClient
from beanie import init_beanie
from config.settings import MONGODB_URL, MONGODB_DB_NAME
from db.models import ALL_DOCUMENT_MODELS

logger = logging.getLogger(__name__)

mongo_client: Optional[AsyncMongoClient] = None


async def init_db() -> None:
    """Initializes the MongoDB connection and Beanie ODM document models."""
    global mongo_client
    try:
        mongo_client = AsyncMongoClient(MONGODB_URL)
        # Verify connection
        await mongo_client.admin.command("ping")
        database = mongo_client[MONGODB_DB_NAME]
        await init_beanie(database=database, document_models=ALL_DOCUMENT_MODELS)
        logger.info(f"Connected to MongoDB at {MONGODB_URL}, initialized database '{MONGODB_DB_NAME}'.")
        print(f"Connected to MongoDB ({MONGODB_DB_NAME}) successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        print(f"Failed to connect to MongoDB: {e}")
        raise e


async def close_db() -> None:
    """Closes the MongoDB client connection cleanly."""
    global mongo_client
    if mongo_client is not None:
        await mongo_client.close()
        mongo_client = None
        logger.info("MongoDB connection closed.")
