import { useState, useEffect, useRef } from "react";

const useLivePredict = (url) => {
  const [predictions, setPredictions] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeout = useRef(null);
  const lastSpokenRef = useRef(0);

  useEffect(() => {
    let mounted = true;

    const connect = () => {
      if (!mounted) return;

      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log("WS connected");
        setIsConnected(true);
      };

      wsRef.current.onmessage = (event) => {
  console.log(" Raw WS message:", event.data); // <--- ADD THIS

  try {
    const data = JSON.parse(event.data);
    setPredictions((prev) => [data, ...prev].slice(0, 10));

    // Optional: TTS debounce
    const now = Date.now();
    if (data.gesture && now - lastSpokenRef.current > 1000) {
      lastSpokenRef.current = now;
      speechSynthesis.cancel();
      speechSynthesis.speak(new SpeechSynthesisUtterance(data.gesture));
    }
  } catch (err) {
    console.error(" Invalid WS message:", err, event.data); // include raw
  }
};

      wsRef.current.onclose = () => {
        console.log("WS closed");
        setIsConnected(false);
        if (mounted) reconnectTimeout.current = setTimeout(connect, 2000);
      };

      wsRef.current.onerror = (err) => {
        console.error("WS error:", err);
        wsRef.current.close();
      };
    };

    connect();

    return () => {
      mounted = false;
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
    };
  }, [url]);

  return { predictions, isConnected };
};

export default useLivePredict;
