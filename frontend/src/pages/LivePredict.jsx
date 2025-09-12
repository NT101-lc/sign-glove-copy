import React, { useEffect, useState, useRef } from "react";
import useLivePredict from "../hooks/useLivePredict.jsx";
import useTTS from "../hooks/useTTS.jsx";
import "./styling/LivePredict.css";

const SKIP_GESTURES = ["Rest"];
const MAX_RECENT = 10;

const LivePredict = () => {
  const { predictions, isConnected } = useLivePredict(
    "ws://127.0.0.1:8000/gesture/predict_ws"
  );
  const { speak } = useTTS(2000, 1000);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [recentGestures, setRecentGestures] = useState([]);
  const lastSpokenRef = useRef(null);

  // Auto-speak latest prediction
  useEffect(() => {
    if (!ttsEnabled || predictions.length === 0) return;

    const latest = predictions[0]?.prediction;

    if (
      latest &&
      typeof latest === "string" &&
      latest !== lastSpokenRef.current &&
      !SKIP_GESTURES.includes(latest)
    ) {
      speak(latest);
      lastSpokenRef.current = latest;
    }
  }, [predictions, ttsEnabled, speak]);

  // Keep recent gestures
  useEffect(() => {
    if (predictions.length === 0) return;
    const latest = predictions[0]?.prediction;
    if (latest && typeof latest === "string") {
      setRecentGestures((prev) => {
        const newList = [latest, ...prev];
        return newList.slice(0, MAX_RECENT);
      });
    }
  }, [predictions]);

  const renderPrediction = () => {
    if (predictions.length === 0) return "Waiting for predictions...";
    const p = predictions[0].prediction;
    if (!p) return "No prediction yet";
    if (typeof p === "string") return p;
    if (p.status === "error") return `Error: ${p.message}`;
    if (p.status === "success" && p.prediction) return p.prediction;
    return JSON.stringify(p);
  };

  return (
    <div className="live-container">
      <h2 className="live-title">
        Live Gesture Prediction
        <span
          className="pulse-dot"
          style={{ backgroundColor: isConnected ? "#22c55e" : "#f87171" }}
        />
      </h2>

      <div className="prediction-display">
        <div className="prediction-box">{renderPrediction()}</div>
      </div>

      <div className="recent-gestures">
        <h3>Recent Gestures</h3>
        <ul>
          {recentGestures.map((g, i) => (
            <li key={i}>{g}</li>
          ))}
        </ul>
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
          Sensor: {predictions[0].values.slice(0, 10).join(", ")}
        </div>
      )}
    </div>
  );
};

export default LivePredict;
