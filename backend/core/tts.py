# backend/core/tts.py
import pyttsx3
import threading
import time
from queue import Queue

class TTSWorker:
    def __init__(self, debounce_seconds=2.0):
        self.queue = Queue()
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        self.engine.setProperty("volume", 1.0)
        self.last_spoken_text = None
        self.last_time = 0.0
        self.debounce_seconds = debounce_seconds
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def enqueue(self, text: str):
        self.queue.put(text)

    def run(self):
        while True:
            text = self.queue.get()
            if not text:
                continue
            now = time.time()
            with self.lock:
                if text == self.last_spoken_text and (now - self.last_time) < self.debounce_seconds:
                    continue
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                    self.last_spoken_text = text
                    self.last_time = now
                except Exception as e:
                    print(f"TTS error: {e}")
