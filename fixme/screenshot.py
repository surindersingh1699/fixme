"""Screen capture module using mss library for Windows."""

import os
import tempfile

import mss
import mss.tools


def take_screenshot() -> str:
    """Capture the primary monitor and return path to temporary PNG file.

    The caller is responsible for deleting the temporary file after use.

    Returns:
        Absolute path to the saved PNG file.

    Raises:
        RuntimeError: If mss fails to initialize.
        PermissionError: If the screenshot appears blank (likely a permissions issue).
    """
    try:
        sct = mss.mss()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize screen capture: {e}") from e

    monitor = sct.monitors[1]  # Primary monitor

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()

    try:
        screenshot = sct.grab(monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=tmp.name)
    except Exception as e:
        os.unlink(tmp.name)
        raise RuntimeError(f"Failed to capture screen: {e}") from e

    file_size = os.path.getsize(tmp.name)
    if file_size < 1000:
        os.unlink(tmp.name)
        raise PermissionError(
            "Screenshot appears blank. Check screen capture permissions. "
            "On macOS: System Settings → Privacy & Security → Screen Recording. "
            "On Windows: ensure no other app is blocking screen capture."
        )

    return tmp.name
