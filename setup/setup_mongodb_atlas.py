#!/usr/bin/env python3
"""
MongoDB Atlas Setup Helper Script
This script helps you configure your MongoDB Atlas connection.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with MongoDB Atlas configuration."""
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Keeping existing .env file")
            return True
    
    print("\n🔧 Setting up MongoDB Atlas connection...")
    print("=" * 50)
    
    # Get MongoDB Atlas connection details
    print("\n📋 Please provide your MongoDB Atlas connection details:")
    
    # Username
    while True:
        username = input("MongoDB Username: ").strip()
        if username:
            break
        print("❌ Username cannot be empty")
    
    # Password
    while True:
        password = input("MongoDB Password: ").strip()
        if password:
            break
        print("❌ Password cannot be empty")
    
    # Cluster name
    while True:
        cluster = input("Cluster name (e.g., cluster0.abc123): ").strip()
        if cluster:
            break
        print("❌ Cluster name cannot be empty")
    
    # Database name
    db_name = input("Database name (default: signglove): ").strip()
    if not db_name:
        db_name = "signglove"
    
    # Build connection string
    connection_string = f"mongodb+srv://{username}:{password}@{cluster}.mongodb.net/{db_name}?retryWrites=true&w=majority"
    
    # Create .env content
    env_content = f"""# Environment Configuration
ENVIRONMENT=development
DEBUG=true

# Security Settings
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Configuration - MongoDB Atlas
MONGO_URI={connection_string}
DB_NAME={db_name}

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://frontend:80

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
ALLOWED_FILE_TYPES=.csv,.json,.txt
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ .env file created successfully!")
        print(f"📁 Location: {env_file.absolute()}")
        print(f"🔗 Connection string: {connection_string[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_connection():
    """Test the MongoDB Atlas connection."""
    print("\n🧪 Testing MongoDB Atlas connection...")
    
    try:
        # Change to backend directory
        os.chdir("backend")
        
        # Run the test script
        import subprocess
        result = subprocess.run([sys.executable, "test_basic_functionality.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ MongoDB Atlas connection successful!")
            return True
        else:
            print("❌ MongoDB Atlas connection failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def main():
    """Main setup function."""
    print("🎯 MongoDB Atlas Setup Helper")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("backend").exists():
        print("❌ Please run this script from the project root directory")
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Test connection
    if test_connection():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Your application is now configured for MongoDB Atlas")
        print("2. You can start the application with: python start_app.py")
        print("3. Make sure your IP address is whitelisted in MongoDB Atlas")
        return True
    else:
        print("\n❌ Setup failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Check your MongoDB Atlas credentials")
        print("2. Verify your IP address is whitelisted")
        print("3. Make sure your cluster is running")
        print("4. Check the MongoDB Atlas setup guide: MONGODB_ATLAS_SETUP.md")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
