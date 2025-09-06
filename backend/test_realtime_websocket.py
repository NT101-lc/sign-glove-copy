#!/usr/bin/env python3
"""
Test script for real-time prediction WebSocket
Simulates Arduino data exactly as it would be sent through the system
"""

import asyncio
import websockets
import json
import time
import random
import numpy as np

def generate_realistic_arduino_data():
    """
    Generate realistic Arduino sensor data based on the actual sketch:
    - Flex sensors: 0-1023 (ESP32 analogRead)
    - Accelerometer: -16000 to 16000 (MPU6050 raw values)  
    - Gyroscope: -2000 to 2000 (MPU6050 raw values)
    """
    # Flex sensors (0-1023 range, typically 200-800 for normal hand positions)
    flex_sensors = [random.randint(200, 800) for _ in range(5)]
    
    # Accelerometer data (MPU6050 raw values, typically -2000 to 2000 for normal movement)
    accel = [random.randint(-2000, 2000) for _ in range(3)]
    
    # Gyroscope data (MPU6050 raw values, typically -500 to 500 for normal movement)
    gyro = [random.randint(-500, 500) for _ in range(3)]
    
    return flex_sensors + accel + gyro

def simulate_regularization(raw_data):
    """
    Simulate the regularization process that happens in collect_stream.py
    This is a simplified version - the real one is more complex
    """
    # For testing, we'll just normalize the data roughly
    processed = []
    
    # Normalize flex sensors (0-1023 -> 0-1)
    for i in range(5):
        processed.append(raw_data[i] / 1023.0)
    
    # Keep accelerometer and gyroscope as-is for now (they get processed differently)
    processed.extend(raw_data[5:11])
    
    return processed

async def test_websocket_connection():
    """Test the WebSocket connection with realistic Arduino data"""
    uri = "ws://localhost:8000/ws/stream"
    
    try:
        print(f"🔌 Connecting to WebSocket: {uri}")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket successfully!")
            print("📡 Starting to send simulated Arduino data...")
            print("=" * 60)
            
            # Send test data for 10 seconds (100 messages at 10Hz)
            for i in range(100):
                # Generate raw Arduino data
                raw_arduino_data = generate_realistic_arduino_data()
                
                # Simulate the regularization process
                processed_data = simulate_regularization(raw_arduino_data)
                
                # Create payload in the expected format (same as collect_stream.py)
                payload = {
                    "right": processed_data,  # 11 processed features
                    "timestamp": time.time()
                }
                
                # Send data
                await websocket.send(json.dumps(payload))
                
                # Show what we're sending (first 5 values are flex sensors)
                flex_vals = [f"{val:.3f}" for val in processed_data[:5]]
                print(f"📤 [{i+1:3d}] Sent: flex={flex_vals} | acc={processed_data[5:8]} | gyro={processed_data[8:11]}")
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    
                    if "prediction" in data:
                        confidence = data.get('confidence', 0)
                        print(f"🎯 Prediction: '{data['prediction']}' (confidence: {confidence:.3f})")
                    elif "error" in data:
                        print(f"❌ Error: {data['error']}")
                    else:
                        print(f"📥 Response: {data}")
                        
                except asyncio.TimeoutError:
                    print("⏰ No response received (timeout)")
                except Exception as e:
                    print(f"❌ Error receiving response: {e}")
                
                # Rate limiting (10Hz = 100ms intervals, same as Arduino)
                await asyncio.sleep(0.1)
                
    except ConnectionRefusedError:
        print("❌ Connection refused. Make sure the backend server is running on port 8000")
        print("   Run: python run_server.py")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")

async def test_single_prediction():
    """Test a single prediction to verify the system is working"""
    print("🔍 Testing single prediction...")
    
    uri = "ws://localhost:8000/ws/stream"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Send a single test message with realistic data
            test_data = {
                "right": [0.4, 0.45, 0.38, 0.42, 0.41, 100, -50, 200, 10, -5, 15],  # 11 sensor values
                "timestamp": time.time()
            }
            
            await websocket.send(json.dumps(test_data))
            print("📤 Sent test data")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            if "prediction" in data:
                print(f"✅ Prediction worker is working!")
                print(f"🎯 Prediction: '{data['prediction']}'")
                print(f"📊 Confidence: {data.get('confidence', 'N/A')}")
                return True
            else:
                print(f"⚠️ Unexpected response: {data}")
                return False
                
    except Exception as e:
        print(f"❌ Single prediction test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Sign Glove Real-time Prediction Test")
    print("=" * 60)
    print("📋 Arduino Data Format:")
    print("   - Flex sensors: 0-1023 (ESP32 analogRead)")
    print("   - Accelerometer: -16000 to 16000 (MPU6050 raw)")
    print("   - Gyroscope: -2000 to 2000 (MPU6050 raw)")
    print("   - Sampling rate: 10Hz (100ms intervals)")
    print("=" * 60)
    
    # First test single prediction
    print("\n1️⃣ Testing single prediction...")
    success = asyncio.run(test_single_prediction())
    
    if success:
        print("\n2️⃣ Testing continuous data stream...")
        print("   (This will send 100 messages over 10 seconds)")
        input("   Press Enter to continue...")
        asyncio.run(test_websocket_connection())
    else:
        print("\n❌ Single prediction failed. Check the backend server and logs.")
    
    print("\n✅ Test completed!")
