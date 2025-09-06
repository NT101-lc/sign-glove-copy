import React, { useState, useRef, useEffect, useCallback } from "react";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const WS_URL = "ws://localhost:8000/ws/stream";

const LivePredict = () => {
  const [prediction, setPrediction] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [connected, setConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [isTtsSupported, setIsTtsSupported] = useState(false);
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [testText, setTestText] = useState("Hello, this is a test");
  const [predictionHistory, setPredictionHistory] = useState([]);

  const wsRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimeout = useRef(null);

  const ttsQueue = useRef([]);
  const utteranceRef = useRef(null);
  const lastSpokenPrediction = useRef(null);
  const resetTimeout = useRef(null);
  const lastTtsTime = useRef(0);

  // --- TTS Support ---
  useEffect(() => {
    const supported = "speechSynthesis" in window;
    setIsTtsSupported(supported);
    
    if (supported) {
      // Load voices
      const loadVoices = () => {
        const availableVoices = window.speechSynthesis.getVoices();
        setVoices(availableVoices);
        if (availableVoices.length > 0 && !selectedVoice) {
          setSelectedVoice(availableVoices[0]);
        }
      };
      
      loadVoices();
      
      // Some browsers load voices asynchronously
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = loadVoices;
      }
    }
  }, [selectedVoice]);

  const speakNextInQueue = useCallback(() => {
    if (!ttsEnabled || ttsQueue.current.length === 0) return;

    const text = ttsQueue.current.shift();
    if (!text) return;

    // Cancel any current speech
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      // Wait a bit for cancellation to complete
      setTimeout(() => {
        if (ttsQueue.current.length > 0) {
          speakNextInQueue();
        }
      }, 100);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 0.8; // Slightly slower for better clarity
    utterance.volume = 1.0;
    utterance.pitch = 1.0;
    
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }

    utterance.onstart = () => {
      console.log("TTS started:", text);
    };

    utterance.onend = () => {
      console.log("TTS ended:", text);
      // Wait a bit before next utterance
      setTimeout(() => {
        if (ttsQueue.current.length > 0) {
          speakNextInQueue();
        }
      }, 500);
    };

    utterance.onerror = (event) => {
      console.error("TTS error:", event.error, "for text:", text);
      // Continue with next in queue even if there's an error
      setTimeout(() => {
        if (ttsQueue.current.length > 0) {
          speakNextInQueue();
        }
      }, 500);
    };

    utteranceRef.current = utterance;
    console.log("Speaking:", text);
    window.speechSynthesis.speak(utterance);
  }, [ttsEnabled]);

  const enqueuePrediction = useCallback(
    (text) => {
      if (!text) return;
      const now = Date.now();

      // Don't repeat the same prediction
      if (text === lastSpokenPrediction.current) return;
      
      // Longer debounce time to prevent interruptions
      if (now - lastTtsTime.current < 2000) return;

      // Clear queue if it gets too long
      if (ttsQueue.current.length > 3) {
        ttsQueue.current = [];
      }

      lastSpokenPrediction.current = text;
      lastTtsTime.current = now;
      ttsQueue.current.push(text);
      
      // Only start speaking if not already speaking
      if (!window.speechSynthesis.speaking) {
        speakNextInQueue();
      }
    },
    [speakNextInQueue]
  );

  const enableTTS = useCallback(() => {
    if (!isTtsSupported) return toast.error("Browser does not support TTS");
    setTtsEnabled((prev) => !prev);
    toast.info(!ttsEnabled ? "TTS Enabled" : "TTS Disabled");
  }, [isTtsSupported, ttsEnabled]);

  // --- TTS Test Functions ---
  const testBasicTTS = useCallback(() => {
    if (!isTtsSupported) {
      toast.error("Browser does not support TTS");
      return;
    }

    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
    }

    const utterance = new SpeechSynthesisUtterance("Hello, this is a basic test");
    utterance.lang = "en-US";
    utterance.rate = 0.8;
    utterance.volume = 1.0;
    utterance.pitch = 1.0;

    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }

    utterance.onstart = () => toast.info("Speaking...");
    utterance.onend = () => toast.success("TTS test completed");
    utterance.onerror = (event) => toast.error(`TTS Error: ${event.error}`);

    window.speechSynthesis.speak(utterance);
  }, [isTtsSupported, selectedVoice]);

  const testPredictionWords = useCallback(() => {
    if (!isTtsSupported) {
      toast.error("Browser does not support TTS");
      return;
    }

    const words = ["Hello", "Yes", "No", "We", "Are", "Students", "Rest"];
    const randomWord = words[Math.floor(Math.random() * words.length)];
    
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
    }

    const utterance = new SpeechSynthesisUtterance(randomWord);
    utterance.lang = "en-US";
    utterance.rate = 0.8;
    utterance.volume = 1.0;
    utterance.pitch = 1.0;

    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }

    utterance.onstart = () => toast.info(`Speaking: ${randomWord}`);
    utterance.onend = () => toast.success("Prediction word test completed");
    utterance.onerror = (event) => toast.error(`TTS Error: ${event.error}`);

    window.speechSynthesis.speak(utterance);
  }, [isTtsSupported, selectedVoice]);

  const testCustomText = useCallback(() => {
    if (!isTtsSupported) {
      toast.error("Browser does not support TTS");
      return;
    }

    if (!testText.trim()) {
      toast.error("Please enter some text to speak");
      return;
    }

    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
    }

    const utterance = new SpeechSynthesisUtterance(testText);
    utterance.lang = "en-US";
    utterance.rate = 0.8;
    utterance.volume = 1.0;
    utterance.pitch = 1.0;

    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }

    utterance.onstart = () => toast.info("Speaking custom text...");
    utterance.onend = () => toast.success("Custom text test completed");
    utterance.onerror = (event) => toast.error(`TTS Error: ${event.error}`);

    window.speechSynthesis.speak(utterance);
  }, [isTtsSupported, selectedVoice, testText]);

  // --- WebSocket connection with auto-reconnect ---
  const connectWebSocket = useCallback(() => {
    if (isConnecting) return;

    setIsConnecting(true);
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("Connected to WebSocket:", WS_URL);
      setConnected(true);
      setIsConnecting(false);
      reconnectAttempts.current = 0; // reset attempts
      toast.success("Connected to live predictions!");
    };

    ws.onmessage = (event) => {
      console.log("WebSocket message received:", event.data);
      try {
        const data = JSON.parse(event.data);
        console.log("Parsed data:", data);
        
        if (data.prediction) {
          console.log("Setting prediction:", data.prediction);
          setPrediction(data.prediction);
          setConfidence(data.confidence || null);
          
          // Add to prediction history
          const newPrediction = {
            word: data.prediction,
            confidence: data.confidence || 0,
            timestamp: new Date().toLocaleTimeString()
          };
          setPredictionHistory(prev => [newPrediction, ...prev.slice(0, 9)]); // Keep last 10
          
          if (ttsEnabled) enqueuePrediction(data.prediction);
        } else {
          console.log("No prediction in data:", data);
        }

        clearTimeout(resetTimeout.current);
        resetTimeout.current = setTimeout(() => {
          lastSpokenPrediction.current = null;
        }, 2000);
      } catch (err) {
        console.error("WebSocket parse error:", err, "Raw:", event.data);
      }
    };

    const handleCloseOrError = (reason) => {
      console.warn("WebSocket closed/error:", reason);
      setConnected(false);
      setIsConnecting(false);

      // Exponential backoff for reconnect
      const attempt = reconnectAttempts.current++;
      const delay = Math.min(1000 * 2 ** attempt, 30000); // cap at 30s
      console.log(`Reconnecting in ${delay / 1000}s (attempt ${attempt + 1})...`);

      reconnectTimeout.current = setTimeout(() => {
        connectWebSocket();
      }, delay);
    };

    ws.onclose = () => handleCloseOrError("closed");
    ws.onerror = () => handleCloseOrError("error");
  }, [isConnecting, ttsEnabled, enqueuePrediction]);

  const resetPrediction = useCallback(() => {
    setPrediction(null);
    setConfidence(null);
    lastSpokenPrediction.current = null;
  }, []);

  // --- Cleanup ---
  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel();
      if (wsRef.current) wsRef.current.close();
      clearTimeout(resetTimeout.current);
      clearTimeout(reconnectTimeout.current);
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Live Gesture Prediction</h1>
          <p className="text-lg text-gray-600">Real-time sign language recognition with TTS</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Prediction Panel */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Live Predictions</h2>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="text-sm font-medium text-gray-600">
                    {connected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>

              {/* Connection Controls */}
              <div className="flex flex-wrap gap-3 mb-6">
                <button
                  onClick={connectWebSocket}
                  disabled={connected || isConnecting}
                  className={`px-6 py-3 rounded-xl font-semibold transition-all duration-200 ${
                    connected
                      ? "bg-green-500 text-white cursor-not-allowed"
                      : isConnecting
                      ? "bg-yellow-400 text-white cursor-wait"
                      : "bg-blue-500 text-white hover:bg-blue-600 hover:shadow-lg"
                  }`}
                >
                  {connected ? "✅ Connected" : isConnecting ? "⏳ Connecting..." : "🔌 Connect"}
                </button>

                <button
                  onClick={enableTTS}
                  disabled={!isTtsSupported}
                  className={`px-6 py-3 rounded-xl font-semibold transition-all duration-200 ${
                    ttsEnabled 
                      ? "bg-purple-500 text-white hover:bg-purple-600" 
                      : "bg-gray-300 text-gray-700 cursor-not-allowed"
                  }`}
                >
                  {ttsEnabled ? "🔊 TTS Enabled" : "🔇 TTS Disabled"}
                </button>

                <button
                  onClick={() => prediction && enqueuePrediction(prediction)}
                  disabled={!prediction || !ttsEnabled}
                  className="px-6 py-3 rounded-xl font-semibold bg-indigo-500 text-white hover:bg-indigo-600 hover:shadow-lg transition-all duration-200 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  🎤 Speak Now
                </button>

                <button
                  onClick={resetPrediction}
                  disabled={!prediction}
                  className="px-6 py-3 rounded-xl font-semibold bg-red-500 text-white hover:bg-red-600 hover:shadow-lg transition-all duration-200 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  🔄 Reset
                </button>
              </div>

              {/* Current Prediction Display */}
              {prediction ? (
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-8 text-center text-white mb-6">
                  <div className="text-6xl font-bold mb-4">{prediction}</div>
                  {confidence !== null && (
                    <div className="w-full bg-white/20 rounded-full h-4 mb-4">
                      <div
                        className="bg-white h-4 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(confidence * 100, 100)}%` }}
                      ></div>
                    </div>
                  )}
                  <div className="text-xl opacity-90">
                    Confidence: {confidence ? `${(confidence * 100).toFixed(1)}%` : 'N/A'}
                  </div>
                </div>
              ) : (
                <div className="bg-gray-100 rounded-2xl p-8 text-center">
                  <div className="text-6xl mb-4">🤖</div>
                  <p className="text-xl text-gray-600">Waiting for live predictions...</p>
                </div>
              )}

              {/* TTS Queue */}
              <div className="bg-gray-50 rounded-xl p-4">
                <h4 className="text-lg font-semibold text-gray-700 mb-3">TTS Queue</h4>
                {ttsQueue.current.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No pending predictions</p>
                ) : (
                  <div className="space-y-2">
                    {ttsQueue.current.map((item, index) => (
                      <div
                        key={index}
                        className="bg-blue-100 px-4 py-2 rounded-lg text-blue-800 font-medium"
                      >
                        {item}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* TTS Test Panel */}
          <div className="space-y-6">
            {/* TTS Status */}
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">TTS Status</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">TTS Support:</span>
                  <span className={`font-semibold ${isTtsSupported ? 'text-green-600' : 'text-red-600'}`}>
                    {isTtsSupported ? '✅ Supported' : '❌ Not Supported'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Available Voices:</span>
                  <span className="font-semibold text-blue-600">{voices.length}</span>
                </div>
              </div>
            </div>

            {/* Voice Selection */}
            {isTtsSupported && voices.length > 0 && (
              <div className="bg-white rounded-2xl shadow-xl p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Voice Settings</h3>
                <select
                  value={selectedVoice?.name || ''}
                  onChange={(e) => {
                    const voice = voices.find(v => v.name === e.target.value);
                    setSelectedVoice(voice);
                  }}
                  className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {voices.map((voice, index) => (
                    <option key={index} value={voice.name}>
                      {voice.name} ({voice.lang})
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* TTS Test Controls */}
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">TTS Testing</h3>
              <div className="space-y-3">
                <button
                  onClick={testBasicTTS}
                  disabled={!isTtsSupported}
                  className="w-full px-4 py-3 bg-blue-500 text-white rounded-xl font-semibold hover:bg-blue-600 transition-all duration-200 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  🎵 Test Basic TTS
                </button>
                
                <button
                  onClick={testPredictionWords}
                  disabled={!isTtsSupported}
                  className="w-full px-4 py-3 bg-green-500 text-white rounded-xl font-semibold hover:bg-green-600 transition-all duration-200 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  🎯 Test Prediction Words
                </button>

                <div className="space-y-2">
                  <input
                    type="text"
                    value={testText}
                    onChange={(e) => setTestText(e.target.value)}
                    placeholder="Enter text to speak..."
                    className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                  <button
                    onClick={testCustomText}
                    disabled={!isTtsSupported}
                    className="w-full px-4 py-3 bg-purple-500 text-white rounded-xl font-semibold hover:bg-purple-600 transition-all duration-200 disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    🎤 Speak Custom Text
                  </button>
                </div>
              </div>
            </div>

            {/* Prediction History */}
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Recent Predictions</h3>
              {predictionHistory.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No predictions yet</p>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {predictionHistory.map((pred, index) => (
                    <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                      <div className="flex items-center gap-3">
                        <span className="text-lg font-bold text-blue-600">{pred.word}</span>
                        <span className="text-sm text-gray-500">({(pred.confidence * 100).toFixed(0)}%)</span>
                      </div>
                      <span className="text-xs text-gray-400">{pred.timestamp}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LivePredict;
