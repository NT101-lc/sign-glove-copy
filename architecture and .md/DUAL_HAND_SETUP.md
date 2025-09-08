# 🧤 Dual-Hand Sign Glove Setup Guide

This guide will help you set up and use the dual-hand sign glove system for synchronized gesture recognition.

## 🎯 Overview

The dual-hand system allows you to:
- **Collect data from both hands simultaneously** (22 sensors total)
- **Train a model on combined hand movements** for more accurate recognition
- **Perform real-time prediction** using both hands
- **Achieve better gesture recognition** by considering hand coordination

## 📋 Prerequisites

- ✅ Two Arduino/ESP32 boards with sensors
- ✅ Two sets of flex sensors (5 per hand)
- ✅ Two MPU6050 IMU modules
- ✅ Python backend environment
- ✅ MongoDB database running

## 🔧 Hardware Setup

### 1. First Glove (Left Hand)
- **Arduino File**: `arduino/sketch.ino`
- **Serial Port**: Configure in `collect_dual_hand_data.py`
- **Sensor Pins**: 
  - Flex: 36, 34, 35, 32, 33
  - IMU: I2C (SDA/SCL)

### 2. Second Glove (Right Hand)
- **Arduino File**: `arduino/dual_hand_sketch.ino`
- **Serial Port**: Configure in `collect_dual_hand_data.py`
- **Sensor Pins**:
  - Flex: 25, 26, 27, 14, 12
  - IMU: I2C (SDA/SCL)

### 3. Connection Setup
```
Left Glove  → COM5 (or your port)
Right Glove → COM6 (or your port)
```

## 🚀 Setup Steps

### Step 1: Upload Arduino Code

1. **First Glove**:
   ```bash
   # Open arduino/sketch.ino in Arduino IDE
   # Select correct board and port
   # Upload to first Arduino
   ```

2. **Second Glove**:
   ```bash
   # Open arduino/dual_hand_sketch.ino in Arduino IDE
   # Select correct board and port
   # Upload to second Arduino
   ```

### Step 2: Configure Data Collection

Edit `backend/ingestion/collect_dual_hand_data.py`:
```python
LEFT_HAND_PORT = 'COM5'   # 👈 Your left hand port
RIGHT_HAND_PORT = 'COM6'  # 👈 Your right hand port
LABEL = 'Hello'           # 👈 Gesture you're collecting
SESSION_ID = 'dual_g1'    # 👈 Session identifier
```

### Step 3: Collect Training Data

```bash
cd backend/ingestion
python collect_dual_hand_data.py
```

**Data Collection Process**:
1. Wear both gloves
2. Perform the target gesture (e.g., "Hello")
3. Hold the gesture for several seconds
4. Repeat with different gestures
5. Collect at least 100-200 samples per gesture

**Expected Output**:
- CSV file: `data/dual_hand_raw_data.csv`
- MongoDB: Sensor data stored in database
- Real-time: WebSocket streaming to frontend

### Step 4: Train Dual-Hand Model

```bash
cd backend/AI
python train_dual_hand_model.py
```

**Training Process**:
- Loads 22-input data (11 per hand)
- Creates neural network model
- Trains on collected data
- Saves model as `gesture_model_dual.tflite`
- Generates training metrics and plots

### Step 5: Test the System

```bash
cd backend
python test_dual_hand.py
```

## 🔍 Data Structure

### Input Format (22 Sensors)
```
Left Hand (11 sensors):
├── Flex sensors: [flex1, flex2, flex3, flex4, flex5]
├── Accelerometer: [accX, accY, accZ]
└── Gyroscope: [gyroX, gyroY, gyroZ]

Right Hand (11 sensors):
├── Flex sensors: [flex1, flex2, flex3, flex4, flex5]
├── Accelerometer: [accX, accY, accZ]
└── Gyroscope: [gyroX, gyroY, gyroZ]

Total: 22 sensor values
```

### CSV Output Format
```csv
session_id,label,timestamp,left_flex_1,left_flex_2,...,right_gyro_3
dual_g1,Hello,1234567890,100,200,300,400,500,10,20,30,5,15,25,150,250,350,450,550,15,25,35,8,18,28
```

## 🌐 Real-Time Prediction

### WebSocket Endpoint
```
ws://localhost:8000/ws/predict
```

### Input Data Format
```json
{
  "left": [100, 200, 300, 400, 500, 10, 20, 30, 5, 15, 25],
  "right": [150, 250, 350, 450, 550, 15, 25, 35, 8, 18, 28],
  "timestamp": 1234567890
}
```

### Output Format
```json
{
  "status": "success",
  "left_prediction": "Hello",
  "right_prediction": "Hello",
  "confidence": 0.95,
  "timestamp": 1234567890,
  "model_type": "dual_hand"
}
```

## 🧪 Testing

### 1. Test Data Collection
```bash
# Check if both gloves are connected
python test_dual_hand.py
```

### 2. Test Real-Time Prediction
1. Start the backend: `python main.py`
2. Open frontend: `npm run dev`
3. Go to Live Prediction page
4. Connect WebSocket
5. Send test data with both hands

### 3. Test Model Training
```bash
# Check training metrics
ls backend/AI/results/
cat backend/AI/results/dual_hand_training_metrics.json
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Connection Errors**:
   - Check device manager for correct COM ports
   - Ensure Arduino drivers are installed
   - Try different USB cables

2. **Sensor Reading Issues**:
   - Verify sensor connections
   - Check power supply
   - Calibrate sensors if needed

3. **Model Training Errors**:
   - Ensure sufficient training data (100+ samples per gesture)
   - Check data format in CSV
   - Verify TensorFlow installation

4. **Prediction Errors**:
   - Check if dual-hand model exists
   - Verify sensor data format
   - Check WebSocket connection

### Debug Commands

```bash
# Check serial ports
python -m serial.tools.list_ports

# Test individual glove
python -c "import serial; ser=serial.Serial('COM5',115200); print(ser.readline())"

# Check model files
ls -la backend/AI/*.tflite

# Test prediction function
python test_dual_hand.py
```

## 📊 Performance Tips

1. **Data Quality**:
   - Collect data in consistent lighting conditions
   - Maintain consistent hand positioning
   - Use clear, distinct gestures

2. **Training Optimization**:
   - Collect balanced data per gesture
   - Use data augmentation if needed
   - Experiment with model architecture

3. **Real-Time Performance**:
   - Optimize sensor sampling rate
   - Use efficient data processing
   - Consider model quantization

## 🔮 Future Enhancements

- **Independent Hand Recognition**: Separate models for each hand
- **Gesture Coordination**: Analyze hand movement patterns
- **Multi-User Support**: Multiple glove pairs
- **Advanced Gestures**: Complex sign language sequences
- **Mobile Deployment**: Edge device optimization

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review error logs in `backend/logs/`
3. Test individual components
4. Verify hardware connections

---

**Happy dual-hand signing! 🧤✌️** 