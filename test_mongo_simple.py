import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load from file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path, override=True)

async def test_connection():
    mongo_uri = os.getenv("MONGO_URI")
    
    if not mongo_uri:
        print("[ERROR] MONGO_URI not found in .env")
        return False
    
    print("[INFO] Testing MongoDB connection...")
    print(f"[INFO] Connecting to cluster...")
    
    try:
        client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        
        print("[OK] Successfully connected to MongoDB Atlas!")
        
        db = client["entrysafe"]
        collections = await db.list_collection_names()
        print(f"[OK] Database 'entrysafe' is ready")
        print(f"[OK] Current collections: {collections if collections else '(empty - ready for first write)'}")
        
        client.close()
        print("[OK] Connection test successful")
        return True
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    exit(0 if result else 1)
