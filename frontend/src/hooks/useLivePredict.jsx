import { useEffect, useState, useRef, useCallback } from "react";

const useLivePredict = (wsUrl) => {
  const [predictions, setPredictions] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const didConnectRef = useRef(false);
  const incomingBuffer = useRef([]); // buffer for rapid frames
  const animationFrameRef = useRef(null);

  const connect = useCallback(() => {
    if (wsRef.current) return;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected!");
      setIsConnected(true);
      didConnectRef.current = true;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        incomingBuffer.current.push(data);

        // Schedule flush via requestAnimationFrame
        if (!animationFrameRef.current) {
          animationFrameRef.current = requestAnimationFrame(() => {
            setPredictions((prev) => [...prev, ...incomingBuffer.current]);
            incomingBuffer.current = [];
            animationFrameRef.current = null;
          });
        }
      } catch (err) {
        console.error("Failed to parse message:", err);
      }
    };

    ws.onclose = (e) => {
      console.log("WebSocket closed, reconnecting...", e.reason);
      setIsConnected(false);
      wsRef.current = null;

      if (didConnectRef.current) {
        reconnectTimeoutRef.current = setTimeout(connect, 1000);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
      ws.close();
    };
  }, [wsUrl]);

  const send = useCallback((data) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn("WebSocket not open. Cannot send message.");
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);

      const ws = wsRef.current;
      if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
        ws.close();
      }
      wsRef.current = null;
    };
  }, [connect]);

  return { predictions, isConnected, send };
};

export default useLivePredict;
