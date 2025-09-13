import React, { useEffect, useState, useRef } from "react";
import useLivePredict from "../hooks/useLivePredict.jsx";
import useTTS from "../hooks/useTTS.jsx";
import "./styling/LivePredict.css";

const SKIP_GESTURES = ["Rest"];
const MAX_RECENT = 5;

const LivePredict = () => {
  const { predictions, isConnected } = useLivePredict(
    "ws://127.0.0.1:8000/gesture/predict_ws"
  );
  const { speak } = useTTS(2000, 1000); // cooldown 2s, queue 1s
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [recentGestures, setRecentGestures] = useState([]);
  const incomingBufferRef = useRef([]);

  // Buffer incoming predictions to prevent UI flicker
  useEffect(() => {
    if (predictions.length === 0) return;
    incomingBufferRef.current.push(predictions[predictions.length - 1]);
  }, [predictions]);

  // Flush buffer every animation frame
  useEffect(() => {
    let animationFrame;

    const flushBuffer = () => {
      if (incomingBufferRef.current.length > 0) {
        const latest = incomingBufferRef.current.shift();

        // Update recent gestures
        if (latest?.prediction && !SKIP_GESTURES.includes(latest.prediction)) {
          setRecentGestures((prev) => {
            const newList = [...prev, latest.prediction];
            return newList.slice(-MAX_RECENT);
          });

          // Trigger TTS for every meaningful gesture
          if (ttsEnabled) {
            speak(latest.prediction);
          }
        }
      }
      animationFrame = requestAnimationFrame(flushBuffer);
    };

    animationFrame = requestAnimationFrame(flushBuffer);

    return () => cancelAnimationFrame(animationFrame);
  }, [ttsEnabled, speak]);

  const renderPrediction = () => {
    if (incomingBufferRef.current.length === 0 && predictions.length === 0)
      return "Waiting for predictions...";

    const latest =
      incomingBufferRef.current[incomingBufferRef.current.length - 1] ||
      predictions[predictions.length - 1];

    if (!latest) return "No prediction yet";
    if (typeof latest.prediction === "string") return latest.prediction;
    if (latest.prediction?.status === "error")
      return `Error: ${latest.prediction.message}`;
    if (latest.prediction?.status === "success" && latest.prediction.prediction)
      return latest.prediction.prediction;
    return JSON.stringify(latest.prediction);
  };

  const latestValues =
    (incomingBufferRef.current[incomingBufferRef.current.length - 1]?.values ||
      predictions[predictions.length - 1]?.values ||
      []).slice(0, 10);

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

      {latestValues.length > 0 && (
        <div className="sensor-preview">
          Sensor: {latestValues.join(", ")}
        </div>
      )}
    </div>
  );
};

export default LivePredict;
