from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import tensorflow as tf
import pyttsx3
import threading
import time
import os

router = APIRouter(prefix="/gesture", tags=["gesture"])

# ---------------- CONFIG ----------------
TFLITE_MODEL_PATH = os.path.join("AI", "gesture_model.tflite")
GESTURE_LABELS = ["Hello", "Yes", "No", "We", "Are", "Students", "Rest"]
SKIP_GESTURES = ["Rest"]
TTS_DEBOUNCE_SECONDS = 2.0

# ---------------- MODEL ----------------
interpreter = tf.lite.Interpreter(model_path=TFLITE_MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# ---------------- TTS ----------------
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)
tts_lock = threading.Lock()
last_tts_time = 0.0
last_spoken_text = None

def speak(text):
    global last_tts_time, last_spoken_text
    if text in SKIP_GESTURES:
        return
    with tts_lock:
        now = time.time()
        if text == last_spoken_text and (now - last_tts_time) < TTS_DEBOUNCE_SECONDS:
            return
        try:
            engine.say(text)
            engine.runAndWait()
            last_tts_time = now
            last_spoken_text = text
        except Exception as e:
            print(f"TTS error: {e}")

# ---------------- PREDICTION ----------------
from ingestion.live_data import get_latest_data

def preprocess_sensor_data(sensor_values):
    x = np.array(sensor_values, dtype=np.float32).reshape(1, 11)
    return x

def predict_gesture(sensor_values):
    x = preprocess_sensor_data(sensor_values)
    interpreter.set_tensor(input_details[0]['index'], x)
    interpreter.invoke()
    y_pred = interpreter.get_tensor(output_details[0]['index'])[0]
    pred_index = int(np.argmax(y_pred))
    return GESTURE_LABELS[pred_index], float(y_pred[pred_index])

# ---------------- POST MODEL ----------------
class LiveSensorData(BaseModel):
    values: Optional[List[float]] = None
    session_id: Optional[str] = None

@router.post("/live-predict")
async def live_predict(sensor_data: LiveSensorData):
    """Receive Arduino POST, update latest data, and run TTS asynchronously."""
    try:
        sensor_values = sensor_data.values
        if sensor_values and len(sensor_values) == 11:
            from ingestion.live_data import update_data
            update_data(sensor_values)
            pred, conf = predict_gesture(sensor_values)
            
            # Run TTS in separate thread
            threading.Thread(target=speak, args=(pred,)).start()
            
            return JSONResponse({
                "status": "success",
                "prediction": pred,
                "confidence": conf,
                "real_sensor": True,
                "session_id": sensor_data.session_id
            })
        else:
            return JSONResponse({
                "status": "error",
                "message": "Invalid sensor data",
                "real_sensor": False
            }, status_code=400)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.get("/latest")
async def latest_sensor():
    """Return the latest sensor data for frontend polling."""
    data = get_latest_data()
    if data is None:
        return {"values": [], "real_sensor": False}
    pred, conf = predict_gesture(data)
    return {"values": data, "prediction": pred, "confidence": conf, "real_sensor": True}
