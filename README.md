# 🤖 Jarvis — Offline AI Personal Assistant for Windows

A fully **offline, privacy-first** voice-controlled AI assistant built for Windows. Jarvis listens for a wake word, transcribes your commands with high accuracy, and executes real actions on your PC — all without sending a single byte to the cloud.

---

## 🧠 How It Works

```
Microphone Input
      │
      ▼
┌─────────────────────┐
│  Vosk (Wake Word)   │  ◄─── Always listening, ultra-low CPU
│  "Computer..."      │
└─────────────────────┘
      │  Wake word detected
      ▼
┌─────────────────────┐
│  Whisper (base.en)  │  ◄─── High-accuracy offline transcription
│  faster-whisper     │       runs fully on CPU with int8 quantization
└─────────────────────┘
      │  Command text
      ▼
┌──────────────────────────────────────────────────┐
│          main.py — Ollama Tool-Calling Loop       │
│  Model: llama3.2  │  Sliding memory (last 10)    │
│  Strict routing system prompt enforced            │
└──────────────────────────────────────────────────┘
      │  Tool calls (JSON)
      ▼
┌──────────────────────────────────────────────────────┐
│                    Tools Layer                        │
│  fast_controls.py   │ windows_agent.py │ web_agent.py│
│  Volume, Brightness │ PowerShell exec  │ Playwright   │
│  Screenshot, Battery│ Safety Sandbox   │ Browser CDP  │
│  open_browser()     │ 30+ Blocklist    │ YouTube Ghost│
└──────────────────────────────────────────────────────┘
      │  Result
      ▼
┌─────────────────────┐
│  speaker.py (TTS)   │  ◄─── pyttsx3 + pygame, barge-in with SPACEBAR
└─────────────────────┘
```

---

## ✨ Features

### 🎙️ Voice Pipeline
- **Wake Word Detection** — Always-on, low-latency wake word (`"Computer"`) via **Vosk** + KaldiRecognizer running at 16kHz. Zero cloud dependency.
- **Command Transcription** — After wake, records your full command and transcribes it with **faster-whisper** (`base.en`), using `int8` quantization to run entirely on CPU (DDR5 RAM accelerated).
- **Context Hints** — A custom initial prompt biases Whisper to correctly spell proper nouns like `Vedant`, `YouTube`, `LinkedIn`, etc.
- **Static Energy Threshold** — Prevents the first word of your command from being clipped, with a 1.5s silence pause threshold for natural speech cadence.

### 🔊 Text-to-Speech (TTS)
- **Offline, Instant Speech** — Uses Windows' built-in voices via `pyttsx3` at a natural 170 WPM rate.
- **Barge-In Support** — Press `SPACEBAR` at any time to instantly stop Jarvis mid-sentence. Powered by `pygame` mixer + `keyboard` listener.
- **Automatic Cleanup** — Temporary `.wav` files are generated and deleted on every utterance — no audio clutter on disk.

### 🧠 LLM Orchestrator (`main.py`)
The central brain is now fully operational — a **strict-routing, tool-calling loop** powered by Ollama (Llama 3.2):

- **Tool Schema (`TOOL_DEFINITIONS`)** — 13 typed function schemas exposed to the LLM, covering audio, display, system state, web, and PowerShell.
- **Tool Map (`TOOL_MAP`)** — Direct Python function dispatch: LLM tool call names map 1-to-1 to real function objects.
- **Strict Routing System Prompt** — Enforces 5 hard rules:
  1. Use dedicated tools for their exact tasks (volume, brightness, battery, etc.)
  2. Route everything else to `execute_powershell`
  3. No improvised workarounds
  4. Admit defeat gracefully if a task is impossible
  5. Never show raw code or JSON in spoken responses
- **Sliding Memory** — Keeps only the last 10 turns plus the system prompt to prevent context overflow.
- **Two-Stage Inference** — First call decides tool(s); second call generates the final natural-language spoken response after tool results are fed back.

### ⚡ Fast System Controls (`tools/fast_controls.py`)
Direct, instant Windows system control without LLM overhead:

