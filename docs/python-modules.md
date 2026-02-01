# Core Python Modules (`fixme/`)

The `fixme` package contains the backend logic used by the sidecar. These modules are imported by `sidecar/main.py` and are not modified by the desktop app migration.

## Directory Structure

```
fixme/
├── __init__.py         # Package marker
├── app.py              # Legacy system tray entry point (Windows)
├── conversation.py     # Voice conversation flow orchestrator
├── diagnose.py         # Claude Vision screenshot diagnosis
├── fixes.py            # IT fix command execution (macOS + Windows)
├── overlay.py          # Legacy annotation overlay (tkinter)
├── recorder.py         # Screen recording (mss + OpenCV)
├── screenshot.py       # Screen capture (mss)
├── tts.py              # Text-to-speech (ElevenLabs)
├── ui.py               # Legacy tkinter UI (replaced by desktop/)
└── voice_input.py      # Legacy speech recognition (replaced by Web Speech API)
```

## Active Modules (used by sidecar)

### `fixme/diagnose.py` — Screenshot Diagnosis

- Sends a screenshot to Claude Vision API (`claude-sonnet-4-20250514`)
- Returns structured JSON with issue description and fix steps
- OS-aware prompts (macOS vs Windows commands)
- **Dependencies:** `anthropic`, `base64`, `json`, `os`

### `fixme/fixes.py` — Fix Execution

- `execute(cmd, admin)` — Runs shell commands via `subprocess`
- macOS admin elevation: `osascript -e 'do shell script "..." with administrator privileges'`
- Windows admin elevation: `ctypes.windll.shell32.ShellExecuteW` (UAC)
- `get_current_ssid()` — Detects current Wi-Fi network (macOS: `networksetup`, Windows: `netsh`)
- **Dependencies:** `ctypes`, `re`, `subprocess`, `time`

### `fixme/screenshot.py` — Screen Capture

- Uses `mss` library to capture primary monitor
- Saves to temp PNG file
- macOS: includes guidance for Screen Recording permission in System Settings
- **Dependencies:** `mss`, `os`, `tempfile`

### `fixme/tts.py` — Text-to-Speech

- ElevenLabs API for audio generation
- Claude for translation (non-English languages)
- macOS playback: `open` command with temp audio file
- Supported languages: English, Spanish, Punjabi, Hindi, French
- **Dependencies:** `anthropic`, `elevenlabs`, `os`, `tempfile`

### `fixme/conversation.py` — Conversation Flow

- Orchestrates a voice-driven ask-before-every-action permission loop
- Used by the legacy `app.py` system tray entry point
- **Dependencies:** `anthropic`, `fixme.voice_input`

### `fixme/recorder.py` — Screen Recording

- Captures frames via `mss` in a background thread
- Writes MP4 via OpenCV's `VideoWriter`
- **Dependencies:** `cv2`, `mss`, `numpy`, `threading`

## Legacy Modules (replaced by desktop app)

These modules are superseded by the Tauri + React desktop app but remain in the codebase for reference:

| Module | Replaced by |
| ------ | ----------- |
| `fixme/ui.py` | React components in `desktop/src/components/` |
| `fixme/voice_input.py` | Web Speech API via `useSpeechRecognition` hook |
| `fixme/overlay.py` | React DOM rendering in webview |
| `fixme/app.py` | Tauri window management in `desktop/src-tauri/` |

## Dependency Map

```
sidecar/main.py
  ├── fixme.screenshot ── mss
  ├── fixme.diagnose   ── anthropic (Claude Vision)
  ├── fixme.fixes      ── subprocess, ctypes
  ├── fixme.tts        ── anthropic, elevenlabs
  └── pyautogui        ── (click_at, type_text methods)
```
