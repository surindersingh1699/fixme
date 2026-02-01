# Desktop App — Tauri v2 + React

## Tech Stack

| Layer | Technology | Purpose |
| ----- | ---------- | ------- |
| Frontend | React 19 + Tailwind CSS 4 | UI components, styling |
| Bundler | Vite 7 | Dev server, HMR, production build |
| Desktop shell | Tauri v2 (Rust) | Native window, IPC, process management |
| Backend | Python sidecar | AI diagnosis, command execution, TTS |
| Voice | Web Speech API | Browser-native speech recognition |

## Directory Structure

```
desktop/
├── src/
│   ├── components/
│   │   ├── ChatArea.jsx            # Scrollable message list with auto-scroll
│   │   ├── ChatBubble.jsx          # User/assistant message bubbles
│   │   ├── InputBar.jsx            # Text input + Diagnose + Screenshot buttons
│   │   ├── PermissionDialog.jsx    # Yes/No/Skip modal for fix steps
│   │   ├── Sidebar.jsx             # Session list, language selector, logo
│   │   ├── StatusBadge.jsx         # Status indicator pill (Ready/Thinking/etc)
│   │   ├── StepCard.jsx            # Fix step progress card
│   │   ├── VoiceInputDialog.jsx    # Text input fallback (Speech API unavailable)
│   │   └── VoiceOrb.jsx            # Animated SVG orb (idle/listening/processing)
│   ├── hooks/
│   │   ├── useSidecar.js           # Tauri invoke wrapper for Python sidecar
│   │   ├── useHistory.js           # localStorage chat history management
│   │   └── useSpeechRecognition.js # Web Speech API wrapper
│   ├── lib/
│   │   └── tokens.js               # Design tokens (colors, fonts)
│   ├── App.jsx                     # Main app — state, handlers, layout
│   ├── main.jsx                    # React root mount
│   └── index.css                   # Tailwind imports + dark theme + scrollbar
├── src-tauri/
│   ├── src/
│   │   ├── main.rs                 # Rust entry point
│   │   ├── lib.rs                  # Tauri setup, sidecar spawn, command registration
│   │   └── sidecar.rs              # Python process management + JSON-RPC bridge
│   ├── capabilities/
│   │   └── default.json            # Tauri permission grants
│   ├── icons/                      # App icons (32x32, 128x128, icns, ico)
│   ├── Cargo.toml                  # Rust dependencies
│   ├── tauri.conf.json             # App window config, CSP, plugins
│   └── build.rs                    # Tauri build script
├── index.html                      # HTML shell with Inter font
├── package.json                    # React + Tailwind + Tauri deps
└── vite.config.js                  # Vite + React + Tailwind plugins
```

---

## Rust Backend (`src-tauri/`)

### `sidecar.rs` — Python Process Manager

Manages the Python sidecar as a child process with JSON-RPC communication over stdin/stdout.

**Key types:**

- `PendingMap = Arc<Mutex<HashMap<u64, oneshot::Sender<Value>>>>` — Thread-safe map of in-flight request IDs to response channels
- `Sidecar` struct — Holds child process handle, stdin writer, pending map, atomic request ID counter

**Lifecycle:**

1. `spawn()` — Starts `python3 sidecar/main.py`, captures stdin/stdout, spawns reader thread
2. Reader thread — Loops over stdout lines, parses JSON-RPC responses, resolves matching pending request by ID
3. `call()` — Assigns incremented ID, writes JSON-RPC request to stdin, awaits oneshot channel for response
4. `kill()` / `Drop` — Terminates child process on app exit

### `lib.rs` — Tauri App Setup

- Registers the `sidecar_call` Tauri command
- On setup: walks up directory tree to find `sidecar/main.py`
- Prefers venv Python (`venv/bin/python3` on macOS, `venv/Scripts/python.exe` on Windows)
- Falls back to system `python3`
- Manages sidecar as Tauri app state via `Arc<Sidecar>`

