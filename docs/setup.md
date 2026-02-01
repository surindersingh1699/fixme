# Setup and Running

## Prerequisites

| Requirement | Version | Purpose |
| ----------- | ------- | ------- |
| Node.js | 20+ | Vite 7 requires Node 20+ (`nvm use 20`) |
| Rust | stable (1.70+) | Tauri v2 Rust backend |
| Python | 3.10+ | Sidecar + fixme modules |
| npm | 10+ | Frontend dependency management |

## API Keys

| Key | Service | Used by |
| --- | ------- | ------- |
| `ANTHROPIC_API_KEY` | Claude (Anthropic) | sidecar chat, diagnose, TTS translation |
| `ELEVENLABS_API_KEY` | ElevenLabs TTS | sidecar speak |

Store in `.env` at the project root. The sidecar loads these via `python-dotenv`.

## Initial Setup

### 1. Python environment

```bash
cd fixme
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Rust toolchain

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

### 3. Node.js (via nvm)

```bash
nvm install 20
nvm use 20
```

### 4. Desktop app dependencies

```bash
cd desktop
npm install
```

## Running the Desktop App

### Development

```bash
cd fixme/desktop
source "$HOME/.cargo/env"   # Ensure Rust/cargo is in PATH
nvm use 20                  # Node 20+ required for Vite 7
npx tauri dev               # Starts Vite + compiles Rust + launches app
```

This will:

1. Start Vite dev server on `http://localhost:1420` with HMR
2. Compile the Rust backend
3. Open the native app window
4. Spawn the Python sidecar automatically

### Production Build

```bash
cd fixme/desktop
source "$HOME/.cargo/env"
nvm use 20
npx tauri build
```

Output locations:

- **macOS:** `desktop/src-tauri/target/release/bundle/dmg/FixMe_1.0.0_aarch64.dmg`
- **Windows:** `desktop/src-tauri/target/release/bundle/msi/FixMe_1.0.0_x64.msi`

## Running the Landing Page

```bash
cd fixme/landing
npm install
npm run dev     # Development
npm run build   # Production build
```

## Running the Legacy Python UI (deprecated)

```bash
source venv/bin/activate
python -m fixme.ui
```

## Troubleshooting

### Port 1420 already in use

If Vite fails to start because port 1420 is occupied from a previous run:

```bash
lsof -ti:1420 | xargs kill -9
```

### `cargo` not found

Ensure Rust is in your PATH:

```bash
source "$HOME/.cargo/env"
```

### Node version too old for Vite 7

Vite 7 requires Node 20+. Switch with nvm:

```bash
nvm use 20
```

### Screen Recording permission (macOS)

The screenshot/diagnose feature requires Screen Recording permission. Go to System Settings > Privacy & Security > Screen Recording and enable the FixMe app.
