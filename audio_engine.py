import os
import json
import pyaudio
from vosk import Model, KaldiRecognizer
import speech_recognition as sr
from faster_whisper import WhisperModel

# --- 1. SETUP MODELS (CPU ONLY) ---
print("Loading Whisper (Base) and Vosk models into System RAM...")

if not os.path.exists("vosk_model"):
    print("ERROR: Please download the Vosk model and place it in a folder named 'vosk_model'")
    exit(1)
vosk_model = Model("vosk_model")
wake_word_recognizer = KaldiRecognizer(vosk_model, 16000)

# UPGRADE 1: Using "base.en" for much higher accuracy
whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")
print("Models loaded successfully!\n")

# --- 2. AUDIO FUNCTIONS ---

def listen_for_wake_word():
    """Continuously listens in the background for the word 'computer'."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("\n[Vosk] Listening for wake word: 'Computer'...")

    while True:
        # exception_on_overflow=False prevents the stream from crashing if the CPU hiccups
        data = stream.read(4000, exception_on_overflow=False)
        if wake_word_recognizer.AcceptWaveform(data):
            result = json.loads(wake_word_recognizer.Result())
            text = result.get("text", "")
            
            if "computer" in text:
                print("\n*** WAKE WORD DETECTED! ***")
                stream.stop_stream()
                stream.close()
                p.terminate()
                return True

def record_and_transcribe_command():
    """Records the user's command and translates it using Whisper."""
    recognizer = sr.Recognizer()
    
    # UPGRADE 3: Static thresholds prevent the mic from clipping the first word you say
    recognizer.energy_threshold = 300 
    recognizer.dynamic_energy_threshold = False
    recognizer.pause_threshold = 1.5 # Waits 1.5s of silence before stopping recording
    
    with sr.Microphone() as source:
        print("[Whisper] Listening to your command now... (Speak normally)")
        audio = recognizer.listen(source)
        
    print("[Whisper] Transcribing on DDR5 RAM...")
    
    temp_file = "temp/temp_command.wav"
    with open(temp_file, "wb") as f:
        f.write(audio.get_wav_data())
        
    # UPGRADE 2: The Initial Prompt biases the AI to spell these specific words correctly
    context_hint = "Vedant, YouTube, Chrome, LinkedIn, folder, file, laptop, search."
    
    segments, _ = whisper_model.transcribe(
        temp_file, 
        beam_size=5,
        initial_prompt=context_hint 
    )
    
    text = "".join([segment.text for segment in segments])
    
    os.remove(temp_file)
    
    return text.strip()

# --- 3. TEST LOOP ---
if __name__ == "__main__":
    if not os.path.exists("temp"):
        os.makedirs("temp")
        
    try:
        while True:
            listen_for_wake_word()
            command = record_and_transcribe_command()
            print(f">>> You commanded: '{command}'\n")
            
    except KeyboardInterrupt:
        print("\nExiting Audio Engine.")