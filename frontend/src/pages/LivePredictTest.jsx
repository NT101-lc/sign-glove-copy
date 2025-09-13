// LivePredictTest.jsx
import React, { useEffect } from "react";
import useLivePredict from "../hooks/useLivePredict.jsx";

const generateDummyFrame = () => {
  // 11 random float values per frame
  return Array.from({ length: 11 }, () => parseFloat((Math.random() * 10).toFixed(2)));
};

const LivePredictTest = () => {
  const { predictions, isConnected, send } = useLivePredict(
    "ws://127.0.0.1:8000/gesture/predict_ws"
  );

  useEffect(() => {
    if (!isConnected) return;

    // send dummy frames every second
    const interval = setInterval(() => {
      const frame = generateDummyFrame();
      send({ sensor_values: [frame], session_id: "test_session" });
      console.log("Sent dummy frame:", frame);
    }, 1000);

    return () => clearInterval(interval);
  }, [isConnected, send]);

  return (
    <div>
      <h1>{isConnected ? "WS Connected" : "Disconnected"}</h1>
      <h2>Last Predictions:</h2>
      <ul>
        {predictions.map((p, i) => (
          <li key={i}>
            {p.session_id}: {p.prediction || "None"} | Values: [{p.values.join(", ")}]
          </li>
        ))}
      </ul>
    </div>
  );
};

export default LivePredictTest;
