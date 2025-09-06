import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Your MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://namanh14122005:test123@signglove-cluster.2fgsv8h.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "sign_glove"

async def test_atlas_connection():
    print(f"Testing MongoDB Atlas connection...")
    print(f"MONGO_URI: {MONGO_URI}")
    print(f"DB_NAME: {DB_NAME}")
    
    try:
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        await client.admin.command("ping")
        print("✅ MongoDB Atlas connection successful!")
        
        # Test database access
        db = client[DB_NAME]
        collections = await db.list_collection_names()
        print(f"✅ Database '{DB_NAME}' accessible. Collections: {collections}")
        
        # Test creating a test document
        test_collection = db.test_connection
        result = await test_collection.insert_one({"test": "connection", "timestamp": "2024"})
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Clean up test document
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Test document cleaned up")
        
    except Exception as e:
        print("❌ MongoDB Atlas connection failed!")
        print(f"Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check if your IP address is whitelisted in MongoDB Atlas Network Access")
        print("2. Verify your username and password are correct")
        print("3. Make sure the cluster is running and not paused")
        print("4. Check your internet connection")

if __name__ == "__main__":
    asyncio.run(test_atlas_connection())
