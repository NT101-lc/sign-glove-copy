#!/usr/bin/env python3
"""
Fix Environment and Setup Users Script
This script fixes the .env file and creates default users.
"""

import os
import sys
from pathlib import Path

def fix_env_file():
    """Create a proper .env file."""
    env_content = """# Environment Configuration
ENVIRONMENT=development
DEBUG=true

# Security Settings
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Configuration - MongoDB Atlas
MONGO_URI=mongodb+srv://anhdh23bi14015:test123@SignGlove-Cluster.mongodb.net/sign_glove?retryWrites=true&w=majority
DB_NAME=sign_glove

# CORS Settings
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://frontend:80"]

# ESP32 Configuration
ESP32_IP=192.168.1.100

# Auth / JWT
SECRET_KEY=change-me-in-prod
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
COOKIE_SECURE=false

# Optional: auto-seed an editor user
# DEFAULT_EDITOR_EMAIL=editor@example.com
# DEFAULT_EDITOR_PASSWORD=changeme

# TTS Configuration
TTS_ENABLED=true
TTS_PROVIDER=gtts
TTS_VOICE=ur-IN-SalmanNeural
TTS_RATE=150
TTS_VOLUME=2.0
TTS_CACHE_ENABLED=true
TTS_CACHE_DIR=tts_cache

# Performance and Monitoring
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
MAX_REQUEST_SIZE=10485760
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# File Upload Settings
UPLOAD_DIR=uploads
MAX_FILE_SIZE=52428800
ALLOWED_FILE_TYPES=[".csv",".json",".txt"]
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Fixed .env file")
        return True
    except Exception as e:
        print(f"❌ Error fixing .env file: {e}")
        return False

def setup_users():
    """Setup default users using a simple approach."""
    try:
        # Add backend to path
        backend_dir = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_dir))
        
        import asyncio
        from core.database import users_collection
        from passlib.context import CryptContext
        from datetime import datetime, timezone
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        async def create_users():
            default_users = [
                {"email": "admin@signglove.com", "password": "admin123", "role": "admin"},
                {"email": "editor@signglove.com", "password": "editor123", "role": "editor"},
                {"email": "user@signglove.com", "password": "user123", "role": "guest"}
            ]
            
            created_count = 0
            
            for user_data in default_users:
                email = user_data["email"]
                password = user_data["password"]
                role = user_data["role"]
                
                # Check if user exists
                existing = await users_collection.find_one({"email": email})
                if existing:
                    print(f"⚠️  User {email} already exists")
                    continue
                
                # Create user
                hashed = pwd_context.hash(password)
                doc = {
                    "email": email,
                    "password_hash": hashed,
                    "role": role,
                    "created_at": datetime.now(timezone.utc)
                }
                
                result = await users_collection.insert_one(doc)
                if result.inserted_id:
                    print(f"✅ Created {role} user: {email} (password: {password})")
                    created_count += 1
            
            print(f"\n📊 Created {created_count} new users")
            print(f"🔑 Login credentials:")
            print(f"   Admin: admin@signglove.com / admin123")
            print(f"   Editor: editor@signglove.com / editor123")
            print(f"   User: user@signglove.com / user123")
            
            return True
        
        # Run the async function
        return asyncio.run(create_users())
        
    except Exception as e:
        print(f"❌ Error setting up users: {e}")
        return False

def main():
    """Main function."""
    print("🔧 Fixing Environment and Setting Up Users")
    print("=" * 50)
    
    # Fix .env file
    if not fix_env_file():
        return False
    
    # Setup users
    if not setup_users():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Go to http://localhost:5173")
    print("2. Login with any of the credentials above")
    print("3. Start using your Sign Glove application!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
