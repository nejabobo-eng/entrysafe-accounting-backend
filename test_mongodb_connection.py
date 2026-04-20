"""
Quick MongoDB Connection Test
Run this after setting MONGO_URI in .env to verify connection works
"""

import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load .env
load_dotenv()

async def test_mongodb():
    """Test MongoDB connection"""
    
    mongo_uri = os.getenv("MONGO_URI")
    
    if not mongo_uri:
        print("[ERROR] MONGO_URI not found in .env")
        return False
    
    print(f"[INFO] Attempting connection to MongoDB...")
    print(f"[INFO] URI (masked): mongodb+srv://***:***@{mongo_uri.split('@')[1] if '@' in mongo_uri else 'local'}")
    
    try:
        # Create client
        client = AsyncIOMotorClient(mongo_uri)
        
        # Connect and verify
        db = client["entrysafe"]
        
        # Ping to verify
        await client.admin.command("ping")
        print("[OK] Successfully connected to MongoDB")
        
        # List collections
        collections = await db.list_collection_names()
        print(f"[OK] Database 'entrysafe' exists")
        print(f"[OK] Current collections: {collections if collections else '(empty - ready for first write)'}")
        
        # Close
        client.close()
        print("[OK] Connection closed successfully")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print(f"[ERROR] Double-check:")
        print(f"  1. Connection string in .env is correct")
        print(f"  2. Cluster is deployed (wait 2-3 min if just created)")
        print(f"  3. Network access includes 0.0.0.0/0")
        print(f"  4. Password is correct")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mongodb())
    exit(0 if success else 1)
