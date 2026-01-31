# FixMe — Windows IT Issue Fixer

A Windows system tray app that screenshots your screen, diagnoses IT issues using Claude Vision, walks you through fixes with voice guidance (English/Spanish), and annotates your screen like a live tutorial.

## Features

- **Screenshot + AI Diagnosis** — Takes a screenshot and sends it to Claude Vision to identify IT issues
- **Voice-Guided Fixes** — Speaks each fix step aloud and asks permission before executing (ElevenLabs TTS)
- **Bilingual** — English and Spanish support for all voice interactions
- **Screen Annotations** — Transparent overlay highlights UI elements (circles, arrows, labels) during fixes
- **Screen Recording** — Optionally record the entire fix process as MP4
- **No action without permission** — Every step requires explicit user approval via voice or button

## Supported Fixes

| Issue | What it does |
|---|---|
| Wi-Fi problems | Toggle Wi-Fi off/on via `netsh wlan` |
| DNS issues | Flush DNS cache via `ipconfig /flushdns` |
| Network reset | Full disconnect + flush + release/renew cycle |
| Password/credentials | Open Windows Credential Manager |

## Setup

### 1. API Keys

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here
```

- **Anthropic**: https://console.anthropic.com
- **ElevenLabs**: https://elevenlabs.io (free tier available)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python fixme/app.py
```

A wrench icon appears in the system tray. Click it → "Diagnose Screen" to start.

## Build as .exe

```bash
pip install pyinstaller
pyinstaller fixme.spec
```

Output: `dist/FixMe.exe`. Place your `.env` file next to it.

## Project Structure

```
fixme/
├── fixme/
│   ├── app.py              # System tray entry point
│   ├── screenshot.py        # Screen capture (mss)
│   ├── diagnose.py          # Claude Vision diagnosis
│   ├── fixes.py             # Windows fix commands
│   ├── tts.py               # ElevenLabs TTS (English + Spanish)
│   ├── voice_input.py       # Windows SAPI speech recognition
│   ├── overlay.py           # Screen annotation overlay
│   ├── recorder.py          # Screen recording (OpenCV)
│   └── conversation.py      # Voice permission flow orchestrator
├── prompts/                 # PDD prompt files
├── assets/                  # App icon
├── requirements.txt
└── fixme.spec               # PyInstaller build config
```

## PDD (Prompt-Driven Development)

This project uses PDD for AI-powered code generation. Each module has a corresponding `.prompt` file in `prompts/` with YAML front matter.

```bash
pip install pdd
pdd setup
pdd sync screenshot
```

## Windows Permissions

- **Microphone**: Settings → Privacy → Microphone → Allow apps
- **Screen capture**: No special permissions needed
- **Admin commands** (DNS flush): UAC prompt will appear automatically
