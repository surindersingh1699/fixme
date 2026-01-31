"""Windows IT fix command execution with UAC elevation support."""

import ctypes
import re
import subprocess
import time

WIFI_DEVICE = "Wi-Fi"

FIXES = {
    "toggle_wifi": {
        "label": "Toggle Wi-Fi Off/On",
        "commands": [
            "netsh wlan disconnect",
            "WAIT:3",
            "netsh wlan connect name={ssid}",
        ],
        "needs_admin": False,
    },
    "flush_dns": {
        "label": "Flush DNS Cache",
        "commands": [
            "ipconfig /flushdns",
        ],
        "needs_admin": True,
    },
    "restart_network": {
        "label": "Full Network Reset",
        "commands": [
            "netsh wlan disconnect",
            "ipconfig /flushdns",
            "ipconfig /release",
            "ipconfig /renew",
            "WAIT:3",
            "netsh wlan connect name={ssid}",
        ],
        "needs_admin": True,
    },
    "open_credential_manager": {
        "label": "Open Credential Manager",
        "commands": [
            "rundll32.exe keymgr.dll,KRShowKeyMgr",
        ],
        "needs_admin": False,
    },
}


def get_current_ssid() -> str | None:
    """Detect the currently connected Wi-Fi SSID on Windows.

    Returns:
        The SSID string, or None if not connected or detection fails.
    """
    try:
        result = subprocess.run(
            "netsh wlan show interfaces",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            # Match "SSID" but not "BSSID"
            if re.match(r"^\s*SSID\s*:", line) or re.match(r"^SSID\s*:", line):
                return line.split(":", 1)[1].strip()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        pass
    return None


def execute(command: str, needs_admin: bool = False) -> tuple[bool, str]:
    """Execute a Windows command, optionally with UAC elevation.

    Args:
        command: The command string to run.
        needs_admin: Whether to request UAC elevation.

    Returns:
        Tuple of (success: bool, message: str).
    """
    # Handle special WAIT command
    if command.startswith("WAIT:"):
        try:
            seconds = int(command.split(":")[1])
            time.sleep(seconds)
            return True, f"Waited {seconds} seconds"
        except (ValueError, IndexError):
            return False, f"Invalid WAIT command: {command}"

    # Replace {ssid} placeholder
    if "{ssid}" in command:
        ssid = get_current_ssid()
        if ssid:
            command = command.replace("{ssid}", ssid)
        else:
            return False, "Could not detect Wi-Fi SSID. Make sure Wi-Fi is available."

    if needs_admin:
        try:
            # Use ShellExecuteW for UAC elevation
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", "cmd.exe", f"/c {command}", None, 0
            )
            # ShellExecuteW returns > 32 on success
            if ret > 32:
                return True, f"Executed with admin privileges: {command}"
            else:
                return False, f"UAC elevation failed (code {ret}) for: {command}"
        except AttributeError:
            # Not on Windows (no windll)
            return False, "UAC elevation is only available on Windows"
        except Exception as e:
            return False, f"Admin execution failed: {e}"
    else:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                output = result.stdout.strip() or "Command completed successfully"
                return True, output
            else:
                error = result.stderr.strip() or f"Command exited with code {result.returncode}"
                return False, error
        except subprocess.TimeoutExpired:
            return False, "Command timed out after 30 seconds"
        except subprocess.CalledProcessError as e:
            return False, f"Command failed: {e.stderr or str(e)}"


def get_available_fixes() -> dict:
    """Return the dictionary of available fixes."""
    return FIXES
