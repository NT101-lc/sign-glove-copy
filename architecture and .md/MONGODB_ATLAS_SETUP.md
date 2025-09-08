# MongoDB Atlas Setup Guide

This guide will help you set up MongoDB Atlas for your Sign Glove project.

## Step 1: Create MongoDB Atlas Account

1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Click "Try Free" or "Sign Up"
3. Create an account or sign in

## Step 2: Create a Cluster

1. Click "Build a Database"
2. Choose "FREE" tier (M0)
3. Select your preferred cloud provider (AWS, Google Cloud, or Azure)
4. Choose a region close to you
5. Click "Create"

## Step 3: Set Up Database Access

1. In the left sidebar, click "Database Access"
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Create a username and password (save these!)
5. Set privileges to "Read and write to any database"
6. Click "Add User"

## Step 4: Set Up Network Access

1. In the left sidebar, click "Network Access"
2. Click "Add IP Address"
3. For development, click "Allow Access from Anywhere" (0.0.0.0/0)
4. Click "Confirm"

## Step 5: Get Your Connection String

1. Go back to "Database" in the sidebar
2. Click "Connect"
3. Choose "Connect your application"
4. Copy the connection string

## Step 6: Configure Your Application

1. Create a `.env` file in your project root (if it doesn't exist)
2. Add your MongoDB Atlas connection string:

```env
MONGO_URI=mongodb+srv://yourusername:yourpassword@cluster0.abc123.mongodb.net/signglove?retryWrites=true&w=majority
DB_NAME=signglove
```

**Important Notes:**
- Replace `yourusername` with your actual username
- Replace `yourpassword` with your actual password
- Replace `cluster0.abc123` with your actual cluster name
- The `signglove` in the URI is the database name

## Step 7: Test Your Connection

Run the test script to verify your connection:

```bash
cd backend
python test_basic_functionality.py
```

## Common Issues and Solutions

### Issue: Authentication Failed
**Solution:**
- Double-check your username and password
- Make sure you're using the correct connection string format
- Verify your IP address is whitelisted in Network Access

### Issue: Connection Timeout
**Solution:**
- Check your internet connection
- Verify the cluster is running (green status in Atlas)
- Try connecting from a different network

### Issue: SSL/TLS Error
**Solution:**
- Make sure you're using `mongodb+srv://` (not `mongodb://`)
- The connection string should include `?retryWrites=true&w=majority`

## Security Best Practices

1. **Never commit your `.env` file** - it's already in `.gitignore`
2. **Use strong passwords** for your database user
3. **Limit IP access** in production (don't use 0.0.0.0/0)
4. **Use environment variables** in production deployments

## Troubleshooting

If you're still having issues:

1. Check the MongoDB Atlas status page
2. Verify your cluster is active (not paused)
3. Test the connection string in MongoDB Compass
4. Check the application logs for specific error messages

## Example .env File

```env
# Environment Configuration
ENVIRONMENT=development
DEBUG=true

# Security Settings
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Configuration - MongoDB Atlas
MONGO_URI=mongodb+srv://yourusername:yourpassword@cluster0.abc123.mongodb.net/signglove?retryWrites=true&w=majority
DB_NAME=signglove

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://frontend:80

# ESP32 Configuration
ESP32_IP=192.168.1.100

# Auth / JWT
SECRET_KEY=change-me-in-prod
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
COOKIE_SECURE=false

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
```
