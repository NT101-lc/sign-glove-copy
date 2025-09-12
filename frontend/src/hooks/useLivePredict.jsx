import { useEffect, useState, useRef, useCallback } from "react";

const useLivePredict = (wsUrl) => {
  const [predictions, setPredictions] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  const send = useCallback(
    (data) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(data));
      }
    },
    []
  );

  useEffect(() => {
    let ws;
    let reconnectTimeout;

    const connect = () => {
      ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        console.log("WS connected");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Ensure proper prediction format
          if (!data.prediction) return;

          // Accept only strings or objects with status
          const p = data.prediction;
          if (typeof p === "string" || (p.status && p.status === "success") || (p.status && p.status === "error")) {
            setPredictions((prev) => [data, ...prev.slice(0, 19)]); // keep last 20
          } else {
            console.warn("Invalid prediction format:", p);
          }
        } catch (err) {
          console.warn("Failed to parse WS message:", event.data, err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.warn("WS disconnected, reconnecting in 2s");
        reconnectTimeout = setTimeout(connect, 2000);
      };

      ws.onerror = (err) => {
        console.error("WS error:", err);
        ws.close();
      };
    };

    connect();

    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (ws) ws.close();
    };
  }, [wsUrl]);

  return { predictions, isConnected, send };
};

export default useLivePredict;
