# FixMe — Architecture

## Overview

FixMe is an AI-powered IT support assistant that diagnoses and fixes common computer issues through screenshot analysis, voice interaction, and guided step-by-step remediation. It uses Claude (Anthropic) for vision-based diagnosis and conversational flow, ElevenLabs for multilingual text-to-speech, and a pure tkinter desktop UI.

## Project Structure

```
fixme/
├── fixme/                  # Core Python package
│   ├── __init__.py         # Package init
│   ├── app.py              # System tray entry point (Windows)
│   ├── conversation.py     # Voice conversation flow orchestrator
│   ├── diagnose.py         # Claude Vision screenshot diagnosis
│   ├── fixes.py            # IT fix command execution (Windows)
│   ├── overlay.py          # Transparent annotation overlay
│   ├── recorder.py         # Screen recording (mss + OpenCV)
│   ├── screenshot.py       # Screen capture (mss)
│   ├── tts.py              # Text-to-speech (ElevenLabs + Claude translation)
│   ├── ui.py               # Desktop chat UI (pure tkinter)
│   └── voice_input.py      # Speech recognition (SAPI / tkinter fallback)
├── landing/                # React landing page
│   ├── src/
│   │   ├── App.jsx         # Main landing page component
│   │   ├── App.css         # (empty — Tailwind only)
│   │   ├── index.css       # Tailwind base + dark body
│   │   └── main.jsx        # React root mount
│   ├── index.html          # HTML shell
│   ├── vite.config.js      # Vite + Tailwind CSS v4 plugin
│   └── package.json        # Dependencies
├── prompts/                # PDD prompt files
│   ├── app_python.prompt
│   ├── conversation_python.prompt
│   ├── diagnose_python.prompt
│   ├── fixes_python.prompt
│   ├── overlay_python.prompt
│   ├── recorder_python.prompt
│   ├── screenshot_python.prompt
│   ├── tts_python.prompt
│   └── voice_input_python.prompt
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not committed)
└── README.md
```

## Module Details

### `fixme/__init__.py`
- **Imports:** None
- **Purpose:** Package marker. Docstring describes FixMe.

### `fixme/app.py` — System Tray Application
- **Standard lib:** `os`, `sys`, `threading`, `warnings`
- **Third-party:** `dotenv`, `PIL` (Pillow), `pystray`
- **Local:** `fixme.screenshot`, `fixme.diagnose`, `fixme.fixes`, `fixme.tts`, `fixme.voice_input`, `fixme.conversation.ConversationFlow`, `fixme.overlay.Overlay`, `fixme.recorder.ScreenRecorder`
- **Classes:** `FixMeApp` — Wires all modules together via a Windows system tray icon with menu actions for diagnosis, quick fixes, recording, and language switching.
- **Entry point:** `main()` function.

### `fixme/conversation.py` — Conversation Flow
- **Standard lib:** `os`, `warnings`
- **Third-party:** `anthropic`
- **Local:** `fixme.voice_input.is_affirmative`, `fixme.voice_input.is_negative`
- **Classes:** `ConversationFlow` — Orchestrates a voice-driven ask-before-every-action permission loop for executing IT fixes.

### `fixme/diagnose.py` — Screenshot Diagnosis
- **Standard lib:** `base64`, `json`, `os`
- **Third-party:** `anthropic`
- **Functions:** `diagnose_screenshot(path)` — Sends a screenshot to Claude Vision API and returns structured JSON with issue description and fix steps.

### `fixme/fixes.py` — Fix Execution
- **Standard lib:** `ctypes`, `re`, `subprocess`, `time`
- **Functions:** `get_current_ssid()`, `execute(cmd)`, `get_available_fixes()` — Runs Windows shell commands (netsh, ipconfig, rundll32) with optional UAC elevation via `ctypes.windll.shell32.ShellExecuteW`.

### `fixme/overlay.py` — Annotation Overlay
- **Standard lib:** `threading`, `warnings`
- **Classes:** `Overlay` — Creates a transparent, click-through fullscreen tkinter window that highlights UI elements and shows step text during fix execution.

