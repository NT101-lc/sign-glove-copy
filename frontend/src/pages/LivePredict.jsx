// src/pages/LivePredict.jsx
import React, { useState, useEffect, useRef, useCallback } from "react";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";

const LATEST_SENSOR_URL = "http://localhost:8000/gesture/latest";
const SKIP_GESTURES = ["Rest"];
const FETCH_INTERVAL = 15000; // poll every 2s
const TTS_DEBOUNCE = 10000;   // 6s debounce
const TTS_SPACING = 2000;    // 1s between speeches

const LivePredict = ({ user }) => {
  const [prediction, setPrediction] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [status, setStatus] = useState("Connecting...");
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [isTtsSupported, setIsTtsSupported] = useState(false);
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [loading, setLoading] = useState(true);

  const ttsQueue = useRef([]);
  const utteranceRef = useRef(null);
  const lastSpokenPrediction = useRef(null);
  const lastTtsTime = useRef(0);

  // --- TTS setup ---
  useEffect(() => {
    const supported = "speechSynthesis" in window;
    setIsTtsSupported(supported);
    if (!supported) return;

    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);
      if (availableVoices.length > 0 && !selectedVoice) {
        setSelectedVoice(availableVoices[0]);
      }
    };
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }, [selectedVoice]);

  // --- TTS queue processor ---
  // --- TTS queue processor ---
const speakNextInQueue = useCallback(() => {
  if (!ttsEnabled || ttsQueue.current.length === 0) return;

  // Don't cancel current speech; wait until it finishes
  if (window.speechSynthesis.speaking) {
    setTimeout(speakNextInQueue, 200); // check again after 200ms
    return;
  }

  const text = ttsQueue.current.shift();
  if (!text) return;

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 0.8;
  if (selectedVoice) utterance.voice = selectedVoice;

  utterance.onend = () => setTimeout(speakNextInQueue, TTS_SPACING);
  utterance.onerror = () => setTimeout(speakNextInQueue, TTS_SPACING);

  utteranceRef.current = utterance;
  window.speechSynthesis.speak(utterance);
}, [ttsEnabled, selectedVoice]);

// --- Enqueue prediction for TTS ---
const enqueuePrediction = useCallback((text, realSensor) => {
  if (!text || SKIP_GESTURES.includes(text) || !realSensor) return;

  const now = Date.now();
  if (text === lastSpokenPrediction.current) return; // avoid duplicates
  if (now - lastTtsTime.current < TTS_DEBOUNCE) return; // debounce

  lastSpokenPrediction.current = text;
  lastTtsTime.current = now;

  ttsQueue.current.push(text);

  // Only start speaking if not currently speaking
  if (!window.speechSynthesis.speaking) speakNextInQueue();

  toast.info(`Prediction: ${text}`, { autoClose: 1000 });
}, [speakNextInQueue]);

  // --- Poll latest predictions ---
  useEffect(() => {
    let active = true;

    const fetchLatest = async () => {
      if (!active) return;
      setLoading(true);

      try {
        const res = await fetch(LATEST_SENSOR_URL);
        const data = await res.json();

        if (!active) return;

        if (!data.values || data.values.length === 0) {
          setStatus("Waiting for sensor data...");
        } else {
          setPrediction(data.prediction);
          setConfidence(data.confidence);
          setStatus(data.real_sensor ? "Arduino connected" : "Test mode");
          enqueuePrediction(data.prediction, data.real_sensor);
        }
      } catch (err) {
        console.error("Error fetching latest sensor data:", err);
        setStatus("Error connecting");
      } finally {
        setLoading(false);
        if (active) setTimeout(fetchLatest, FETCH_INTERVAL);
      }
    };

    fetchLatest();

    return () => {
      active = false;
      window.speechSynthesis.cancel();
    };
  }, [enqueuePrediction]);

  return (
    <div role="main" aria-label="Live Gesture Prediction Page">
      <div className="card mb-4">
        <h2 tabIndex={0}>Live Gesture Prediction</h2>
        <p style={{ marginTop: 8, color: "#555" }}>
          Real-time predictions from your Sign Glove system. TTS can be toggled and test mode is supported if Arduino is not connected.
        </p>
      </div>

      {!user ? (
        <div className="card mb-4">
          <h3>Welcome</h3>
          <p>Please sign in to view live predictions and enable TTS.</p>
          <a href="/login" className="btn btn-primary">Sign In</a>
        </div>
      ) : (
        <>
          <div className="card mb-4">
            <h3>Status</h3>
            <p style={{ fontWeight: "bold" }}>{status}</p>
            <button
              className={`px-4 py-2 rounded font-bold ${ttsEnabled ? "bg-green-500 text-white" : "bg-gray-300 text-black"}`}
              onClick={() => setTtsEnabled(!ttsEnabled)}
            >
              {ttsEnabled ? "Disable TTS" : "Enable TTS"}
            </button>
          </div>

          <div className="card mb-4">
            <h3>Current Prediction</h3>
            {loading ? (
              <Skeleton height={50} width={200} />
            ) : (
              <div style={{ fontSize: "3rem", fontWeight: "bold", marginTop: 8 }}>
                {prediction}
              </div>
            )}
            {confidence !== null && !loading && (
              <p>Confidence: {(confidence * 100).toFixed(1)}%</p>
            )}
          </div>

          {isTtsSupported && voices.length > 0 && (
            <div className="card mb-4">
              <label htmlFor="voice-select">Select Voice:</label>
              <select
                id="voice-select"
                value={selectedVoice?.name || ""}
                onChange={e => {
                  const voice = voices.find(v => v.name === e.target.value);
                  setSelectedVoice(voice);
                }}
                className="p-2 border rounded"
              >
                {voices.map((v, idx) => (
                  <option key={idx} value={v.name}>{v.name} ({v.lang})</option>
                ))}
              </select>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default LivePredict;
