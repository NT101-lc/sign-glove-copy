# core/model.py
import os
import logging
import numpy as np
from tensorflow.keras.models import load_model
from core.settings import settings
import pickle

logger = logging.getLogger("signglove")

# ---------------- Load model safely ----------------
model = None
scaler = None
label_encoder = None

# Load Keras H5 model
try:
    if os.path.exists(settings.MODEL_PATH):
        model = load_model(settings.MODEL_PATH)
        logger.info(f"Loaded Keras H5 model from {settings.MODEL_PATH}")
    else:
        logger.warning(f"[Warning] Model file not found at {settings.MODEL_PATH}. Model will not be loaded.")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None

# Load scaler
try:
    if os.path.exists(settings.SCALER_PATH):
        with open(settings.SCALER_PATH, "rb") as f:
            scaler = pickle.load(f)
        logger.info(f"Loaded scaler from {settings.SCALER_PATH}")
    else:
        logger.warning(f"[Warning] Scaler file not found at {settings.SCALER_PATH}.")
except Exception as e:
    logger.error(f"Failed to load scaler: {e}")
    scaler = None

# Load label encoder
try:
    if os.path.exists(settings.ENCODER_PATH):
        with open(settings.ENCODER_PATH, "rb") as f:
            label_encoder = pickle.load(f)
        logger.info(f"Loaded label encoder from {settings.ENCODER_PATH}")
    else:
        logger.warning(f"[Warning] Label encoder file not found at {settings.ENCODER_PATH}.")
except Exception as e:
    logger.error(f"Failed to load label encoder: {e}")
    label_encoder = None

# ---------------- Label map fallback ----------------
LABEL_MAP = {
    0: "Hello",
    1: "Yes",
    2: "No",
    3: "We",
    4: "Are",
    5: "Students",
    6: "Rest"
}

# ---------------- Prediction function ----------------
def predict_gesture(values: list) -> dict:
    """
    Predict gesture from single-hand sensor data using the preloaded model.

    Args:
        values (list): List of sensor values (expected 11 for single-hand)

    Returns:
        dict: {"status": "success"/"error", "prediction": str, "confidence": float}
    """
    try:
        if model is None:
            return {"status": "error", "message": "Model not loaded"}

        if len(values) != 11:
            return {"status": "error", "message": "Invalid input (expected 11 values)"}

        # Convert to numpy array
        input_data = np.array([values], dtype=np.float32)

        # Apply scaler if available
        if scaler:
            input_data = scaler.transform(input_data)

        # Predict
        output = model.predict(input_data)  # shape (1, num_classes)
        predicted_index = int(np.argmax(output))
        confidence = float(np.max(output))

        # Map label
        if label_encoder:
            predicted_label = label_encoder.inverse_transform([predicted_index])[0]
        else:
            predicted_label = LABEL_MAP.get(predicted_index, str(predicted_index))

        return {
            "status": "success",
            "prediction": predicted_label,
            "confidence": confidence
        }

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"status": "error", "message": f"Prediction failed: {str(e)}"}
