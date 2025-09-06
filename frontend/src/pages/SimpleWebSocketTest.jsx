import React, { useState, useRef, useEffect } from "react";

const SimpleWebSocketTest = () => {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isConnecting, setIsConnecting] = useState(false);
  const wsRef = useRef(null);

  const connectWebSocket = () => {
    if (isConnecting) return;

    setIsConnecting(true);
    const ws = new WebSocket("ws://localhost:8000/ws/stream");
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("✅ WebSocket connected!");
      setConnected(true);
      setIsConnecting(false);
      addMessage("✅ Connected to WebSocket");
    };

    ws.onmessage = (event) => {
      console.log("📥 Message received:", event.data);
      addMessage(`📥 Received: ${event.data}`);
    };

    ws.onclose = () => {
      console.log("❌ WebSocket closed");
      setConnected(false);
      setIsConnecting(false);
      addMessage("❌ WebSocket closed");
    };

    ws.onerror = (error) => {
      console.error("❌ WebSocket error:", error);
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
    addMessage("🔌 Disconnected");
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
    <div className="max-w-2xl mx-auto mt-10 p-6 bg-white rounded-xl shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-blue-600">Simple WebSocket Test</h2>
      
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
          Clear
        </button>
      </div>

      <div className="bg-gray-100 rounded-lg p-4 h-64 overflow-y-auto">
        <h3 className="text-lg font-semibold mb-3">Messages:</h3>
        {messages.length === 0 ? (
          <p className="text-gray-500">No messages yet. Click Connect to start.</p>
        ) : (
          <div className="space-y-1">
            {messages.map((message, index) => (
              <div key={index} className="text-sm font-mono bg-white p-2 rounded border">
                {message}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">Instructions:</h3>
        <ol className="text-sm text-gray-700 space-y-1">
          <li>1. Click "Connect" above</li>
          <li>2. Check if you see "Connected" message</li>
          <li>3. Open browser console (F12) and look for any errors</li>
          <li>4. Run backend test: <code>python test_tts_slow.py</code></li>
          <li>5. Watch for messages appearing here</li>
        </ol>
      </div>
    </div>
  );
};

export default SimpleWebSocketTest;
