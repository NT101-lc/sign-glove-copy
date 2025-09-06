"""
Async WebSocket API for real-time gesture prediction using trained AI
with a prediction queue, stale-message skipping, and proper startup of the worker.
"""

import logging
import asyncio
import json
import time
import numpy as np
from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect
import tensorflow as tf

logger = logging.getLogger("signglove")
router = APIRouter(prefix="/ws", tags=["WebSocket"])

# ------------------- CONFIG -------------------
RATE_LIMIT_SECONDS = 0.5  # ~ messages/sec per client
rate_limiter = {}

# Load TFLite model
import os
TFLITE_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'AI', 'gesture_model.tflite')
interpreter = tf.lite.Interpreter(model_path=TFLITE_MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

GESTURE_LABELS = ["Hello", "Yes", "No", "We", "Are", "Students", "Rest"]

# ------------------- HELPER FUNCTIONS -------------------
def preprocess_sensor_data(sensor_values):
    if len(sensor_values) != 11:
        raise ValueError(f"Expected 11 features, got {len(sensor_values)}")
    x = np.array(sensor_values, dtype=np.float32).reshape(1, 11)
    for i in range(5):  # normalize flex sensors
        x[0, i] /= 1023.0
    return x

def predict_gesture(sensor_values):
    x = preprocess_sensor_data(sensor_values)
    start = time.time()
    interpreter.set_tensor(input_details[0]['index'], x)
    interpreter.invoke()
    y_pred = interpreter.get_tensor(output_details[0]['index'])[0]
    end = time.time()
    print(f"[TFLite] Prediction took {end - start:.4f} seconds")
    pred_index = int(np.argmax(y_pred))
    return GESTURE_LABELS[pred_index], float(y_pred[pred_index])

# ------------------- PREDICTION QUEUE -------------------
prediction_queue = asyncio.Queue()
queue_lock = asyncio.Lock()  # ensure only one prediction at a time
latest_message_per_client = {}  # store latest sensor data per client

async def prediction_worker():
    print("[Worker] Prediction worker started")
    logger.info("Prediction worker started")
    
    while True:
        try:
            print("[Worker] Waiting for messages in queue...")
            websocket, sensor_values, client_ip = await prediction_queue.get()
            print(f"[Worker] Got message from {client_ip}")
            
            try:
                # Skip stale messages if newer ones exist for this client
                if latest_message_per_client.get(client_ip) != sensor_values:
                    print(f"[Worker] Skipping stale message from {client_ip}")
                    prediction_queue.task_done()
                    continue

                async with queue_lock:
                    print(f"[Worker] Processing message from {client_ip}: {sensor_values}")
                    pred, conf = await asyncio.get_event_loop().run_in_executor(None, predict_gesture, sensor_values)
                    response = {
                        "timestamp": time.time(),
                        "prediction": pred,
                        "confidence": conf
                    }
                    print(f"[Worker] Sending response: {response}")
                    await websocket.send_json(response)
            except Exception as e:
                logger.error(f"Prediction worker error: {e}")
                print(f"[Worker] Error: {e}")
                try:
                    await websocket.send_json({"error": str(e)})
                except Exception:
                    pass  # websocket may be closed
            finally:
                prediction_queue.task_done()
        except Exception as e:
            logger.error(f"Prediction worker loop error: {e}")
            print(f"[Worker] Loop error: {e}")
            await asyncio.sleep(1)  # Wait before retrying

# ------------------- WEBSOCKET ENDPOINT -------------------
@router.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    client_ip = websocket.client.host
    await websocket.accept()
    logger.info(f"WebSocket connected: {client_ip}")
    print(f"[WebSocket] Connected: {client_ip}")

    try:
        while True:
            data_text = await websocket.receive_text()
            print(f"[WebSocket] Received data from {client_ip}: {data_text[:100]}...")

            # Rate limiting
            now = time.time()
            last_time = rate_limiter.get(client_ip, 0)
            if now - last_time < RATE_LIMIT_SECONDS:
                print(f"[WebSocket] Rate limited for {client_ip}")
                continue
            rate_limiter[client_ip] = now

            try:
                payload = json.loads(data_text)
                sensor_values = payload.get("right", [])
                print(f"[WebSocket] Parsed sensor values: {len(sensor_values)} values")

                if not sensor_values or len(sensor_values) != 11:
                    print(f"[WebSocket] Invalid sensor data: {len(sensor_values)} values")
                    await websocket.send_json({"error": "Invalid sensor data"})
                    continue

                # Update latest message per client
                latest_message_per_client[client_ip] = sensor_values

                # Add to prediction queue
                print(f"[WebSocket] Adding to prediction queue for {client_ip}")
                await prediction_queue.put((websocket, sensor_values, client_ip))
                print(f"[WebSocket] Queue size: {prediction_queue.qsize()}")

            except json.JSONDecodeError as e:
                logger.warning(f"{client_ip}: invalid JSON received: {e}")
                print(f"[WebSocket] JSON decode error: {e}")
            except Exception as e:
                logger.error(f"{client_ip}: WebSocket error: {e}")
                print(f"[WebSocket] Error: {e}")
                await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {client_ip}")
        print(f"[WebSocket] Disconnected: {client_ip}")
        rate_limiter.pop(client_ip, None)
        latest_message_per_client.pop(client_ip, None)
    except Exception as e:
        logger.error(f"WebSocket error ({client_ip}): {e}")
        print(f"[WebSocket] Error: {e}")
        await websocket.close()

# ------------------- STARTUP FUNCTION -------------------
async def start_prediction_worker():
    """Start the prediction worker task. Call this from main app startup."""
    asyncio.create_task(prediction_worker())
    print("[Startup] Prediction worker task scheduled")
