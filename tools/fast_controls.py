import os
import time
import ctypes
from datetime import datetime
import keyboard
import psutil
from PIL import ImageGrab
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- 1. AUDIO & MEDIA ---

def set_volume(level: int):
    """Sets master volume to a specific percentage (0-100)."""
    try:
        level = max(0, min(100, level))
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Volume set to {level}%."
    except Exception as e:
        return f"Failed to set volume: {e}"

def mute_speakers(mute: bool = True):
    """Mutes or unmutes the main speakers."""
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        # 1 for mute, 0 for unmute
        volume.SetMute(1 if mute else 0, None)
        return "Speakers muted." if mute else "Speakers unmuted."
    except Exception as e:
        return f"Failed to toggle mute: {e}"

def media_play_pause():
    """Toggles play/pause for whatever media is currently active."""
    keyboard.send("play/pause media")
    return "Media play/pause toggled."

def media_next():
    """Skips to the next track."""
    keyboard.send("next track")
    return "Skipped to next track."

def media_previous():
    """Returns to the previous track."""
    keyboard.send("previous track")
    return "Returned to previous track."

# --- 2. DISPLAY ---

def set_brightness(level: int):
    """Sets the main display brightness (0-100)."""
    try:
        level = max(0, min(100, level))
        sbc.set_brightness(level)
        return f"Screen brightness set to {level}%."
    except Exception as e:
        return f"Failed to set brightness: {e}"

# --- 3. SYSTEM STATE & SECURITY ---

def lock_screen():
    """Instantly locks the Windows machine."""
    ctypes.windll.user32.LockWorkStation()
    return "Screen locked."

def sleep_laptop():
    """Puts the laptop to sleep."""
    # Note: AI will lose connection to you until you wake it back up!
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return "Laptop is going to sleep."

def get_battery_status():
    """Reads current battery percentage and power state."""
    try:
        battery = psutil.sensors_battery()
        if not battery:
            return "Cannot read battery status (might be a desktop PC)."
        
        plugged = "Plugged in" if battery.power_plugged else "Running on battery"
        return f"Battery is at {battery.percent}%. {plugged}."
    except Exception as e:
        return f"Failed to read battery: {e}"

def take_screenshot():
    """Takes a screenshot and saves it to the default Windows Screenshots folder."""
    try:
        # Dynamically find the user's official Pictures/Screenshots folder
        pictures_dir = os.path.join(os.path.expanduser('~'), 'Pictures', 'Screenshots')
        os.makedirs(pictures_dir, exist_ok=True) # Create it if it doesn't exist
        
        # Name it cleanly with a timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"Screenshot_{timestamp}.png"
        filepath = os.path.join(pictures_dir, filename)
        
        img = ImageGrab.grab()
        img.save(filepath)
        return f"Screenshot successfully saved to {filepath}."
    except Exception as e:
        return f"Failed to take screenshot: {e}"

# --- 4. SILENT TOOLS (Grounding) ---

def get_current_time():
    """Returns exact current time and date so the AI has temporal awareness."""
    now = datetime.now()
    return now.strftime("Current date and time is: %A, %B %d, %Y - %I:%M %p")