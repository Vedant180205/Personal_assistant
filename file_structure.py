import os

# The exact path you provided
base_path = r"C:\Users\vedant\OneDrive\Desktop\personal assistant"

# The folders and files to create
structure = {
    "temp": None, # None means it's just a folder
    "main.py": "# The central orchestrator.\n# This will tie audio_engine, llm_client, and tools together.\n",
    "audio_engine.py": "# Handles microphone input, Porcupine wake word, and faster-whisper CPU translation.\n",
    "llm_client.py": "# Manages the connection to Ollama (Llama 3.2) and handles VRAM loading/unloading.\n",
    "tools.py": "# Contains the functions for the AI to interact with Windows and the Web.\n",
    ".env": "# Store your environment variables here (like the Porcupine access key).\n",
    "requirements.txt": "openai\nduckduckgo-search\npython-docx\nfaster-whisper\npvporcupine\npyaudio\nSpeechRecognition\npython-dotenv\n"
}

def create_project_structure():
    # Ensure the base directory exists
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        print(f"Created base directory: {base_path}")

    # Create the files and folders
    for name, content in structure.items():
        item_path = os.path.join(base_path, name)
        
        if content is None:
            # Create folder
            if not os.path.exists(item_path):
                os.makedirs(item_path)
                print(f"Created folder: {name}/")
        else:
            # Create file
            with open(item_path, "w") as f:
                f.write(content)
            print(f"Created file: {name}")

    print("\nProject structure generated successfully!")

# Run the function
create_project_structure()