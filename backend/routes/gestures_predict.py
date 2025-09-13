# backend/routes/gesture_routes_tts_cooldown.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import logging
import time
from core.model import predict_gesture
from core.tts import TTSWorker

logger = logging.getLogger("signglove")
router = APIRouter(prefix="/gesture", tags=["gesture"])

EXPECTED_VALUES = 11
THROTTLE = 0.05  # 50ms per frame (~20Hz) for human-like UI speed
TTS_COOLDOWN = 0.4  # seconds before repeating the same gesture

# TTS worker
tts_worker = TTSWorker()

# ---------------- WEBSOCKET MANAGER ----------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WS client connected: {len(self.active_connections)} total")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WS client disconnected: {len(self.active_connections)} remaining")

    async def broadcast(self, message: dict):
        alive = []
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
                alive.append(conn)
            except:
                pass  # ignore send errors
        self.active_connections = alive

predict_manager = ConnectionManager()

# ---------------- PREDICT WS ----------------
@router.websocket("/predict_ws")
async def predict_ws(websocket: WebSocket):
    await predict_manager.connect(websocket)
    last_tts_time = {}  # track last TTS time per gesture

    try:
        while True:
            try:
                # Wait for JSON from client; timeout keeps connection alive
                data = await asyncio.wait_for(websocket.receive_json(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except WebSocketDisconnect:
                logger.info("WS client disconnected")
                break
            except Exception as e:
                logger.warning(f"Receive error: {e}")
                continue

            # Extract and clean sequence
            sequence = data.get("sensor_values", [])
            session_id = data.get("session_id", "unknown_session")

            clean_sequence = [
                (frame + [0.0]*(EXPECTED_VALUES - len(frame)))[:EXPECTED_VALUES]
                for frame in sequence if isinstance(frame, list) and frame
            ]
            if not clean_sequence:
                continue  # skip empty batch

            # -------- AI prediction --------
            try:
                result = predict_gesture(clean_sequence)
                gesture_name = result.get("prediction") if result.get("status") == "success" else None
            except Exception as e:
                logger.error(f"Prediction error: {e}")
                gesture_name = None

            # -------- Trigger TTS immediately with cooldown --------
            now = time.time()
            if gesture_name and gesture_name not in ["Rest"]:
                last_time = last_tts_time.get(gesture_name, 0)
                if now - last_time > TTS_COOLDOWN:
                    tts_worker.enqueue({"prediction": gesture_name})
                    last_tts_time[gesture_name] = now

            # -------- Broadcast every frame with throttling --------
            for frame in clean_sequence:
                payload = {
                    "prediction": gesture_name or "None",
                    "values": frame,
                    "session_id": session_id
                }

                # Send to sender
                try:
                    await websocket.send_json(payload)
                except Exception as e:
                    logger.warning(f"Send error to sender: {e}")

                # Broadcast to other clients
                await predict_manager.broadcast(payload)

                # Throttle to simulate human-like speed in UI
                await asyncio.sleep(THROTTLE)

    finally:
        predict_manager.disconnect(websocket)
