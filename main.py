import ollama
from speaker import speak
from tools import fast_controls
from tools import windows_agent

# --- 1. THE MASSIVE TOOL SCHEMA ---
TOOL_DEFINITIONS = [
    # Audio & Media
    {
        "type": "function",
        "function": {"name": "set_volume", "description": "Set the system volume to a specific percentage.", "parameters": {"type": "object", "properties": {"level": {"type": "integer", "description": "0 to 100"}}, "required": ["level"]}}
    },
    {
        "type": "function",
        "function": {"name": "mute_speakers", "description": "Mutes or unmutes the speakers.", "parameters": {"type": "object", "properties": {"mute": {"type": "boolean", "description": "True to mute, False to unmute"}}, "required": ["mute"]}}
    },
    {
        "type": "function",
        "function": {"name": "media_play_pause", "description": "Toggles play or pause for active media.", "parameters": {"type": "object", "properties": {}}}
    },
    {
        "type": "function",
        "function": {"name": "media_next", "description": "Skips to the next media track.", "parameters": {"type": "object", "properties": {}}}
    },
    {
        "type": "function",
        "function": {"name": "media_previous", "description": "Returns to the previous media track.", "parameters": {"type": "object", "properties": {}}}
    },
    # Display & Web
    {
        "type": "function",
        "function": {"name": "set_brightness", "description": "Set the display brightness to a specific percentage.", "parameters": {"type": "object", "properties": {"level": {"type": "integer", "description": "0 to 100"}}, "required": ["level"]}}
    },
    {
        "type": "function",
        "function": {"name": "open_browser", "description": "Opens a web browser to a URL or searches Google.", "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "URL or search term"}}, "required": ["query"]}}
    },
    # System State
    {
        "type": "function",
        "function": {"name": "lock_screen", "description": "Locks the Windows computer.", "parameters": {"type": "object", "properties": {}}}
    },
    {
        "type": "function",
        "function": {"name": "sleep_laptop", "description": "Puts the Windows laptop to sleep.", "parameters": {"type": "object", "properties": {}}}
    },
    {
        "type": "function",
        "function": {"name": "get_battery_status", "description": "Checks the current battery percentage and charging state.", "parameters": {"type": "object", "properties": {}}}
    },
    {
        "type": "function",
        "function": {"name": "take_screenshot", "description": "Takes a screenshot of the current screen.", "parameters": {"type": "object", "properties": {}}}
    },
    {
        "type": "function",
        "function": {"name": "get_current_time", "description": "Gets the exact current date and time.", "parameters": {"type": "object", "properties": {}}}
    },
    # The Ultimate Fallback
    {
        "type": "function",
        "function": {
            "name": "execute_powershell",
            "description": "Execute raw PowerShell commands for ANY system task not covered by the dedicated tools above.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "The exact PowerShell command to execute."}},
                "required": ["command"]
            }
        }
    }
]

# Map the string names from the LLM to your actual Python functions
TOOL_MAP = {
    "set_volume": fast_controls.set_volume,
    "mute_speakers": fast_controls.mute_speakers,
    "media_play_pause": fast_controls.media_play_pause,
    "media_next": fast_controls.media_next,
    "media_previous": fast_controls.media_previous,
    "set_brightness": fast_controls.set_brightness,
    "open_browser": fast_controls.open_browser,
    "lock_screen": fast_controls.lock_screen,
    "sleep_laptop": fast_controls.sleep_laptop,
    "get_battery_status": fast_controls.get_battery_status,
    "take_screenshot": fast_controls.take_screenshot,
    "get_current_time": fast_controls.get_current_time,
    "execute_powershell": windows_agent.execute_powershell
}

# --- 2. THE STRICT ROUTING SYSTEM PROMPT ---
MEMORY_LIMIT = 10
conversation_history = [
    {
        "role": "system",
        "content": (
            "You are Jarvis, a precise Windows OS Agent. You have a specific set of tools. "
            "You must follow these STRICT ROUTING RULES: "
            "1. DEDICATED TOOLS: You have dedicated, fast tools for Volume, Muting, Media Control (Play/Pause/Skip), Brightness, Web Browsing, Locking the Screen, Sleeping the Laptop, Checking Battery, Taking Screenshots, and Checking Time. Use them strictly for those exact tasks. "
            "2. THE POWERSHELL FALLBACK: For ALL OTHER tasks (e.g., CPU usage, File management, clearing cache, opening local apps), you MUST use the 'execute_powershell' tool. "
            "3. NO SUBSTITUTION: Do not invent workarounds. If asked to do a task you do not have a dedicated tool for, route it to PowerShell. "
            "4. ADMIT DEFEAT: If a task is impossible, or if PowerShell fails, tell the user gracefully. Do not randomly execute unrelated tools. "
            "5. NO RAW CODE: Never show raw PowerShell code or JSON to the user in your spoken response. Just state the result concisely in natural language."
        )
    }
]

def manage_memory():
    """Ensures we only keep the system prompt and the last N messages."""
    global conversation_history
    if len(conversation_history) > MEMORY_LIMIT + 1:
        conversation_history = [conversation_history[0]] + conversation_history[-(MEMORY_LIMIT):]

# --- 3. THE MAIN LOOP ---
def run_jarvis():
    print("--- JARVIS SYSTEM ONLINE (HYBRID STRICT-ROUTING MODE) ---")
    speak("System active. Strict tool routing protocols engaged.")

    while True:
        try:
            user_input = input("\n[You]: ") 
            
            if not user_input or user_input.strip().lower() in ["exit", "quit"]:
                print("Shutting down...")
                break
            
            # 1. Add to Memory
            conversation_history.append({"role": "user", "content": user_input})

            # 2. Think (Brain)
            response = ollama.chat(
                model='llama3.2',
                messages=conversation_history,
                tools=TOOL_DEFINITIONS
            )

            # 3. Check for Actions (Hands)
            if response.get("message", {}).get("tool_calls"):
                for tool in response["message"]["tool_calls"]:
                    func_name = tool["function"]["name"]
                    kwargs = tool["function"]["arguments"]
                    
                    print(f"\n[*] Routing to Tool: {func_name}")
                    print(f"[*] Arguments Passed: {kwargs}")
                    
                    if func_name in TOOL_MAP:
                        tool_result = TOOL_MAP[func_name](**kwargs)
                        
                        print(f"[*] Tool Output: {tool_result}\n")
                        
                        conversation_history.append({
                            "role": "tool",
                            "name": func_name,
                            "content": str(tool_result)
                        })

                # Let the AI generate its final spoken response
                response = ollama.chat(
                    model='llama3.2',
                    messages=conversation_history
                )

            # 4. Speak (Mouth)
            ai_text = response["message"]["content"]
            conversation_history.append({"role": "assistant", "content": ai_text})
            
            print(f"\n[Jarvis]: {ai_text}")
            speak(ai_text)
            
            # 5. Clean Memory
            manage_memory()

        except KeyboardInterrupt:
            print("\nShutting down Jarvis...")
            break
        except Exception as e:
            print(f"\n[System Error]: {e}")
            speak("I encountered an internal error.")

if __name__ == "__main__":
    run_jarvis()