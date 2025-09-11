#!/usr/bin/env python3
"""
Setup Default Users Script
This script creates default users for the Sign Glove application.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

async def setup_default_users():
    """Create default users in the database."""
    try:
        from core.database import users_collection
        from core.settings import settings
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        print("🔧 Setting up default users...")
        print("=" * 40)
        
        # Default users to create
        default_users = [
            {
                "email": "admin@signglove.com",
                "password": "admin123",
                "role": "admin",
                "description": "Default admin user"
            },
            {
                "email": "editor@signglove.com", 
                "password": "editor123",
                "role": "editor",
                "description": "Default editor user"
            },
            {
                "email": "user@signglove.com",
                "password": "user123", 
                "role": "user",
                "description": "Default user"
            }
        ]
        
        created_count = 0
        
        for user_data in default_users:
            email = user_data["email"]
            password = user_data["password"]
            role = user_data["role"]
            description = user_data["description"]
            
            # Check if user already exists
            existing_user = await users_collection.find_one({"email": email})
            
            if existing_user:
                print(f"⚠️  User {email} already exists (role: {existing_user.get('role', 'unknown')})")
                continue
            
            # Create new user
            hashed_password = pwd_context.hash(password)
            user_doc = {
                "email": email,
                "password_hash": hashed_password,
                "role": role,
                "created_at": asyncio.get_event_loop().time()
            }
            
            result = await users_collection.insert_one(user_doc)
            
            if result.inserted_id:
                print(f"✅ Created {role} user: {email} (password: {password})")
                created_count += 1
            else:
                print(f"❌ Failed to create user: {email}")
        
        print(f"\n📊 Summary:")
        print(f"   Created {created_count} new users")
        print(f"   Total users in database: {await users_collection.count_documents({})}")
        
        print(f"\n🔑 Default Login Credentials:")
        print(f"   Admin: admin@signglove.com / admin123")
        print(f"   Editor: editor@signglove.com / editor123") 
        print(f"   User: user@signglove.com / user123")
        
        print(f"\n⚠️  Security Note: Change these passwords in production!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up users: {e}")
        return False

async def test_login():
    """Test login with default users."""
    try:
        from core.database import users_collection
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        print(f"\n🧪 Testing login functionality...")
        
        test_email = "admin@signglove.com"
        test_password = "admin123"
        
        # Find user
        user = await users_collection.find_one({"email": test_email})
        
        if not user:
            print(f"❌ Test user not found: {test_email}")
            return False
        
        # Verify password
        if pwd_context.verify(test_password, user.get("password_hash", "")):
            print(f"✅ Login test successful for {test_email}")
            print(f"   Role: {user.get('role', 'unknown')}")
            return True
        else:
            print(f"❌ Password verification failed for {test_email}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return False

async def main():
    """Main function."""
    print("🎯 Sign Glove - Default Users Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("backend").exists():
        print("❌ Please run this script from the project root directory")
        return False
    
    # Setup users
    if not await setup_default_users():
        return False
    
    # Test login
    if not await test_login():
        return False
    
    print(f"\n🎉 Setup completed successfully!")
    print(f"\n📋 Next steps:")
    print(f"1. Go to http://localhost:5173")
    print(f"2. Login with any of the default credentials above")
    print(f"3. Start using your Sign Glove application!")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
