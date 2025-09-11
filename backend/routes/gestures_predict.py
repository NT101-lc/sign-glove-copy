# backend/routes/gesture_routes.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from core.model import predict_gesture
from core.tts import TTSWorker
from ingestion.streaming.live_data import update_data, get_latest_data
from pydantic import BaseModel
from typing import List, Optional
import logging
import asyncio

# Initialize logger
logger = logging.getLogger("signglove")

router = APIRouter(prefix="/gesture", tags=["gesture"])

# TTS worker instance
tts_worker = TTSWorker()

# ---------------- POST MODELS ----------------
class SensorData(BaseModel):
    sensor_values: List[List[float]]  # allow sequence of frames
    session_id: Optional[str] = None

# ---------------- ENDPOINTS ----------------
@router.post("/predict")
async def predict(sensor_data: SensorData):
    try:
        sequence = sensor_data.sensor_values
        update_data(sequence[-1])
        prediction = predict_gesture(sequence)
        tts_worker.enqueue(prediction)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "prediction": prediction,
                "session_id": sensor_data.session_id
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@router.get("/latest")
async def latest_sensor():
    data = get_latest_data()
    if not data:
        return {"values": [], "real_sensor": False}
    pred = predict_gesture([data])
    return {"values": data, "prediction": pred, "real_sensor": True}

# ---------------- WEBSOCKET MANAGER ----------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except:
                pass  # ignore send errors

# Separate managers for clarity
stream_manager = ConnectionManager()
predict_manager = ConnectionManager()

# ---------------- LIVE STREAM ----------------
@router.websocket("/stream")
async def stream_ws(websocket: WebSocket):
    await stream_manager.connect(websocket)
    try:
        while True:
            try:
                # Wait briefly for keep-alive messages from frontend, but non-blocking
                await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
            except asyncio.TimeoutError:
                pass  # no message received, continue
            except WebSocketDisconnect:
                break
            except Exception as e:
                print("Receive error:", e)
                break
            # No need to predict here anymore, frontend will get broadcast from collector
    except WebSocketDisconnect:
        pass
    finally:
        stream_manager.disconnect(websocket)

# ---------------- PREDICT WS ----------------
@router.websocket("/predict_ws")
async def predict_ws(websocket: WebSocket):
    await predict_manager.connect(websocket)
    logger.info("New WS connection on /predict_ws")
    try:
        while True:
            try:
                data = await websocket.receive_json()
            except WebSocketDisconnect:
                logger.info("WS client disconnected from /predict_ws")
                break
            except Exception:
                logger.warning("Received invalid JSON from WS client")
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            sequence = data.get("sensor_values")
            session_id = data.get("session_id", "unknown_session")

            if not sequence:
                logger.warning("Received empty sensor_values from WS client")
                await websocket.send_json({"error": "No sensor_values provided"})
                continue

            # Log incoming sequence
            logger.info(f"Received sequence from session {session_id}: {sequence[-1]}")

            # Update live data store
            update_data(sequence[-1])

            try:
                # Run model prediction
                prediction = predict_gesture(sequence[-1])  # single frame for simplicity

                # Log prediction result
                logger.info(f"Prediction result for session {session_id}: {prediction}")

                # Check if model loaded
                if prediction.get("status") != "success":
                    logger.warning(f"Prediction failed: {prediction.get('message')}")

                # Send prediction back to collector
                await websocket.send_json({"prediction": prediction, "session_id": session_id})

                # Broadcast prediction to frontend clients
                await stream_manager.broadcast({
                    "prediction": prediction,
                    "values": sequence[-1],
                    "session_id": session_id
                })

                # Trigger TTS if prediction is successful
                if prediction.get("status") == "success" and "prediction" in prediction:
                    tts_worker.enqueue(prediction)
                    logger.info(f"TTS enqueued for gesture: {prediction['prediction']}")

            except Exception as e:
                logger.error(f"Error during prediction for session {session_id}: {e}")
                await websocket.send_json({"error": str(e)})

    finally:
        predict_manager.disconnect(websocket)
        logger.info("WS connection removed from /predict_ws")