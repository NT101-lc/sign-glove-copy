# gesture_model_inference.py
import numpy as np
import pickle
from tensorflow.keras.models import load_model
from collections import deque
from scipy.stats import mode
import os

# ==================== SETTINGS ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))  # Move to backend/
RESULTS_DIR = os.path.join(BACKEND_DIR, "results")
MODEL_DIR = os.path.join(RESULTS_DIR, "models")

# Paths
MODEL_PATH = os.path.join(MODEL_DIR, "gesture_model_fold1.h5")  # default first fold
SCALER_PATH = os.path.join(RESULTS_DIR, "scaler.pkl")
ENCODER_PATH = os.path.join(RESULTS_DIR, "label_encoder.pkl")

TIMESTEPS = 50   # must match training
ROLLING_WINDOW = 5   # number of recent predictions to smooth
SKIP_GESTURES = ["Rest"]   # gestures to ignore

# ==================== LOAD MODEL & PREPROCESSORS ====================
# Load model only if the file exists
if os.path.exists(MODEL_PATH):
    model = load_model(MODEL_PATH)
else:
    print(f"[Warning] Model file not found at {MODEL_PATH}. Model will not be loaded.")
    model = None

# Load scaler
if os.path.exists(SCALER_PATH):
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
else:
    print(f"[Warning] Scaler file not found at {SCALER_PATH}.")
    scaler = None

# Load label encoder
if os.path.exists(ENCODER_PATH):
    with open(ENCODER_PATH, "rb") as f:
        label_encoder = pickle.load(f)
else:
    print(f"[Warning] Label encoder file not found at {ENCODER_PATH}.")
    label_encoder = None

# ==================== BUFFERS ====================
sequence_buffer = []  # stores recent frames for LSTM input
prediction_buffer = deque(maxlen=ROLLING_WINDOW)  # stores recent predictions for smoothing

# ==================== PREPROCESS FRAME ====================
def preprocess_frame(frame):
    """
    Add new sensor frame to the buffer and prepare input for prediction.
    frame: 1D numpy array of shape (NUM_FEATURES,)
    Returns: input tensor of shape (1, TIMESTEPS, NUM_FEATURES) or None if buffer not full
    """
    if scaler is None:
        raise ValueError("Scaler not loaded. Cannot preprocess frame.")

    global sequence_buffer
    frame_scaled = scaler.transform(frame.reshape(1, -1))
    sequence_buffer.append(frame_scaled[0])

    if len(sequence_buffer) > TIMESTEPS:
        sequence_buffer.pop(0)

    if len(sequence_buffer) == TIMESTEPS:
        X_input = np.array(sequence_buffer).reshape(1, TIMESTEPS, frame.shape[0])
        return X_input
    return None

# ==================== PREDICTION WITH SMOOTHING ====================
def predict_gesture(X_input):
    """
    Predict gesture from input tensor and apply rolling window smoothing.
    Returns gesture label as string or None if skipped.
    """
    if model is None or label_encoder is None:
        raise ValueError("Model or label encoder not loaded. Cannot predict gesture.")

    pred_proba = model.predict(X_input)
    pred_class = np.argmax(pred_proba, axis=1)[0]
    prediction_buffer.append(pred_class)

    # Apply mode over rolling window
    smoothed_class = mode(list(prediction_buffer))[0][0]
    gesture_name = label_encoder.inverse_transform([smoothed_class])[0]

    if gesture_name in SKIP_GESTURES:
        return None
    return gesture_name

# ==================== RESET BUFFERS ====================
def reset_buffers():
    global sequence_buffer, prediction_buffer
    sequence_buffer = []
    prediction_buffer.clear()
