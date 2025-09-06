#!/usr/bin/env python3
"""
Simple WebSocket test to verify the endpoint is working
"""

import asyncio
import websockets
import json
import time

async def test_websocket_simple():
    """Test WebSocket with simple data"""
    uri = "ws://localhost:8000/ws/stream"
    
    try:
        print("🔍 Simple WebSocket Test")
        print("=" * 40)
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Send a simple test message
            test_data = {
                "right": [0.4, 0.45, 0.38, 0.42, 0.41, 100, -50, 200, 10, -5, 15],
                "timestamp": time.time()
            }
            
            print(f"📤 Sending: {json.dumps(test_data)}")
            await websocket.send(json.dumps(test_data))
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            print(f"📥 Received: {response}")
            
            data = json.loads(response)
            if "prediction" in data:
                print(f"🎯 Prediction: {data['prediction']}")
                print(f"📊 Confidence: {data.get('confidence', 'N/A')}")
                print("✅ WebSocket is working correctly!")
            else:
                print("❌ No prediction in response")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_simple())
