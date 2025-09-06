#!/usr/bin/env python3
"""
Test script for frontend TTS real-time prediction
Continuously sends realistic Arduino data to test the frontend WebSocket connection
"""

import asyncio
import websockets
import json
import time
import random

def generate_realistic_arduino_data():
    """Generate realistic Arduino sensor data"""
    # Flex sensors (0-1023 range, typically 200-800 for normal hand positions)
    flex_sensors = [random.randint(200, 800) for _ in range(5)]
    
    # Accelerometer data (MPU6050 raw values)
    accel = [random.randint(-2000, 2000) for _ in range(3)]
    
    # Gyroscope data (MPU6050 raw values)
    gyro = [random.randint(-500, 500) for _ in range(3)]
    
    return flex_sensors + accel + gyro

def simulate_regularization(raw_data):
    """Simulate the regularization process"""
    processed = []
    
    # Normalize flex sensors (0-1023 -> 0-1)
    for i in range(5):
        processed.append(raw_data[i] / 1023.0)
    
    # Keep accelerometer and gyroscope as-is
    processed.extend(raw_data[5:11])
    
    return processed

async def continuous_data_stream():
    """Continuously send data to test frontend TTS"""
    uri = "ws://localhost:8000/ws/stream"
    
    try:
        print(f"🔌 Connecting to WebSocket: {uri}")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket successfully!")
            print("📡 Sending continuous data for frontend TTS testing...")
            print("🎯 Open the frontend Live Prediction page and enable TTS!")
            print("⏹️  Press Ctrl+C to stop")
            print("=" * 60)
            
            message_count = 0
            while True:
                # Generate raw Arduino data
                raw_arduino_data = generate_realistic_arduino_data()
                
                # Simulate the regularization process
                processed_data = simulate_regularization(raw_arduino_data)
                
                # Create payload
                payload = {
                    "right": processed_data,
                    "timestamp": time.time()
                }
                
                # Send data
                await websocket.send(json.dumps(payload))
                message_count += 1
                
                # Show progress every 10 messages
                if message_count % 10 == 0:
                    flex_vals = [f"{val:.2f}" for val in processed_data[:5]]
                    print(f"📤 Sent {message_count:3d} messages | flex={flex_vals}")
                
                # Try to receive prediction (non-blocking)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                    data = json.loads(response)
                    
                    if "prediction" in data:
                        confidence = data.get('confidence', 0)
                        print(f"🎯 Prediction: '{data['prediction']}' (conf: {confidence:.2f})")
                except asyncio.TimeoutError:
                    pass  # No response yet, continue
                except Exception as e:
                    print(f"❌ Error receiving response: {e}")
                
                # Rate limiting (10Hz = 100ms intervals, same as Arduino)
                await asyncio.sleep(0.1)
                
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped after sending {message_count} messages")
    except ConnectionRefusedError:
        print("❌ Connection refused. Make sure the backend server is running on port 8000")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")

if __name__ == "__main__":
    print("🎤 Frontend TTS Real-time Prediction Test")
    print("=" * 60)
    print("📋 Instructions:")
    print("1. Make sure backend is running (python run_server.py)")
    print("2. Open frontend in browser")
    print("3. Go to Live Prediction page")
    print("4. Click 'Connect' button")
    print("5. Enable TTS by clicking 'TTS Enabled' button")
    print("6. Watch for predictions and listen for TTS audio!")
    print("=" * 60)
    
    input("Press Enter when ready to start sending data...")
    
    asyncio.run(continuous_data_stream())
