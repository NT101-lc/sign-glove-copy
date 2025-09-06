#!/usr/bin/env python3
"""
Debug WebSocket connection to see what's happening
"""

import asyncio
import websockets
import json
import time
import random

def generate_test_data():
    """Generate test sensor data"""
    flex_sensors = [random.randint(200, 800) for _ in range(5)]
    accel = [random.randint(-2000, 2000) for _ in range(3)]
    gyro = [random.randint(-500, 500) for _ in range(3)]
    
    # Normalize flex sensors
    processed = [f/1023.0 for f in flex_sensors]
    processed.extend(accel + gyro)
    
    return processed

async def debug_websocket():
    """Debug WebSocket connection"""
    uri = "ws://localhost:8000/ws/stream"
    
    try:
        print("🔍 WebSocket Debug - Checking message format")
        print("=" * 50)
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Send a test message and see what happens
            test_data = {
                "right": generate_test_data(),
                "timestamp": time.time()
            }
            
            print(f"📤 Sending data: {json.dumps(test_data, indent=2)}")
            await websocket.send(json.dumps(test_data))
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"📥 Received response: {json.dumps(data, indent=2)}")
                
                if "prediction" in data:
                    print(f"✅ Prediction: {data['prediction']}")
                    print(f"📊 Confidence: {data.get('confidence', 'N/A')}")
                else:
                    print("❌ No prediction in response")
                    
            except asyncio.TimeoutError:
                print("⏰ No response received (timeout)")
            except Exception as e:
                print(f"❌ Error receiving response: {e}")
                
    except Exception as e:
        print(f"❌ WebSocket error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_websocket())
