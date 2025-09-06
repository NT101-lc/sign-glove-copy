# Sign Glove AI System Architecture

## 🏗️ System Overview

The Sign Glove AI system is a real-time sign language recognition platform that combines hardware sensors, machine learning, and web technologies to provide accessible communication through gesture recognition and text-to-speech.

## 📊 High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Hardware      │    │   Backend       │    │   Frontend      │
│   Layer         │    │   Services      │    │   Interface     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • ESP32 Arduino │    │ • FastAPI       │    │ • React SPA     │
│ • Flex Sensors  │───▶│ • WebSocket     │◀───│ • WebSocket     │
│ • MPU6050 IMU   │    │ • TensorFlow    │    │ • TTS Engine    │
│ • Serial Comm   │    │ • MongoDB       │    │ • Real-time UI  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Component Details

### 1. Hardware Layer (Arduino/ESP32)

**Components:**
- **ESP32 Microcontroller**: Main processing unit
- **5x Flex Sensors**: Finger bend detection (0-1023 analog values)
- **MPU6050 IMU**: 6-axis motion sensor (accelerometer + gyroscope)
- **Serial Communication**: USB connection to backend

**Data Format:**
```
flex1,flex2,flex3,flex4,flex5,accX,accY,accZ,gyroX,gyroY,gyroZ,timestamp
```

**Arduino Sketches:**
- `sketch_realtime.ino`: Single-hand real-time data collection
- `dual_hand_sketch.ino`: Dual-hand system support
- `sketch.ino`: Basic data collection

### 2. Data Collection Layer

**Python Scripts:**
- `collect_stream.py`: Real-time data streaming to WebSocket
- `collect_data.py`: Batch data collection for training
- `collect_dual_hand_data.py`: Dual-hand data collection

**Data Processing:**
- **Regularization**: Noise reduction and smoothing
- **Normalization**: Sensor value scaling (0-1)
- **IMU Processing**: Roll, pitch, yaw calculations
- **Queue Management**: Rate limiting and buffering

### 3. Backend Services (FastAPI)

**Core Services:**
```
backend/
├── main.py                 # FastAPI application entry point
├── routes/
│   ├── liveWS.py          # WebSocket real-time predictions
│   ├── predict_routes.py  # REST API predictions
│   ├── training_routes.py # Model training endpoints
│   ├── auth_routes.py     # Authentication & authorization
│   └── ...
├── core/
│   ├── model.py           # TensorFlow Lite model interface
│   ├── database.py        # MongoDB connection
│   └── settings.py        # Configuration management
└── AI/
    ├── gesture_model.tflite # Trained ML model
    ├── model.py            # Model training script
    └── train_dual_hand_model.py
```

**Key Features:**
- **WebSocket Server**: Real-time bidirectional communication
- **Prediction Queue**: Asynchronous prediction processing
- **Model Management**: TensorFlow Lite model loading/inference
- **Authentication**: JWT-based user management
- **Database**: MongoDB for data persistence

### 4. Machine Learning Pipeline

**Model Architecture:**
- **Framework**: TensorFlow Lite
- **Input**: 11 features (5 flex + 3 accel + 3 gyro)
- **Output**: 7 gesture classes
- **Labels**: ["Hello", "Yes", "No", "We", "Are", "Students", "Rest"]

**Training Process:**
1. **Data Collection**: CSV-based gesture recording
2. **Preprocessing**: Regularization and normalization
3. **Model Training**: Neural network training
4. **Quantization**: Model optimization for edge deployment
5. **Deployment**: TFLite model integration

### 5. Frontend Interface (React)

**Components:**
```
frontend/src/
├── pages/
│   ├── LivePredict.jsx    # Real-time prediction interface
│   ├── Dashboard.jsx      # System overview
│   ├── Predict.jsx        # Manual prediction testing
│   └── ...
├── components/
│   ├── VoiceStreaming.jsx # TTS integration
│   └── ...
└── api/
    └── api.js            # Backend communication
```

**Features:**
- **Real-time UI**: Live prediction display
- **TTS Integration**: Browser-based text-to-speech
- **WebSocket Client**: Real-time data streaming
- **Responsive Design**: Mobile-friendly interface
- **Authentication**: User login/management

