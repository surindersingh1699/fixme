"""Screen recording using mss frame capture and OpenCV MP4 encoding."""

import os
import threading
import time
import warnings
from datetime import datetime

import cv2
import mss
import numpy as np


class ScreenRecorder:
    """Records the primary monitor to an MP4 file."""

    def __init__(self, fps: int = 10):
        self.fps = fps
        self._recording = False
        self._thread = None
        self._output_path = None

    @property
    def is_recording(self) -> bool:
        """Whether recording is currently active."""
        return self._recording

    def start(self, output_path: str = None) -> None:
        """Start screen recording in a background thread.

        Args:
            output_path: Where to save the MP4. Defaults to Desktop.
        """
        if self._recording:
            return

        if output_path is None:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(desktop, f"FixMe_Recording_{timestamp}.mp4")

        self._output_path = output_path
        self._recording = True
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()

    def stop(self) -> str | None:
        """Stop recording and return the output file path.

        Returns:
            Path to the saved MP4 file, or None if not recording.
        """
        if not self._recording:
            return None

        self._recording = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

        return self._output_path

    def _record_loop(self):
        """Capture frames and write to video file."""
        try:
            sct = mss.mss()
            monitor = sct.monitors[1]  # Primary monitor
            width = monitor["width"]
            height = monitor["height"]

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(
                self._output_path, fourcc, self.fps, (width, height)
            )

            frame_interval = 1.0 / self.fps

            while self._recording:
                start_time = time.time()

                frame = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                writer.write(frame)

                # Maintain target FPS
                elapsed = time.time() - start_time
                sleep_time = frame_interval - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

            writer.release()

        except Exception as e:
            self._recording = False
            warnings.warn(f"Screen recording failed: {e}")
