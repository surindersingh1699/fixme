"""FixMe Python sidecar — JSON-RPC server over stdin/stdout.

Wraps existing fixme modules for Tauri IPC.
"""

import json
import os
import sys
import traceback

# Add project root to path so we can import fixme package
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, ".env"))

# Lazy imports to avoid loading everything at startup
_modules = {}

def _get_module(name):
    if name not in _modules:
        if name == "screenshot":
            from fixme import screenshot
            _modules[name] = screenshot
        elif name == "diagnose":
            from fixme import diagnose
            _modules[name] = diagnose
        elif name == "fixes":
            from fixme import fixes
            _modules[name] = fixes
        elif name == "tts":
            from fixme import tts
            _modules[name] = tts
        elif name == "anthropic":
            import anthropic
            _modules[name] = anthropic
    return _modules.get(name)


def handle_chat(params):
    """Send user text to Claude and return response with optional commands."""
    anthropic = _get_module("anthropic")
    text = params.get("text", "")
    lang = params.get("lang", "en")
    history = params.get("history", [])

    _is_mac = sys.platform == "darwin"
    _os = "macOS" if _is_mac else "Windows"
    names = {"en": "English", "es": "Spanish", "pa": "Punjabi",
             "hi": "Hindi", "fr": "French"}

    system_prompt = (
        f"You are FixMe, an IT support assistant running on {_os}. "
        f"Respond in {names.get(lang, 'English')}. "
        "When the user describes a computer problem, diagnose it and provide "
        f"actionable {_os} terminal commands to fix it.\n\n"
        "If commands are needed, end your response with a COMMANDS block:\n"
        "```commands\n"
        "description: What this does | command: the_shell_command | admin: false\n"
        "description: Next step | command: another_command | admin: true\n"
        "```\n\n"
        f"Use {_os}-native commands:\n"
        + ("- networksetup for Wi-Fi, dscacheutil/killall mDNSResponder for DNS\n"
           "- open -a 'App Name' to launch apps, defaults for settings\n"
           "- pmset for power, diskutil for disks, system_profiler for info\n"
           if _is_mac else
           "- netsh for Wi-Fi, ipconfig for DNS/network\n"
           "- rundll32 for credential manager\n")
        + "\nIf the issue is conversational (greetings, questions about you, etc.), "
        "just respond naturally without a commands block. "
        "Be concise and empathetic."
    )

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["text"]})
    messages.append({"role": "user", "content": text})

    m = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    reply = m.content[0].text.strip()

    # Parse commands block
    commands = []
    display_reply = reply
    if "```commands" in reply:
        parts = reply.split("```commands")
        display_reply = parts[0].strip()
        cmd_block = parts[1].split("```")[0].strip()
        for line in cmd_block.splitlines():
            line = line.strip()
            if not line or "description:" not in line:
                continue
            desc = cmd = ""
            admin = False
            for part in line.split("|"):
                part = part.strip()
                if part.startswith("description:"):
                    desc = part[len("description:"):].strip()
                elif part.startswith("command:"):
                    cmd = part[len("command:"):].strip()
                elif part.startswith("admin:"):
                    admin = part[len("admin:"):].strip().lower() == "true"
            if desc and cmd:
                commands.append({"description": desc, "command": cmd, "needs_admin": admin})

    return {
        "reply": display_reply,
        "commands": commands,
    }


def handle_diagnose(params):
    """Capture screenshot, analyze with Claude Vision, return diagnosis."""
    screenshot = _get_module("screenshot")
    diagnose = _get_module("diagnose")

    img_path = screenshot.take_screenshot()
    try:
        result = diagnose.diagnose_screenshot(img_path)
    finally:
        try:
            os.unlink(img_path)
        except OSError:
            pass
    return result


def handle_execute_step(params):
    """Execute a single command."""
    fixes = _get_module("fixes")
    command = params.get("command", "")
    admin = params.get("admin", False)
    ok, msg = fixes.execute(command, admin)
    return {"success": ok, "message": msg}


def handle_speak(params):
    """Text-to-speech via ElevenLabs."""
    tts = _get_module("tts")
    text = params.get("text", "")
    lang = params.get("lang", "en")
    tts.speak(text, lang)
    return {"ok": True}


def handle_screenshot(params):
    """Take a screenshot and return the file path."""
    screenshot = _get_module("screenshot")
    path = screenshot.take_screenshot()
    return {"path": path}


def handle_click_at(params):
    """Click at screen coordinates using pyautogui."""
    import pyautogui
    pyautogui.FAILSAFE = True
    x = params.get("x", 0)
    y = params.get("y", 0)
    pyautogui.click(x, y)
    return {"ok": True}


def handle_type_text(params):
    """Type text using pyautogui."""
    import pyautogui
    pyautogui.FAILSAFE = True
    text = params.get("text", "")
    pyautogui.typewrite(text, interval=0.03)
    return {"ok": True}


def handle_verify(params):
    """Take a verification screenshot and re-diagnose."""
    screenshot = _get_module("screenshot")
    diagnose = _get_module("diagnose")

    img_path = screenshot.take_screenshot()
    try:
        result = diagnose.diagnose_screenshot(img_path)
    finally:
        try:
            os.unlink(img_path)
        except OSError:
            pass
    return result


HANDLERS = {
    "chat": handle_chat,
    "diagnose": handle_diagnose,
    "execute_step": handle_execute_step,
    "speak": handle_speak,
    "screenshot": handle_screenshot,
    "click_at": handle_click_at,
    "type_text": handle_type_text,
    "verify": handle_verify,
}


def main():
    """Main loop: read JSON-RPC requests from stdin, dispatch, write responses."""
    # Signal readiness
    sys.stderr.write("[FixMe Sidecar] Ready\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except json.JSONDecodeError as e:
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
            continue

        req_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params", {})

        handler = HANDLERS.get(method)
        if not handler:
            resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}
        else:
            try:
                result = handler(params)
                resp = {"jsonrpc": "2.0", "id": req_id, "result": result}
            except Exception as e:
                traceback.print_exc(file=sys.stderr)
                resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}

        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
