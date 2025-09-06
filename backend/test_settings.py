#!/usr/bin/env python3
"""
Test script to verify that settings are loading environment variables correctly.
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.settings import settings

print("=== Settings Configuration Test ===")
print(f"MONGO_URI: {settings.MONGO_URI}")
print(f"DB_NAME: {settings.DB_NAME}")
print(f"ENVIRONMENT: {settings.ENVIRONMENT}")
print(f"DEBUG: {settings.DEBUG}")

# Check if .env file exists
env_file_path = os.path.join(os.path.dirname(__file__), ".env")
print(f"\n=== Environment File Check ===")
print(f".env file path: {env_file_path}")
print(f".env file exists: {os.path.exists(env_file_path)}")

if os.path.exists(env_file_path):
    print("\n=== .env file contents ===")
    with open(env_file_path, 'r') as f:
        content = f.read()
        # Only show first few lines for security
        lines = content.split('\n')[:10]
        for i, line in enumerate(lines, 1):
            if 'MONGO_URI' in line or 'DB_NAME' in line:
                print(f"{i}: {line}")
            elif line.strip() and not line.startswith('#'):
                print(f"{i}: {line[:50]}...")
else:
    print("❌ .env file not found!")
    print("Please create a .env file in the backend directory with your MongoDB Atlas connection string.")
