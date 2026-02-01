# FixMe — Architecture

## Overview

FixMe is an AI-powered IT support assistant that diagnoses and fixes common computer issues through screenshot analysis, voice interaction, and guided step-by-step remediation. It uses Claude (Anthropic) for vision-based diagnosis and conversational flow, ElevenLabs for multilingual text-to-speech, and a Tauri v2 + React desktop UI.

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  Tauri v2 Desktop Shell                   │
│                                                          │
│  ┌──────────────────────┐    ┌────────────────────────┐  │
│  │   React Frontend     │    │   Rust Backend          │  │
│  │   (System WebView)   │◄──►│   (Tauri Commands)      │  │
│  │                      │    │                          │  │
│  │  - Chat UI           │    │  - sidecar.rs            │  │
│  │  - Voice Orb         │    │    (process management)  │  │
│  │  - Permission Dialog │    │  - lib.rs                │  │
│  │  - Sidebar           │    │    (app setup + IPC)     │  │
│  └──────────────────────┘    └───────────┬──────────────┘  │
│                                          │                 │
└──────────────────────────────────────────┼─────────────────┘
                                           │ JSON-RPC
                                           │ (stdin/stdout)
                              ┌────────────▼──────────────┐
                              │   Python Sidecar           │
                              │   (sidecar/main.py)        │
                              │                            │
                              │  - fixme.diagnose          │
                              │  - fixme.fixes             │
                              │  - fixme.screenshot        │
                              │  - fixme.tts               │
                              └────────────────────────────┘
```

**Data flow:** React component calls `invoke("sidecar_call")` which hits the Rust Tauri command, writes JSON-RPC to the Python sidecar's stdin, the Python handler executes and writes the response to stdout, Rust reads it and resolves back to the React frontend.

## Project Structure

```
fixme/
├── fixme/              # Core Python package (used by sidecar)
├── desktop/            # Tauri v2 + React desktop app
│   ├── src/            # React components, hooks, styles
│   └── src-tauri/      # Rust backend (sidecar bridge, app config)
├── sidecar/            # Python JSON-RPC server
│   └── main.py
├── landing/            # React landing page (Vercel)
├── docs/               # Detailed documentation (see below)
├── prompts/            # PDD prompt files
├── requirements.txt    # Python dependencies
├── .env                # API keys (not committed)
└── architecture.md     # This file
```

## Documentation

Detailed documentation for each part of the project:

- **[Desktop App](docs/desktop-app.md)** — Tauri v2 + React frontend, Rust backend, components, hooks, state flow, configuration
- **[Python Sidecar](docs/sidecar.md)** — JSON-RPC protocol, available methods, command parsing
- **[Python Modules](docs/python-modules.md)** — Core `fixme` package: diagnose, fixes, screenshot, TTS, legacy modules
- **[Landing Page](docs/landing-page.md)** — React + Vite + Tailwind marketing site
- **[Setup and Running](docs/setup.md)** — Prerequisites, installation, dev/production commands, troubleshooting

## Key Design Decisions

| Decision | Rationale |
| -------- | --------- |
| Tauri v2 over Electron | ~10MB bundle (uses system webview) vs ~150MB Electron |
| Python sidecar over rewriting in Rust | Existing `fixme` modules work. Claude/ElevenLabs Python SDKs are mature. Zero changes to backend logic. |
| JSON-RPC over stdin/stdout | Simple, no networking, no port conflicts. Sidecar dies with the app. |
| Web Speech API over SAPI | Works cross-platform in webview. Falls back to text input on unsupported platforms. |
| localStorage for history | Simple, no database. Sufficient for chat session persistence. |
| React 19 + Tailwind 4 | Matches landing page stack. Consistent design system. |

## API Keys Required

| Key | Service | Used by |
| --- | ------- | ------- |
| `ANTHROPIC_API_KEY` | Claude (Anthropic) | sidecar chat, diagnose, TTS translation |
| `ELEVENLABS_API_KEY` | ElevenLabs TTS | sidecar speak |

## Quick Start

```bash
cd fixme/desktop
source "$HOME/.cargo/env"
nvm use 20
npx tauri dev
```

See [Setup and Running](docs/setup.md) for full instructions.