| Function | Description |
|---|---|
| `set_volume(level)` | Set master volume 0–100% via Windows Core Audio API (pycaw) |
| `mute_speakers(mute)` | Mute / unmute system audio |
| `media_play_pause()` | Toggle play/pause for any active media |
| `media_next()` | Skip to next track |
| `media_previous()` | Go to previous track |
| `set_brightness(level)` | Control display brightness 0–100% |
| `open_browser(query)` | Open a URL directly or Google-search any query via `webbrowser` |
| `lock_screen()` | Instantly lock the Windows workstation |
| `sleep_laptop()` | Put the machine to sleep |
| `get_battery_status()` | Read battery percentage and charge state |
| `take_screenshot()` | Take and save a timestamped screenshot to `~/Pictures/Screenshots/` |
| `get_current_time()` | Return exact date and time for LLM temporal awareness |

> **AI Hallucination Guard** — `_extract_number()` defensively strips numeric values from any malformed dict/string the LLM might pass, preventing crashes from AI argument formatting errors.

### 🌐 Playwright Browser Agent (`tools/web_agent.py`)
Advanced browser automation via **Playwright CDP (Chrome DevTools Protocol)**:

- **`start_jarvis_browser()`** — Launches a dedicated Chrome instance with a remote debugging port (`9222`) and an isolated profile (`C:\JarvisProfile`), keeping Jarvis' browsing separate from your personal tabs.
- **`search_youtube_active(query)`** — Connects to the already-open Jarvis browser without opening a new one:
  1. Connects over CDP to `localhost:9222`
  2. Grabs the active tab in the existing context
  3. Navigates to YouTube if not already there
  4. **Ghost-Types** the query character-by-character (100ms delay) into the search bar for human-like interaction
  5. Hits Enter and disconnects smoothly without closing the browser

### 🛡️ Sandboxed PowerShell Agent (`tools/windows_agent.py`)
Execute arbitrary PowerShell commands for complex, AI-generated tasks — with a **multi-layer safety net**:

- **Blocklist of 30+ Dangerous Keywords** across 6 categories:
  - File & disk destruction (`delete`, `format`, `diskpart`, ...)
  - Process & power controls (`shutdown`, `taskkill`, `kill`, ...)
  - Network alteration (`netsh`, `firewall`, `ipconfig /release`, ...)
  - Registry & boot modification (`bcdedit`, `reg.exe`, `wmic`, ...)
  - Service & user account changes (`stop-service`, `net user`, ...)
  - Software removal (`winget uninstall`, `msiexec /x`, ...)
- **Human-in-the-Loop Confirmation** — Any blocked command returns a `REQUIRES_CONFIRMATION` token, causing Jarvis to ask you out loud before proceeding.
- **Visible Window Execution** — PowerShell runs in a new, visible terminal window with `-NoExit` so you can inspect the output.
- **`safety_bypassed` Flag** — Internal override for confirmed-dangerous commands after user approval.

---

## 📁 Project Structure

