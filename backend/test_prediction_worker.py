#!/usr/bin/env python3
"""
Test if the prediction worker is actually running
"""

import asyncio
import websockets
import json
import time

async def test_prediction_worker():
    """Test if prediction worker is running"""
    uri = "ws://localhost:8000/ws/stream"
    
    try:
        print("🔍 Testing Prediction Worker")
        print("=" * 40)
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Send multiple test messages to see if worker responds
            for i in range(3):
                test_data = {
                    "right": [0.4, 0.45, 0.38, 0.42, 0.41, 100, -50, 200, 10, -5, 15],
                    "timestamp": time.time()
                }
                
                print(f"📤 Sending message {i+1}...")
                await websocket.send(json.dumps(test_data))
                
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"📥 Response {i+1}: {response}")
                    
                    data = json.loads(response)
                    if "prediction" in data:
                        print(f"🎯 Prediction: {data['prediction']}")
                    else:
                        print(f"⚠️ No prediction: {data}")
                        
                except asyncio.TimeoutError:
                    print(f"⏰ No response for message {i+1}")
                
                await asyncio.sleep(1)
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_prediction_worker())
