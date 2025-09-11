import React from "react";
import useLivePredict from "../hooks/useLivePredict";


const LivePredictDisplay = () => {
  const { predictions, isConnected, isReady } = useLivePredict(
    "ws://localhost:8000/gesture/stream"
  );

  return (
    <div style={{ padding: "1rem", fontFamily: "sans-serif" }}>
      <h2>Live Predictions</h2>
      <p>
        WebSocket Status:{" "}
        <strong>
          {isConnected ? (isReady ? "Ready" : "Connecting...") : "Disconnected"}
        </strong>
      </p>

      {isReady ? (
        <ul>
          {predictions.map((pred, idx) => (
            <li key={idx}>
              {typeof pred === "object" ? JSON.stringify(pred) : pred}
            </li>
          ))}
        </ul>
      ) : (
        <p>Waiting for data...</p>
      )}
    </div>
  );
};

export default LivePredictDisplay;
