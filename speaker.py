import os
import pyttsx3
import pygame
import keyboard
import time

def speak(text: str):
    """
    Generates fast, offline speech using the built-in Windows voice. 
    Can be interrupted at any time by pressing the SPACEBAR.
    """
    print(f"\n[Jarvis]: {text}")
    
    audio_file = "temp/temp_voice.wav"
    
    # 1. Generate the audio file instantly using Windows built-in voices
    engine = pyttsx3.init()
    engine.setProperty('rate', 170) # 170 is a crisp, natural speed
    
    # Save it to a file instantly
    engine.save_to_file(text, audio_file)
    engine.runAndWait()

    # 2. Play the audio using our Kill Switch logic
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

    print("[System] Speaking... (Press 'SPACE' to interrupt)")

    # 3. The "Barge-in" Loop
    while pygame.mixer.music.get_busy():
        if keyboard.is_pressed('space'):
            print("\n*** AUDIO INTERRUPTED BY USER ***")
            pygame.mixer.music.stop()
            break
        time.sleep(0.05)
        
    # 4. Clean up
    pygame.mixer.quit()
    
    if os.path.exists(audio_file):
        try:
            os.remove(audio_file)
        except:
            pass

# --- TEST ---
if __name__ == "__main__":
    if not os.path.exists("temp"):
        os.makedirs("temp")
        
    test_text = "Reverted to built-in Windows audio systems. System is stable and ready to proceed."
    speak(test_text) 