```
personal assistant/
│
├── main.py                  # LLM orchestrator: Ollama tool-calling loop + memory management
├── audio_engine.py          # Wake word detection (Vosk) + Whisper transcription pipeline
├── speaker.py               # Offline TTS with SPACEBAR barge-in support
├── llm_client.py            # Ollama/Llama 3.2 stub (for future VRAM management)
├── file_structure.py        # One-time project scaffold script
│
├── tools/
│   ├── __init__.py
│   ├── fast_controls.py     # Direct Windows API system controls + open_browser()
│   ├── windows_agent.py     # Sandboxed PowerShell execution engine
│   └── web_agent.py         # Playwright CDP browser automation (YouTube ghost-typing)
│
├── vosk_model/              # Vosk offline speech model (not tracked by git)
├── temp/                    # Runtime temp folder for .wav files (auto-created)
│
├── .env                     # Environment variables (Porcupine key, etc.) — gitignored
├── .gitignore
└── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+**
- **Windows OS** (hard dependency — uses Windows Core Audio API, PowerShell, ctypes)
- A working **microphone**
- **[Ollama](https://ollama.com/)** installed and running locally with `llama3.2` pulled
- [**Vosk model**](https://alphacephei.com/vosk/models) — Download `vosk-model-small-en-us` and place the folder as `vosk_model/` in the project root

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/personal-assistant.git
cd "personal assistant"
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

> **Note:** `pyaudio` may require a pre-built wheel on Windows. If `pip install pyaudio` fails, download the correct `.whl` from [Gohlke's repository](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install it manually.

### 4. Install Playwright Browsers
```bash
playwright install chromium
```

### 5. Pull the LLM Model (Ollama)
```bash
ollama pull llama3.2
```

### 6. Download the Vosk Model
```bash
# Download from https://alphacephei.com/vosk/models
# Extract and rename the folder to: vosk_model/
```

### 7. Configure Environment Variables
Create a `.env` file in the project root:
```env
PORCUPINE_ACCESS_KEY=your_picovoice_key_here
```

> Get a free Porcupine key at [picovoice.ai](https://picovoice.ai/). This is only required if using Picovoice for wake word detection.

### 8. Run the Assistant
```bash
python main.py
```

Type your command at the `[You]:` prompt. Say **"exit"** or **"quit"** to shut down.

> **Voice mode:** Run `audio_engine.py` standalone to test the wake word + Whisper pipeline. Full voice integration into `main.py` is the next milestone.

---

## ⚙️ Dependencies

| Package | Purpose |
|---|---|
| `ollama` | Local LLM inference client (Llama 3.2 tool-calling) |
| `faster-whisper` | High-accuracy offline speech-to-text (CPU int8) |
| `vosk` | Always-on wake word detection |
| `SpeechRecognition` | Microphone capture and audio buffer management |
| `pyaudio` | Low-level audio stream from microphone |
| `pyttsx3` | Offline Windows TTS engine |
| `pygame` | Audio playback with barge-in support |
| `keyboard` | Global hotkey detection (SPACE to interrupt) |
| `pycaw` | Windows Core Audio API for volume control |
| `screen-brightness-control` | Monitor brightness API |
| `psutil` | Battery status and system metrics |
| `Pillow` | Screenshot capture via `ImageGrab` |
| `playwright` | Headless/headed browser automation via CDP |
| `python-dotenv` | `.env` file loading |
| `pvporcupine` | (Optional) Picovoice wake word engine |
| `openai` | OpenAI API client (for cloud fallback, optional) |
| `duckduckgo-search` | Web search capability for the LLM agent |
| `python-docx` | Document read/write for office-related tasks |

---

## 🗺️ Roadmap

- [x] Vosk wake word detection pipeline
- [x] faster-whisper CPU transcription with context hints
- [x] Offline TTS with SPACEBAR barge-in
- [x] Fast system controls (volume, brightness, battery, screenshot, sleep, lock)
- [x] `open_browser()` — Google search / URL opener
- [x] Sandboxed PowerShell agent with 30+ keyword blocklist
- [x] **LLM Client integration (Llama 3.2 via Ollama)**
- [x] **Full orchestration in `main.py` — strict-routing tool-calling loop**
- [x] **Playwright browser agent — Chrome CDP + YouTube ghost-typing**
- [ ] Full voice integration — wire `audio_engine.py` into `main.py`
- [ ] Web search tool via DuckDuckGo exposed to LLM
- [ ] Document read/write capabilities exposed to LLM
- [ ] Multi-turn conversation memory (persistent across sessions)
- [ ] VRAM-aware Llama loading/unloading via `llm_client.py`

---

## 🔒 Privacy

This assistant is designed to be **100% offline** by default:
- Vosk runs locally — no audio leaves your machine during wake word detection.
- faster-whisper runs on-device — your voice commands are never uploaded.
- pyttsx3 uses Windows' built-in voices — no TTS API calls.
- The LLM is **Ollama (local Llama 3.2)** — no OpenAI by default.
- Playwright runs a local Chrome instance — browsing is not proxied or logged.

The `.env` and `vosk_model/` are gitignored to prevent credential and large model leaks.

---

## 📄 License

This project is for personal use. Feel free to fork and extend it.