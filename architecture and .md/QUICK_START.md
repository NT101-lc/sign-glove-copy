# 🚀 Sign Glove Quick Start Guide

## Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB (local or Docker)
- Arduino IDE (for ESP32 programming)

## 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### Environment Configuration
```bash
cp ../env.example .env
# Edit .env with your settings
```

### Start Backend
```bash
python main.py
# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 3. Database Setup

### Option A: Local MongoDB
```bash
# Install MongoDB locally
# Start MongoDB service
```

### Option B: MongoDB Atlas (Recommended)
1. **Create Atlas Cluster**:
   - Go to [MongoDB Atlas](https://cloud.mongodb.com)
   - Create a free cluster
   - Set up database access (username/password)
   - Configure network access (IP whitelist)

2. **Get Connection String**:
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string

3. **Update Environment**:
   ```bash
   # In your .env file, update MONGO_URI:
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/signglove?retryWrites=true&w=majority
   ```

### Option C: Docker MongoDB
```bash
docker run -d --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=signglove123 \
  mongo:7.0
```

## 4. Arduino Setup (When You Have the Glove)

### Install Required Libraries
1. Open Arduino IDE
2. Go to Tools > Manage Libraries
3. Install:
   - `MPU6050` by Electronic Cats
   - `Wire` (included with ESP32 core)

### Configure ESP32
1. Select ESP32 board in Arduino IDE
2. Set correct port
3. Upload `arduino/sketch.ino`

### Update Configuration
Edit `backend/ingestion/collect_data.py`:
```python
SERIAL_PORT = 'COM5'  # Change to your port
LABEL = 'A'           # Set gesture label
SESSION_ID = 'test1'  # Set session ID
```

## 5. Data Collection

```bash
cd backend
python ingestion/collect_data.py
```

## 6. Model Training

1. Upload data via frontend `/upload` page
2. Go to Training Results page
3. Click "Manual Training"
4. View results and visualizations

## 7. Testing Without Hardware

### Manual Prediction
- Use `/predict` page with sample data
- Example: `0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1`

### Live Prediction
- Use `/predict/live` page
- Connect WebSocket for real-time testing

## 8. Docker Deployment (Optional)

```bash
docker compose up -d --build
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Check if MongoDB is running (local) or Atlas cluster is accessible
   - Verify connection string in `.env`
   - For Atlas: Check IP whitelist and credentials

2. **Serial Port Not Found**
   - Check device manager for correct port
   - Update `SERIAL_PORT` in `collect_data.py`

3. **Model Training Fails**
   - Ensure you have training data
   - Check data format in CSV files

4. **Frontend Can't Connect**
   - Verify backend is running on port 8080
   - Check CORS settings in `.env`

### Logs
- Backend logs: Check console output
- Data collection logs: `backend/data_collection.log`

## API Documentation
- Interactive docs: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## Next Steps

1. **With Hardware**: Test with actual glove sensors
2. **Without Hardware**: Use sample data for development
3. **Improve Model**: Collect more training data
4. **Add Features**: Implement additional gestures 