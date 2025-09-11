#!/usr/bin/env python3
"""
Sign Glove Application Startup Script
This script helps you start the application with proper checks and setup.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_docker():
    """Check if Docker is available."""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is available")
            return True
        else:
            print("❌ Docker is not available")
            return False
    except FileNotFoundError:
        print("❌ Docker is not installed or not in PATH")
        return False

def check_docker_compose():
    """Check if Docker Compose is available."""
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose is available")
            return True
        else:
            print("❌ Docker Compose is not available")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose is not installed or not in PATH")
        return False

def check_env_file():
    """Check if .env file exists and create one if needed."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file exists")
        return True
    elif env_example.exists():
        print("⚠️  .env file not found, creating from env.example...")
        try:
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ .env file created from env.example")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("❌ Neither .env nor env.example found")
        return False

def start_with_docker():
    """Start the application using Docker Compose."""
    print("\n🚀 Starting Sign Glove with Docker Compose...")
    
    try:
        # Build and start services
        subprocess.run(['docker-compose', 'down'], check=False)
        subprocess.run(['docker-compose', 'build'], check=True)
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        
        print("✅ Services started successfully!")
        print("\n📋 Service URLs:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8080")
        print("   MongoDB: localhost:27017")
        
        print("\n📊 To view logs:")
        print("   docker-compose logs -f")
        
        print("\n🛑 To stop services:")
        print("   docker-compose down")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start services: {e}")
        return False

def start_backend_only():
    """Start only the backend service."""
    print("\n🚀 Starting backend only...")
    
    try:
        # Change to backend directory
        os.chdir("backend")
        
        # Install dependencies if needed
        if not Path("venv").exists():
            print("📦 Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        # Activate virtual environment and install dependencies
        if os.name == 'nt':  # Windows
            activate_script = "venv\\Scripts\\activate"
            pip_cmd = "venv\\Scripts\\pip"
        else:  # Unix/Linux
            activate_script = "venv/bin/activate"
            pip_cmd = "venv/bin/pip"
        
        print("📦 Installing dependencies...")
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        
        # Run the test script
        print("🧪 Running basic functionality test...")
        result = subprocess.run([sys.executable, "test_basic_functionality.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backend test passed!")
            print("\n🚀 Starting backend server...")
            subprocess.run([pip_cmd, "install", "uvicorn"], check=True)
            subprocess.run([pip_cmd, "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"], check=True)
        else:
            print("❌ Backend test failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start backend: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main startup function."""
    print("🎯 Sign Glove Application Startup")
    print("=" * 40)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_env_file():
        return False
    
    # Ask user for startup method
    print("\n📋 Choose startup method:")
    print("1. Full application (Docker Compose) - Recommended")
    print("2. Backend only (Local Python)")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            if check_docker() and check_docker_compose():
                return start_with_docker()
            else:
                print("❌ Docker is required for full application startup")
                return False
        elif choice == "2":
            return start_backend_only()
        elif choice == "3":
            print("👋 Goodbye!")
            return True
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
