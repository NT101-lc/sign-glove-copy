import React, { useEffect, useState, useRef } from "react";
import useLivePredict from "../hooks/useLivePredict.jsx";
import useTTS from "../hooks/useTTS.jsx";
import "./styling/LivePredict.css";

const SKIP_GESTURES = ["Rest"];

const LivePredict = () => {
  const { predictions, isConnected } = useLivePredict("ws://127.0.0.1:8000/gesture/predict_ws");
  const { speak } = useTTS(2000, 1000); // 2s debounce, 1s spacing
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const lastSpokenRef = useRef(null);

  // Auto-speak latest prediction if TTS is enabled
  useEffect(() => {
    if (!ttsEnabled || predictions.length === 0) return;

    const latest = predictions[0].prediction;
    if (latest && latest !== lastSpokenRef.current && !SKIP_GESTURES.includes(latest)) {
      speak(latest);
      lastSpokenRef.current = latest;
    }
  }, [predictions, ttsEnabled, speak]);

  return (
    <div className="live-container">
      <h2 className="live-title">
        Live Gesture Prediction
        <span
          className="pulse-dot"
          style={{ backgroundColor: isConnected ? "#22c55e" : "#f87171" }}
        ></span>
      </h2>

      <div className="prediction-display">
        {predictions.length === 0 ? (
          <div className="loading-text">Waiting for predictions...</div>
        ) : (
          <div className="prediction-box">{predictions[0].prediction}</div>
        )}
      </div>

      <div className="controls">
        <div className="status-text">
          Status: {isConnected ? "Connected" : "Disconnected"}
        </div>
        <div className="button-group">
          <button onClick={() => setTtsEnabled(!ttsEnabled)}>
            {ttsEnabled ? "Disable TTS" : "Enable TTS"}
          </button>
        </div>
      </div>

      {predictions.length > 0 && predictions[0].values && (
        <div className="sensor-preview">
          Sensor: {predictions[0].values.slice(0, 10).join(", ")} {/* show first 10 values */}
        </div>
      )}
    </div>
  );
};

export default LivePredict;