**Tauri command:**

```rust
#[tauri::command]
async fn sidecar_call(method: String, params: Value, state: State<'_, Arc<Sidecar>>)
    -> Result<Value, String>
```

---

## React Frontend (`src/`)

### Components

| Component | Description |
| --------- | ----------- |
| `App.jsx` | Root component. Manages all state (session, chat items, status, busy, orb state, dialogs). Contains handlers for send, diagnose, screenshot, voice, and fix step execution. |
| `Sidebar.jsx` | Left panel (220px). Shows FixMe logo, "New Chat" button, session history list, and language selector (EN/ES/PA/HI/FR). |
| `ChatArea.jsx` | Scrollable message container with auto-scroll to bottom on new messages. Renders `ChatBubble` and `StepCard` items. |
| `ChatBubble.jsx` | Individual message bubble. User messages: indigo-600, right-aligned. Assistant messages: zinc-900, left-aligned. |
| `InputBar.jsx` | Bottom bar with text input, send button, "Diagnose Screen" button, and "Screenshot" button. Disabled when busy. |
| `VoiceOrb.jsx` | Centered animated SVG orb. States: idle (mic icon), listening (bouncing bars), processing (bouncing dots), success (checkmark), error (X). |
| `StepCard.jsx` | Fix step progress indicator. Shows step number, description, and status (pending/running/done/failed/skipped) with colored badges. |
| `PermissionDialog.jsx` | Modal overlay with backdrop blur. Shows step description and command. Three buttons: Yes (indigo), Skip (zinc), No - Stop (red). |
| `VoiceInputDialog.jsx` | Fallback text input modal when Web Speech API is unavailable (e.g., Tauri WKWebView on macOS). Localized prompt in 5 languages. |
| `StatusBadge.jsx` | Small pill in the top bar showing current status (Ready, Thinking, Diagnosing, etc.) with colored dot indicator. |

### Hooks

| Hook | Description |
| ---- | ----------- |
| `useSidecar()` | Returns `{ call }` function that wraps `invoke("sidecar_call", { method, params })`. All Python backend communication goes through this. |
| `useHistory()` | localStorage-based session management. Returns `{ sessions, newSession, addMessage, getSession }`. Session titles auto-update from first user message. |
| `useSpeechRecognition()` | Web Speech API wrapper. Returns `{ isListening, transcript, startListening, stopListening }`. Supports language switching via BCP 47 locale codes. Returns `false` from `startListening()` when API unavailable. |

---

## App State Flow

### Chat Flow

```
User types message -> handleSend()
  -> setBusy(true), setOrbState("processing")
  -> addChatItem(user message)
  -> useSidecar.call("chat", {text, lang, history})
  -> addChatItem(assistant reply)
  -> If commands returned -> runFixSteps(commands)
    -> For each step:
      -> askPermission() -> show PermissionDialog -> wait for user response
      -> If "yes" -> useSidecar.call("execute_step", {command, admin})
      -> If "no" -> break loop
      -> If "skip" -> continue
    -> After all steps -> useSidecar.call("verify") -> re-diagnose
  -> setBusy(false), setOrbState("idle")
```

### Diagnose Flow

```
User clicks Diagnose -> handleDiagnose()
  -> useSidecar.call("diagnose")
  -> Returns {diagnosis, steps[]}
  -> If steps exist -> runFixSteps(steps) (same permission flow as above)
```

### Voice Flow

```
User clicks Voice Orb -> handleVoiceClick()
  -> startListening(lang)
  -> If Speech API available: orb enters "listening" state
  -> If not available: show VoiceInputDialog (text fallback)
  -> On transcript/submit -> handleSend(text)
```

---

## Tauri Configuration

| Setting | Value |
| ------- | ----- |
| Window size | 880 x 680 (min 680 x 480) |
| Window position | Centered |
| Dev URL | `http://localhost:1420` |
| CSP | `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:` |
| Plugins | `shell` (open URLs), `fs` (file access) |
