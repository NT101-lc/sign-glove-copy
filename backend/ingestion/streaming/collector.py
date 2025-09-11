# backend/ingestion/streaming/collector.py
import asyncio
import logging
import json
import requests
import websockets

from serial_reader import SerialReader
from preprocessing import normalize_sensor_data
from config_loader import load_config
from movement_detection import MovementDetector

# Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("collector")

# Toggle WebSocket vs HTTP POST
USE_WS = True
ws_url = "ws://127.0.0.1:8000/gesture/predict_ws"

async def ws_sender(ws_url, sequence_queue, session_id="demo", batch_size=5, batch_delay=0.05):
    """
    Continuously send gesture sequences to backend via WebSocket.
    - Batches multiple sequences before sending to reduce WS traffic.
    - batch_size: max sequences per message
    - batch_delay: max time to wait before sending batch (seconds)
    """
    headers = {"Origin": "http://localhost:5173"}  # prevent 403
    while True:
        try:
            async with websockets.connect(ws_url) as ws:
                logger.info("Connected to WS backend")
                batch = []
                while True:
                    try:
                        seq = await asyncio.wait_for(sequence_queue.get(), timeout=batch_delay)
                        batch.append(seq)
                        # send if batch full
                        if len(batch) >= batch_size:
                            payload = {"sensor_values": batch, "session_id": session_id}
                            await ws.send(json.dumps(payload))
                            logger.info(f"Sent batch via WS: {len(batch)} sequences")
                            batch.clear()
                    except asyncio.TimeoutError:
                        # send whatever is in the batch after timeout
                        if batch:
                            payload = {"sensor_values": batch, "session_id": session_id}
                            await ws.send(json.dumps(payload))
                            logger.info(f"Sent batch via WS: {len(batch)} sequences (timeout)")
                            batch.clear()
        except Exception as e:
            logger.warning(f"WebSocket error: {e}, reconnecting in 2s")
            await asyncio.sleep(2)


async def read_serial_loop(reader, detector, sequence_queue, backend_cfg):
    """Read serial values and detect gestures, ensuring 11 values per frame."""
    EXPECTED_VALUES = 11  # flex(5) + acc(3) + gyro(3)

    while True:
        raw_values = reader.read()
        if raw_values:
            # Convert all values to float
            try:
                raw_values = [float(v) for v in raw_values]
            except Exception as e:
                logger.warning(f"Skipping invalid raw values: {raw_values} ({e})")
                continue

            # Ensure exactly 11 values
            if len(raw_values) > EXPECTED_VALUES:
                raw_values = raw_values[:EXPECTED_VALUES]
            elif len(raw_values) < EXPECTED_VALUES:
                raw_values += [0.0] * (EXPECTED_VALUES - len(raw_values))  # pad missing

            normalized = normalize_sensor_data(raw_values)
            gesture_window = detector.update(normalized)

            if gesture_window is not None:
                # Make sure each frame in the window has 11 values
                gesture_window_clean = []
                for frame in gesture_window:
                    if len(frame) > EXPECTED_VALUES:
                        frame = frame[:EXPECTED_VALUES]
                    elif len(frame) < EXPECTED_VALUES:
                        frame += [0.0] * (EXPECTED_VALUES - len(frame))
                    gesture_window_clean.append(frame)

                if USE_WS:
                    await sequence_queue.put(gesture_window_clean)
                else:
                    send_sequence_to_backend(gesture_window_clean, backend_cfg)

        await asyncio.sleep(0.01)


def send_sequence_to_backend(sequence, backend_cfg):
    """Send full gesture sequence via HTTP POST."""
    payload = {"sensor_values": sequence, "session_id": backend_cfg["session_id"]}
    try:
        response = requests.post(backend_cfg["url"], json=payload, timeout=3.0)
        if response.status_code == 200:
            data = response.json()
            pred = data.get("prediction")
            logger.info(f"Sequence sent via POST. Prediction: {pred}")
        else:
            logger.warning(f"Backend returned {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending sequence to backend: {e}")


async def main():
    cfg = load_config()
    serial_cfg = cfg["serial"]
    backend_cfg = cfg["backend"]

    reader = SerialReader(
        port=serial_cfg["port"],
        baud_rate=serial_cfg["baud_rate"],
        total_sensors=serial_cfg["total_sensors"],
        reconnect_delay=serial_cfg["reconnect_delay"]
    )
    reader.connect()

    detector = MovementDetector(
        threshold=0.05,
        window_size=5,
        min_length=10
    )

    sequence_queue = asyncio.Queue()

    # Start WS sender if enabled
    if USE_WS:
        asyncio.create_task(ws_sender(backend_cfg["ws_url"], sequence_queue, backend_cfg["session_id"]))

    try:
        await read_serial_loop(reader, detector, sequence_queue, backend_cfg)
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    finally:
        reader.close()
        logger.info("Collector closed")

if __name__ == "__main__":
    asyncio.run(main())