## 🔄 Data Flow Architecture

### Real-time Prediction Flow:
```
Arduino Sensors → Serial → collect_stream.py → WebSocket → Backend → ML Model → Prediction → Frontend → TTS
```

### Training Data Flow:
```
Arduino Sensors → Serial → collect_data.py → CSV → Training Script → TFLite Model → Backend Integration
```

## 🌐 Network Architecture

**Development Environment:**
- **Backend**: `http://localhost:8000`
- **Frontend**: `http://localhost:3000` (Vite dev server)
- **WebSocket**: `ws://localhost:8000/ws/stream`
- **Database**: MongoDB (local or Atlas)

**Production Deployment:**
- **Docker**: Containerized services
- **Nginx**: Reverse proxy and static file serving
- **MongoDB Atlas**: Cloud database
- **HTTPS/WSS**: Secure communication

## 🔐 Security Architecture

**Authentication:**
- **JWT Tokens**: Stateless authentication
- **Role-based Access**: Viewer, Editor, Admin roles
- **Session Management**: Token refresh and validation

**Data Security:**
- **CORS Configuration**: Cross-origin request handling
- **Input Validation**: Sensor data sanitization
- **Rate Limiting**: WebSocket message throttling

## 📱 User Interface Architecture

**Pages Structure:**
- **Dashboard**: System overview and metrics
- **Live Predict**: Real-time gesture recognition
- **Manual Predict**: Single gesture testing
- **Training**: Model training and data management
- **Admin Tools**: System administration
- **TTS Manager**: Text-to-speech configuration

**State Management:**
- **React Hooks**: Local component state
- **WebSocket State**: Real-time connection management
- **TTS State**: Speech synthesis queue management

## 🚀 Deployment Architecture

**Development:**
```bash
# Backend
cd backend && python run_server.py

# Frontend  
cd frontend && npm run dev

# Data Collection
python collect_stream.py
```

**Production (Docker):**
```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
  frontend:
    build: ./frontend
    ports: ["80:80"]
  mongodb:
    image: mongo
    ports: ["27017:27017"]
```

## 🔧 Configuration Management

**Environment Variables:**
- **Database**: MongoDB connection strings
- **CORS**: Allowed origins
- **Authentication**: JWT secrets
- **Model Paths**: TFLite model locations

**Settings Files:**
- `backend/core/settings.py`: Backend configuration
- `frontend/vite.config.js`: Frontend build configuration
- `docker-compose.yml`: Container orchestration

## 📊 Monitoring & Logging

**Logging:**
- **Backend**: Python logging with file rotation
- **Frontend**: Browser console logging
- **WebSocket**: Connection and message logging

**Metrics:**
- **Performance**: Prediction latency tracking
- **Usage**: WebSocket connection counts
- **Errors**: Exception tracking and reporting

## 🔄 System Integration Points

**External APIs:**
- **MongoDB**: Data persistence
- **Browser TTS**: Speech synthesis
- **Serial Port**: Hardware communication

**Internal APIs:**
- **REST Endpoints**: CRUD operations
- **WebSocket**: Real-time communication
- **File Upload**: Training data management

## 🎯 Key Features

1. **Real-time Recognition**: Sub-second gesture prediction
2. **Dual-hand Support**: Left and right hand coordination
3. **TTS Integration**: Voice feedback for accessibility
4. **Training Pipeline**: Continuous model improvement
5. **Multi-user Support**: Role-based access control
6. **Responsive Design**: Cross-platform compatibility

## 🛠️ Development Tools

**Backend:**
- **FastAPI**: Modern Python web framework
- **TensorFlow**: Machine learning framework
- **MongoDB**: NoSQL database
- **WebSockets**: Real-time communication

**Frontend:**
- **React**: Component-based UI framework
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first styling
- **React Toastify**: Notification system

**Hardware:**
- **Arduino IDE**: ESP32 development
- **PlatformIO**: Advanced embedded development
- **Serial Monitor**: Debug communication

This architecture provides a robust, scalable foundation for sign language recognition with real-time capabilities and accessibility features.
