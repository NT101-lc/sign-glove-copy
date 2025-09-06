#!/usr/bin/env python3
"""
Slow TTS test script - sends data less frequently to prevent TTS interruptions
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

async def slow_tts_test():
    """Send data slowly to test TTS without interruptions"""
    uri = "ws://localhost:8000/ws/stream"
    
    try:
        print("🎤 Slow TTS Test - Prevents TTS Interruptions")
        print("=" * 60)
        print("📋 This will send data every 3 seconds to prevent TTS interruptions")
        print("🎯 Open frontend Live Predict page, connect, and enable TTS")
        print("⏹️  Press Ctrl+C to stop")
        print("=" * 60)
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            message_count = 0
            while True:
                # Generate test data
                test_data = {
                    "right": generate_test_data(),
                    "timestamp": time.time()
                }
                
                # Send data
                await websocket.send(json.dumps(test_data))
                message_count += 1
                
                # Show what we're sending
                flex_vals = [f"{val:.2f}" for val in test_data["right"][:5]]
                print(f"📤 [{message_count:3d}] Sent data | flex={flex_vals}")
                
                # Try to receive prediction
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    
                    if "prediction" in data:
                        confidence = data.get('confidence', 0)
                        print(f"🎯 Prediction: '{data['prediction']}' (conf: {confidence:.2f})")
                        print("   🔊 TTS should speak this word now...")
                    else:
                        print(f"📥 Response: {data}")
                        
                except asyncio.TimeoutError:
                    print("⏰ No response received")
                except Exception as e:
                    print(f"❌ Error receiving response: {e}")
                
                # Wait 3 seconds between messages (much slower)
                print("⏳ Waiting 3 seconds before next prediction...")
                await asyncio.sleep(3.0)
                
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped after sending {message_count} messages")
    except ConnectionRefusedError:
        print("❌ Connection refused. Make sure backend is running:")
        print("   python run_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(slow_tts_test())
