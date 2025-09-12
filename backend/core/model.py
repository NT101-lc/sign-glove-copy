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

try:
    if os.path.exists(settings.MODEL_PATH):
        model = load_model(settings.MODEL_PATH)
        logger.info(f"Loaded Keras H5 model from {settings.MODEL_PATH}")
    else:
        logger.warning(f"[Warning] Model file not found at {settings.MODEL_PATH}. Model will not be loaded.")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None

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

# ---------------- Prediction function ----------------
def predict_gesture(sequence: list) -> dict:
    """
    Predict gesture from a sequence of frames.
    Args:
        sequence (list of lists): [[f1,...,f11], [f1,...,f11], ...]
    Returns:
        dict: {"status": "success"/"error", "prediction": str, "confidence": float}
    """
    try:
        if model is None:
            return {"status": "error", "message": "Model not loaded"}

        # Convert sequence to numpy array
        seq_array = np.array(sequence, dtype=np.float32)  # shape: (frames, 11)

        # Validate shape
        if seq_array.ndim != 2 or seq_array.shape[1] != 11:
            return {"status": "error", "message": f"Invalid input shape {seq_array.shape}, expected (frames, 11)"}

        # Apply scaler if available (2D)
        if scaler:
            seq_array = scaler.transform(seq_array)

        # Reshape to 3D for model (1, frames, 11)
        seq_input = seq_array[np.newaxis, :, :]

        # Predict
        output = model.predict(seq_input)  # shape: (1, num_classes)
        predicted_index = int(np.argmax(output))
        confidence = float(np.max(output))

        # Map label
        if label_encoder:
            predicted_label = label_encoder.inverse_transform([predicted_index])[0]
        else:
            predicted_label = str(predicted_index)

        return {"status": "success", "prediction": predicted_label, "confidence": confidence}

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"status": "error", "message": f"Prediction failed: {str(e)}"}
