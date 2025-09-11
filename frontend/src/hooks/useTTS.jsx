import { useRef, useCallback } from "react";

const useTTS = (debounceMs = 2000, spacingMs = 1000) => {
  const ttsQueue = useRef([]);
  const utteranceRef = useRef(null);
  const lastSpoken = useRef("");
  const lastTime = useRef(0);

  const speakNext = useCallback(() => {
    if (ttsQueue.current.length === 0) return;

    if (window.speechSynthesis.speaking) {
      setTimeout(speakNext, 200); // check again in 200ms
      return;
    }

    const text = ttsQueue.current.shift();
    if (!text) return;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 0.8;

    utterance.onend = () => setTimeout(speakNext, spacingMs);
    utterance.onerror = () => setTimeout(speakNext, spacingMs);

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, [spacingMs]);

  const speak = useCallback(
    (text) => {
      if (!text || typeof text !== "string") return;

      const now = Date.now();
      if (text === lastSpoken.current && now - lastTime.current < debounceMs) return;

      lastSpoken.current = text;
      lastTime.current = now;

      ttsQueue.current.push(text);
      if (!window.speechSynthesis.speaking) speakNext();
    },
    [debounceMs, speakNext]
  );

  return { speak };
};

export default useTTS;
