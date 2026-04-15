"""
Speech Handler using Vosk
Handles speech-to-text functionality with offline Spanish recognition
Includes wake word detection ("Hola JARVIS")
"""

import os
import json
import pyaudio
import threading
import time
from vosk import Model, KaldiRecognizer


# Wake words that activate JARVIS
WAKE_WORDS = [
    # Hola variants
    "hola jarvis",
    "hola yarvis",
    "hola charvis",
    # Oye variants  
    "oye jarvis",
    "oye yarvis",
    # Hey/Ey variants
    "hey jarvis",
    "hey yarvis",
    "ey jarvis",
    "ei jarvis",
    # Just the name
    "jarvis",
    "yarvis",
    "charvis",
    "jarbes",
    "jarbi",
    "yarbis",
    # Common misrecognitions
    "harvis",
    "jarbis",
    # Special phrases
    "jarvis estás listo",
    "jarvis estas listo",
    "yarvis estás listo",
    "yarvis estas listo",
    "estás listo jarvis",
    "estas listo jarvis",
]

# Corrections for words that Vosk doesn't recognize well
WORD_CORRECTIONS = {
    "chron": "chrome",
    "cron": "chrome",
    "krom": "chrome",
    "crom": "chrome",
    "grom": "chrome",
    "from": "chrome",  # Only in context of "abre from" -> "abre chrome"
    "gúguel": "google",
    "guguel": "google",
    "gugle": "google",
    "espotifai": "spotify",
    "espotify": "spotify",
    "spotifai": "spotify",
    "yutu": "youtube",
    "yutub": "youtube",
    "yutube": "youtube",
    "guasap": "whatsapp",
    "wasap": "whatsapp",
    "whasap": "whatsapp",
}


def correct_text(text: str) -> str:
    """Apply word corrections to recognized text"""
    words = text.lower().split()
    corrected_words = []
    for word in words:
        corrected_words.append(WORD_CORRECTIONS.get(word, word))
    return ' '.join(corrected_words)


class SpeechHandler:
    def __init__(self):
        # Setup Vosk model
        model_path = os.path.join("models", "vosk-model-small-es-0.42")
        if not os.path.exists(model_path):
            raise Exception(f"Modelo no encontrado en {model_path}. Ejecuta download_vosk_model.py")
        
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.recognizer.SetWords(True)
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_size = 4000
        self.audio = pyaudio.PyAudio()
        
    def listen(self, timeout=10, phrase_time_limit=30, continuous=False) -> str:
        """
        Listen for audio input and convert to text using Vosk
        
        Args:
            timeout: Seconds to wait for speech to start
            phrase_time_limit: Maximum seconds for the phrase
            continuous: If True, keeps listening until speech is detected
            
        Returns:
            Recognized text or empty string if failed
        """
        try:
            # Open audio stream
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            print("Listening...")
            
            # Listen for audio
            frames = []
            silent_chunks = 0
            max_silent_chunks = int(timeout * self.sample_rate / self.chunk_size)
            recording = False
            
            # Reset recognizer
            self.recognizer.Reset()
            
            while True:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Process audio chunk
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').strip()
                    if text:
                        stream.stop_stream()
                        stream.close()
                        corrected = correct_text(text)
                        print(f"Recognized: {text} -> {corrected}")
                        return corrected
                    recording = True
                    silent_chunks = 0
                else:
                    # Check partial results to detect speech
                    partial = json.loads(self.recognizer.PartialResult())
                    if partial.get('partial', '').strip():
                        recording = True
                        silent_chunks = 0
                    elif recording:
                        silent_chunks += 1
                    else:
                        silent_chunks += 1
                
                # Stop if timeout or max phrase length reached
                # If continuous mode and still waiting for speech, don't timeout
                if continuous and not recording:
                    silent_chunks = 0  # Reset timeout while waiting for speech
                elif silent_chunks > max_silent_chunks or len(frames) > phrase_time_limit * self.sample_rate / self.chunk_size:
                    break
            
            # Get final result
            final_result = json.loads(self.recognizer.FinalResult())
            text = final_result.get('text', '').strip()
            
            stream.stop_stream()
            stream.close()
            
            if text:
                corrected = correct_text(text)
                print(f"Recognized: {text} -> {corrected}")
                return corrected
            else:
                print("No speech detected")
                return ""
                
        except Exception as e:
            print(f"Error: {e}")
            return ""
            
    def listen_continuous(self, callback, stop_event):
        """
        Listen continuously and call callback with recognized text
        
        Args:
            callback: Function to call with recognized text
            stop_event: Threading event to stop listening
        """
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.recognizer.Reset()
            
            while not stop_event.is_set():
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').strip()
                    if text:
                        callback(text)
                        
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Error: {e}")
            
    def listen_for_wake_word(self, callback, stop_event):
        """
        Listen continuously for wake word and trigger callback when detected
        
        Args:
            callback: Function to call when wake word is detected (receives detected text)
            stop_event: Threading event to stop listening
        """
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            # Create separate recognizer for wake word detection
            wake_recognizer = KaldiRecognizer(self.model, 16000)
            
            print("🎙️ Escuchando... Di 'Jarvis' o 'Hola Jarvis'...")
            
            while not stop_event.is_set():
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                
                if wake_recognizer.AcceptWaveform(data):
                    result = json.loads(wake_recognizer.Result())
                    text = result.get('text', '').strip().lower()
                    
                    if text:
                        # Check if any wake word is in the recognized text
                        for wake_word in WAKE_WORDS:
                            if wake_word in text:
                                print(f"🔔 Wake word detected: '{text}'")
                                callback(text)  # Pass detected text
                                # Small delay to avoid multiple triggers
                                time.sleep(0.5)
                                wake_recognizer.Reset()
                                break
                else:
                    # Also check partial results for faster response
                    partial = json.loads(wake_recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip().lower()
                    
                    for wake_word in WAKE_WORDS:
                        if wake_word in partial_text:
                            print(f"🔔 Wake word detected (partial): '{partial_text}'")
                            callback(partial_text)  # Pass detected text
                            time.sleep(0.5)
                            wake_recognizer.Reset()
                            break
                            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Wake word error: {e}")
    
    def __del__(self):
        """Cleanup PyAudio"""
        if hasattr(self, 'audio'):
            self.audio.terminate()
