import WebSocket, { WebSocketServer } from "ws";

const wss = new WebSocketServer({ port: 8000, path: "/gesture/stream" });

console.log("Mock WS server running on ws://localhost:8000/gesture/stream");

wss.on("connection", (ws) => {
  console.log("Client connected!");

  // send a fake prediction every second
  const interval = setInterval(() => {
    const fakePrediction = {
      gesture: ["Fist", "Open", "Point", "Rest"][
        Math.floor(Math.random() * 4)
      ],
      confidence: Math.random().toFixed(2),
      timestamp: Date.now(),
    };
    ws.send(JSON.stringify(fakePrediction));
  }, 1000);

  ws.on("close", () => {
    console.log("Client disconnected");
    clearInterval(interval);
  });
});