### `fixme/recorder.py` — Screen Recording
- **Standard lib:** `os`, `threading`, `time`, `warnings`, `datetime`
- **Third-party:** `cv2` (OpenCV), `mss`, `numpy`
- **Classes:** `ScreenRecorder` — Captures frames via mss in a background thread and writes MP4 via OpenCV's VideoWriter.

### `fixme/screenshot.py` — Screen Capture
- **Standard lib:** `os`, `tempfile`
- **Third-party:** `mss`
- **Functions:** `take_screenshot()` — Captures the primary monitor and saves to a temp PNG file.

### `fixme/tts.py` — Text-to-Speech
- **Standard lib:** `os`, `tempfile`, `warnings`
- **Third-party:** `anthropic`, `elevenlabs`
- **Functions:** `translate_to_spanish(text)`, `speak(text, lang)` — Translates via Claude, generates audio via ElevenLabs API, plays with system player.
- **Supported languages:** English (en), Spanish (es), Punjabi (pa), Hindi (hi), French (fr).

### `fixme/voice_input.py` — Voice Input
- **Standard lib:** `threading`, `warnings`
- **Third-party:** `win32com.client` (SAPI), `tkinter` (fallback)
- **Functions:** `is_affirmative(text)`, `is_negative(text)`, `listen()` — Windows SAPI speech recognition with a tkinter text-entry fallback for non-Windows platforms.

### `fixme/ui.py` — Desktop Chat UI
- **Standard lib:** `os`, `sys`, `math`, `threading`, `time`, `json`, `tkinter`, `datetime`, `pathlib`
- **Third-party:** `dotenv`, `anthropic`
- **Classes:**
  - `HistoryManager` — JSON persistence at `~/.fixme/history.json`
  - `VoiceOrb(tk.Canvas)` — Animated microphone button with idle/listening/speaking states
  - `ScrollFrame(tk.Frame)` — Custom scrollable frame using `tk.Canvas` + inner `tk.Frame`
  - `Sidebar(tk.Frame)` — History list + language selector + action buttons
  - `FixMeUI(tk.Tk)` — Main window: two-pane layout with sidebar and chat area
- **Note:** Uses pure tkinter (no customtkinter) to avoid macOS `NSWindow` threading crashes.

## Landing Page (`landing/`)

React + Vite + Tailwind CSS v4 single-page application.

- **Vite config:** Uses `@tailwindcss/vite` plugin
- **App.jsx sections:** Nav, Hero (gradient blobs), Stats, Features (6 cards), HowItWorks, Languages (5-language selector), Comparison, CTA, Footer
- **Theme:** Dark (#09090B background), indigo brand accent
- **Font:** Inter (Google Fonts)

## Dependency Map

```
fixme/ui.py ──→ anthropic (Claude API)
              ──→ dotenv
              ──→ tkinter (stdlib)

fixme/app.py ──→ pystray, Pillow
             ──→ fixme.screenshot ──→ mss
             ──→ fixme.diagnose   ──→ anthropic
             ──→ fixme.fixes      ──→ subprocess, ctypes
             ──→ fixme.tts        ──→ anthropic, elevenlabs
             ──→ fixme.voice_input──→ win32com (SAPI)
             ──→ fixme.conversation──→ anthropic
             ──→ fixme.overlay    ──→ tkinter
             ──→ fixme.recorder   ──→ cv2, mss, numpy
```

## API Keys Required

| Key | Service | Used by |
|-----|---------|---------|
| `ANTHROPIC_API_KEY` | Claude (Anthropic) | diagnose.py, conversation.py, tts.py, ui.py |
| `ELEVENLABS_API_KEY` | ElevenLabs TTS | tts.py |

## Running

```bash
# Desktop UI
./venv/bin/python -m fixme.ui

# System tray app (Windows)
./venv/bin/python -m fixme.app

# Landing page
cd landing && npm run dev
```
