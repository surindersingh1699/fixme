# Python Sidecar

JSON-RPC server that reads requests from stdin and writes responses to stdout. Wraps existing `fixme` package modules without modifying them.

## Directory Structure

```
sidecar/
└── main.py    # JSON-RPC server wrapping fixme modules
```

## Protocol

Communication uses JSON-RPC 2.0 over stdin/stdout (one JSON object per line).

**Request format:**

```json
{"jsonrpc": "2.0", "id": 1, "method": "chat", "params": {"text": "my wifi is slow", "lang": "en"}}
```

**Response format:**

```json
{"jsonrpc": "2.0", "id": 1, "result": {"reply": "...", "commands": [...]}}
```

**Error format:**

```json
{"jsonrpc": "2.0", "id": 1, "error": {"code": -32000, "message": "error description"}}
```

## Available Methods

| Method | Params | Returns | Delegates to |
| ------ | ------ | ------- | ------------ |
| `chat` | `text`, `lang`, `history[]` | `{reply, commands[]}` | Claude API (`claude-sonnet-4-20250514`) |
| `diagnose` | -- | `{diagnosis, steps[]}` | `fixme.screenshot` + `fixme.diagnose` |
| `execute_step` | `command`, `admin` | `{success, message}` | `fixme.fixes.execute()` |
| `speak` | `text`, `lang` | `{ok: true}` | `fixme.tts.speak()` |
| `screenshot` | -- | `{path}` | `fixme.screenshot.take_screenshot()` |
| `click_at` | `x`, `y` | `{ok: true}` | `pyautogui.click()` |
| `type_text` | `text` | `{ok: true}` | `pyautogui.typewrite()` |
| `verify` | -- | `{diagnosis, steps[]}` | `fixme.screenshot` + `fixme.diagnose` |

## Chat Command Parsing

The `chat` method sends user text to Claude with a system prompt that instructs the model to return OS-native shell commands in a structured `commands` block:

```
description: What this does | command: the_shell_command | admin: false
description: Next step | command: another_command | admin: true
```

The sidecar parses this block and returns structured command objects alongside the display reply.

## Module Loading

Modules are loaded lazily on first use via `_get_module()` to keep startup fast. The sidecar adds the project root to `sys.path` and loads `.env` via `python-dotenv` on startup.

## Testing Standalone

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"chat","params":{"text":"hello","lang":"en"}}' | python sidecar/main.py
```
