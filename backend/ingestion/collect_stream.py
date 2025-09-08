# collect_stream.py
import serial
import time
import requests
import logging
import numpy as np
from live_data import update_data  # function to update latest reading for FastAPI

# ---------------- CONFIG ----------------
SERIAL_PORT = "COM6"
BAUD_RATE = 115200
BACKEND_URL = "http://127.0.0.1:8000/gesture/live-predict"
TOTAL_SENSORS = 11
SESSION_ID = "demo"

# Flex sensor expected range
FLEX_MIN = 0.0
FLEX_MAX = 2800.0

# IMU ranges
ACC_MIN, ACC_MAX = -2.0, 2.0  # accelerometer g
GYRO_MIN, GYRO_MAX = -250.0, 250.0  # gyro deg/sec

# Throttle interval for sending to backend
SEND_INTERVAL = 1.5  # seconds

# Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("signglove_live")

# ---------------- HELPERS ----------------
def connect_arduino():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        ser.reset_input_buffer()
        logger.info(f"Connected to Arduino on {SERIAL_PORT}")
        return ser
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        return None

def read_sensor_data(ser):
    try:
        line = ser.readline().decode("utf-8").strip()
        if not line:
            return None
        vals = [float(x) for x in line.split(",")]
        if len(vals) != TOTAL_SENSORS:
            return None
        return vals
    except Exception as e:
        logger.error(f"Read error: {e}")
        return None

def normalize_sensor_data(values):
    vals = values.copy()
    # Flex sensors: ESP32 ADC 12-bit (0-4095)
    for i in range(5):
        vals[i] = vals[i] / 4095.0  # to [0,1]
    
    # Accelerometer: raw to g-force (for ±2g)
    for i in range(5, 8):
        vals[i] = vals[i] / 16384.0
    
    # Gyroscope: raw to deg/sec (for ±250°/s)
    for i in range(8, 11):
        vals[i] = vals[i] / 131.0
    
    return vals

def send_to_backend(sensor_values):
    payload = {
        "values": sensor_values,
        "session_id": SESSION_ID
    }
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=2.0)
        if response.status_code == 200:
            data = response.json()
            pred_label = data.get("prediction")
            confidence = data.get("confidence")
            logger.info(f"Prediction: {pred_label} | Confidence: {confidence:.2f}")
        elif response.status_code == 429:
            logger.warning("Backend rate limit exceeded")
        else:
            logger.warning(f"Backend returned {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending data to backend: {e}")

# ---------------- MAIN LOOP ----------------
def main():
    ser = connect_arduino()
    if not ser:
        return

    latest_reading = None
    last_sent_values = None
    last_send_time = 0

    try:
        while True:
            sensor_values = read_sensor_data(ser)
            if sensor_values:
                normalized = normalize_sensor_data(sensor_values)
                update_data(normalized)  # update live reading for FastAPI
                latest_reading = normalized

            # --- Send to backend only if changed AND interval elapsed ---
            now = time.time()
            if latest_reading and (now - last_send_time >= SEND_INTERVAL):
                if last_sent_values != latest_reading:
                    send_to_backend(latest_reading)
                    last_sent_values = latest_reading
                last_send_time = now

            time.sleep(0.01)
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    finally:
        if ser and ser.is_open:
            ser.close()
            logger.info("Serial connection closed.")


if __name__ == "__main__":
    main()
