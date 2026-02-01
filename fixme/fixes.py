"""Cross-platform IT fix command execution (macOS + Windows)."""

import re
import subprocess
import sys
import time

_IS_MAC = sys.platform == "darwin"

# ── macOS fixes ───────────────────────────────────────────────────────────────

MAC_FIXES = {
    "toggle_wifi": {
        "label": "Toggle Wi-Fi Off/On",
        "commands": [
            "networksetup -setairportpower en0 off",
            "WAIT:3",
            "networksetup -setairportpower en0 on",
        ],
        "needs_admin": False,
    },
    "flush_dns": {
        "label": "Flush DNS Cache",
        "commands": [
            "sudo dscacheutil -flushcache",
            "sudo killall -HUP mDNSResponder",
        ],
        "needs_admin": True,
    },
    "restart_network": {
        "label": "Full Network Reset",
        "commands": [
            "networksetup -setairportpower en0 off",
            "sudo dscacheutil -flushcache",
            "sudo killall -HUP mDNSResponder",
            "WAIT:3",
            "networksetup -setairportpower en0 on",
        ],
        "needs_admin": True,
    },
    "open_credential_manager": {
        "label": "Open Keychain Access",
        "commands": [
            "open -a 'Keychain Access'",
        ],
        "needs_admin": False,
    },
}

# ── Windows fixes ─────────────────────────────────────────────────────────────

WIN_FIXES = {
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

FIXES = MAC_FIXES if _IS_MAC else WIN_FIXES


def get_current_ssid() -> str | None:
    """Detect the currently connected Wi-Fi SSID."""
    try:
        if _IS_MAC:
            # Try networksetup first
            result = subprocess.run(
                ["networksetup", "-getairportnetwork", "en0"],
                capture_output=True, text=True, timeout=10,
            )
            if ":" in result.stdout and "not associated" not in result.stdout.lower():
                return result.stdout.split(":", 1)[1].strip()
            # Fallback: system_profiler for newer macOS
            result = subprocess.run(
                ["system_profiler", "SPAirPortDataType"],
                capture_output=True, text=True, timeout=15,
            )
            lines = result.stdout.splitlines()
            for i, line in enumerate(lines):
                if "Current Network Information:" in line and i + 1 < len(lines):
                    ssid_line = lines[i + 1].strip().rstrip(":")
                    if ssid_line and ssid_line != "Network Type":
                        return ssid_line
        else:
            result = subprocess.run(
                "netsh wlan show interfaces",
                shell=True, capture_output=True, text=True, timeout=10,
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if re.match(r"^\s*SSID\s*:", line) or re.match(r"^SSID\s*:", line):
                    return line.split(":", 1)[1].strip()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        pass
    return None


def execute(command: str, needs_admin: bool = False) -> tuple[bool, str]:
    """Execute a shell command, with platform-appropriate admin handling.

    Args:
        command: The command string to run.
        needs_admin: Whether the command requires elevated privileges.

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

    if needs_admin and _IS_MAC:
        # On macOS, use osascript to prompt for admin password
        # Strip 'sudo ' prefix if present since osascript handles elevation
        clean_cmd = command.replace("sudo ", "", 1) if command.startswith("sudo ") else command
        try:
            apple_script = (
                f'do shell script "{clean_cmd}" '
                f'with administrator privileges'
            )
            result = subprocess.run(
                ["osascript", "-e", apple_script],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                output = result.stdout.strip() or "Command completed successfully"
                return True, output
            else:
                error = result.stderr.strip() or f"Command exited with code {result.returncode}"
                return False, error
        except subprocess.TimeoutExpired:
            return False, "Command timed out after 30 seconds"
        except Exception as e:
            return False, f"Admin execution failed: {e}"
    elif needs_admin and not _IS_MAC:
        # Windows UAC elevation
        try:
            import ctypes
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", "cmd.exe", f"/c {command}", None, 0
            )
            if ret > 32:
                return True, f"Executed with admin privileges: {command}"
            else:
                return False, f"UAC elevation failed (code {ret}) for: {command}"
        except AttributeError:
            return False, "UAC elevation is only available on Windows"
        except Exception as e:
            return False, f"Admin execution failed: {e}"
    else:
        try:
            result = subprocess.run(
                command, shell=True,
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                output = result.stdout.strip() or "Command completed successfully"
                return True, output
            else:
                error = result.stderr.strip() or f"Command exited with code {result.returncode}"
                return False, error
        except subprocess.TimeoutExpired:
            return False, "Command timed out after 30 seconds"
        except Exception as e:
            return False, f"Command failed: {e}"


def get_available_fixes() -> dict:
    """Return the dictionary of available fixes for the current platform."""
    return FIXES
