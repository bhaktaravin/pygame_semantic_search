import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Load .env file from project root
load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    raise RuntimeError("MONGODB_URI not set in environment")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")  # Force connection
except ServerSelectionTimeoutError as e:
    raise ConnectionError("Failed to connect to MongoDB Atlas") from e

db = client.semantic_npc
dialogue_collection = db.dialogues
