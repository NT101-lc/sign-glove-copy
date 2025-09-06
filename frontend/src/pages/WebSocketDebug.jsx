import React, { useState, useRef, useEffect } from "react";
import { toast } from "react-toastify";

const WS_URL = "ws://localhost:8000/ws/stream";

const WebSocketDebug = () => {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isConnecting, setIsConnecting] = useState(false);
  const wsRef = useRef(null);

  const connectWebSocket = () => {
    if (isConnecting) return;

    setIsConnecting(true);
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected:", WS_URL);
      setConnected(true);
      setIsConnecting(false);
      toast.success("Connected to WebSocket!");
      addMessage("✅ Connected to WebSocket");
    };

    ws.onmessage = (event) => {
      console.log("WebSocket message received:", event.data);
      try {
        const data = JSON.parse(event.data);
        addMessage(`📥 Received: ${JSON.stringify(data, null, 2)}`);
        
        if (data.prediction) {
          addMessage(`🎯 Prediction: ${data.prediction} (confidence: ${data.confidence})`);
        }
      } catch (err) {
        console.error("WebSocket parse error:", err);
        addMessage(`❌ Parse error: ${err.message}`);
      }
    };

    ws.onclose = () => {
      console.log("WebSocket closed");
      setConnected(false);
      setIsConnecting(false);
      addMessage("❌ WebSocket closed");
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setConnected(false);
      setIsConnecting(false);
      addMessage(`❌ WebSocket error: ${error}`);
    };
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
    addMessage("🔌 Disconnected from WebSocket");
  };

  const addMessage = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    setMessages(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const clearMessages = () => {
    setMessages([]);
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <div className="max-w-4xl mx-auto mt-10 p-6 bg-white rounded-xl shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-blue-600">WebSocket Debug</h2>
      
      <div className="flex gap-3 mb-6">
        <button
          onClick={connectWebSocket}
          disabled={connected || isConnecting}
          className={`px-4 py-2 rounded ${
            connected
              ? "bg-green-500 text-white cursor-not-allowed"
              : isConnecting
              ? "bg-yellow-400 text-white cursor-wait"
              : "bg-blue-500 text-white hover:bg-blue-600"
          }`}
        >
          {connected ? "Connected" : isConnecting ? "Connecting..." : "Connect"}
        </button>

        <button
          onClick={disconnectWebSocket}
          disabled={!connected}
          className="px-4 py-2 rounded bg-red-500 text-white hover:bg-red-600 disabled:bg-gray-300"
        >
          Disconnect
        </button>

        <button
          onClick={clearMessages}
          className="px-4 py-2 rounded bg-gray-500 text-white hover:bg-gray-600"
        >
          Clear Messages
        </button>
      </div>

      <div className="bg-gray-100 rounded-lg p-4 h-96 overflow-y-auto">
        <h3 className="text-lg font-semibold mb-3">WebSocket Messages:</h3>
        {messages.length === 0 ? (
          <p className="text-gray-500">No messages yet. Click Connect to start debugging.</p>
        ) : (
          <div className="space-y-2">
            {messages.map((message, index) => (
              <div key={index} className="text-sm font-mono bg-white p-2 rounded border">
                {message}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">Instructions:</h3>
        <ol className="text-sm text-gray-700 space-y-1">
          <li>1. Click "Connect" to connect to WebSocket</li>
          <li>2. Run the backend test: <code>python test_tts_slow.py</code></li>
          <li>3. Watch for messages appearing here</li>
          <li>4. Check browser console (F12) for any errors</li>
        </ol>
      </div>
    </div>
  );
};

export default WebSocketDebug;
