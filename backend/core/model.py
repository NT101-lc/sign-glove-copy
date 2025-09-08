# core/model.py

import numpy as np
import tensorflow as tf
import os
import logging
from core.settings import settings

# Initialize logger
logger = logging.getLogger("signglove")

# ---------------- Load TFLite model once ----------------
if not os.path.exists(settings.MODEL_PATH):
    logger.error(f"TFLite model not found at {settings.MODEL_PATH}")
    interpreter = None
else:
    interpreter = tf.lite.Interpreter(model_path=settings.MODEL_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    logger.info(f"Loaded TFLite model from {settings.MODEL_PATH}")

# ---------------- Label map ----------------
LABEL_MAP = {
    0: "Hello",
    1: "Yes",
    2: "No",
    3: "We",
    4: "Are",
    5: "Students",
    6: "Rest"
}

# ---------------- Prediction ----------------
def predict_gesture(values: list) -> dict:
    """
    Predicts gesture from single hand sensor data using a preloaded TFLite model.
    Args:
        values (list): List of 11 sensor values.
    Returns:
        dict: Prediction result with status, prediction, and confidence.
    """
    try:
        if interpreter is None:
            return {"status": "error", "message": "Model not loaded"}

        if len(values) != 11:
            return {"status": "error", "message": "Invalid input (expected 11 values)"}

        # Prepare input data
        input_data = np.array([values], dtype=np.float32)

        # Run inference
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])

        # Process output
        predicted_index = int(np.argmax(output))
        confidence = float(np.max(output))
        label = LABEL_MAP.get(predicted_index, f"Class {predicted_index}")

        return {
            "status": "success",
            "prediction": label,
            "confidence": confidence
        }

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"status": "error", "message": f"Prediction failed: {str(e)}"}
