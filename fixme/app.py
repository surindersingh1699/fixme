"""Windows system tray application - main entry point for FixMe."""

import os
import sys
import threading
import warnings

from dotenv import load_dotenv

# Load environment before any module imports that need API keys
load_dotenv()

from PIL import Image, ImageDraw, ImageFont

import pystray

from fixme import screenshot, diagnose, fixes, tts, voice_input
from fixme.conversation import ConversationFlow
from fixme.overlay import Overlay
from fixme.recorder import ScreenRecorder


class FixMeApp:
    """System tray application that wires all FixMe modules together."""

    def __init__(self):
        self.lang = "en"
        self.overlay = None
        self.recorder = ScreenRecorder(fps=10)
        self._diagnosing = False
        self._icon = None

    def _create_icon_image(self, color: str = "#4CAF50") -> Image.Image:
        """Create a tray icon image using Pillow.

        Args:
            color: Background color for the icon.

        Returns:
            A 64x64 PIL Image.
        """
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([4, 4, 60, 60], fill=color)
        try:
            font = ImageFont.truetype("segoeui.ttf", 30)
        except (IOError, OSError):
            font = ImageFont.load_default()
        draw.text((20, 12), "F", fill="white", font=font)
        return img

    def _build_menu(self) -> pystray.Menu:
        """Build the system tray menu."""
        return pystray.Menu(
            pystray.MenuItem("Diagnose Screen", self._on_diagnose),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Language",
                pystray.Menu(
                    pystray.MenuItem(
                        "English",
                        self._set_english,
                        checked=lambda item: self.lang == "en",
                    ),
                    pystray.MenuItem(
                        "Español",
                        self._set_spanish,
                        checked=lambda item: self.lang == "es",
                    ),
                ),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Screen Recording",
                pystray.Menu(
                    pystray.MenuItem("Start Recording", self._start_recording),
                    pystray.MenuItem("Stop Recording", self._stop_recording),
                ),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Quick Fixes",
                pystray.Menu(
                    pystray.MenuItem("Toggle Wi-Fi", self._quick_toggle_wifi),
                    pystray.MenuItem("Flush DNS", self._quick_flush_dns),
                ),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )

    def run(self):
        """Start the system tray application."""
        self._icon = pystray.Icon(
            name="FixMe",
            icon=self._create_icon_image(),
            title="FixMe - IT Issue Fixer",
            menu=self._build_menu(),
        )
        self._icon.run()

    def _set_english(self, icon, item):
        self.lang = "en"

    def _set_spanish(self, icon, item):
        self.lang = "es"

    def _on_diagnose(self, icon, item):
        """Handle 'Diagnose Screen' click."""
        if self._diagnosing:
            tts.speak("Diagnosis already in progress. Please wait.", self.lang)
            return

        self._diagnosing = True
        thread = threading.Thread(target=self._run_diagnosis, daemon=True)
        thread.start()

    def _run_diagnosis(self):
        """Run the full diagnosis flow in a background thread."""
        try:
            # Update icon to scanning state
            if self._icon:
                self._icon.icon = self._create_icon_image("#FFC107")

            # Initialize overlay
            self.overlay = Overlay()

            # Step 1: Screenshot
            tts.speak("Taking a screenshot to analyze your screen.", self.lang)
            image_path = screenshot.take_screenshot()

            # Step 2: Diagnose
            tts.speak("Analyzing the screenshot. Please wait.", self.lang)
            result = diagnose.diagnose_screenshot(image_path)

            # Step 3: Clean up screenshot
            try:
                os.unlink(image_path)
            except OSError:
                pass

            # Step 4: Run conversation flow
            conversation = ConversationFlow(
                lang=self.lang,
                tts=tts,
                voice_input_module=voice_input,
                overlay=self.overlay,
                fixes=fixes,
            )
            conversation.run_fix(result)

        except PermissionError as e:
            tts.speak(str(e), self.lang)
        except Exception as e:
            warnings.warn(f"Diagnosis failed: {e}")
            tts.speak(
                f"Sorry, the diagnosis failed: {e}",
                self.lang,
            )
        finally:
            self._diagnosing = False
            if self._icon:
                self._icon.icon = self._create_icon_image("#4CAF50")
            if self.overlay:
                self.overlay.destroy()
                self.overlay = None

    def _quick_toggle_wifi(self, icon, item):
        """Quick fix: toggle Wi-Fi with voice permission."""
        thread = threading.Thread(
            target=self._run_quick_fix,
            args=("toggle_wifi",),
            daemon=True,
        )
        thread.start()

    def _quick_flush_dns(self, icon, item):
        """Quick fix: flush DNS with voice permission."""
        thread = threading.Thread(
            target=self._run_quick_fix,
            args=("flush_dns",),
            daemon=True,
        )
        thread.start()

    def _run_quick_fix(self, fix_id: str):
        """Run a quick fix with voice permission."""
        available = fixes.get_available_fixes()
        fix = available.get(fix_id)
        if not fix:
            return

        try:
            self.overlay = Overlay()

            # Build a simple diagnosis result for the conversation flow
            steps = []
            ssid = fixes.get_current_ssid() or ""
            for i, cmd in enumerate(fix["commands"]):
                cmd_resolved = cmd.replace("{ssid}", ssid)
                steps.append({
                    "step": i + 1,
                    "description": f"{fix['label']} - {cmd_resolved}",
                    "command": cmd,
                    "needs_admin": fix["needs_admin"],
                    "ui_highlight": None,
                })

            result = {
                "diagnosis": f"Running quick fix: {fix['label']}",
                "steps": steps,
            }

            conversation = ConversationFlow(
                lang=self.lang,
                tts=tts,
                voice_input_module=voice_input,
                overlay=self.overlay,
                fixes=fixes,
            )
            conversation.run_fix(result)

        except Exception as e:
            tts.speak(f"Quick fix failed: {e}", self.lang)
        finally:
            if self.overlay:
                self.overlay.destroy()
                self.overlay = None

    def _start_recording(self, icon, item):
        """Start screen recording."""
        if self.recorder.is_recording:
            tts.speak("Already recording.", self.lang)
            return

        self.recorder.start()
        tts.speak("Screen recording started.", self.lang)

        if self.overlay:
            self.overlay.show_recording_indicator()

    def _stop_recording(self, icon, item):
        """Stop screen recording."""
        if not self.recorder.is_recording:
            tts.speak("No recording in progress.", self.lang)
            return

        output_path = self.recorder.stop()
        tts.speak(f"Recording saved to {output_path}.", self.lang)

        if self.overlay:
            self.overlay.hide_recording_indicator()

    def _on_quit(self, icon, item):
        """Quit the application."""
        if self.recorder.is_recording:
            self.recorder.stop()
        if self.overlay:
            self.overlay.destroy()
        icon.stop()


def main():
    """Entry point for the FixMe application."""
    # Validate API keys
    missing_keys = []
    if not os.environ.get("ANTHROPIC_API_KEY"):
        missing_keys.append("ANTHROPIC_API_KEY")
    if not os.environ.get("ELEVENLABS_API_KEY"):
        missing_keys.append("ELEVENLABS_API_KEY")

    if missing_keys:
        try:
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "FixMe - Setup Required",
                f"Missing API keys: {', '.join(missing_keys)}\n\n"
                "Create a .env file next to FixMe.exe with:\n"
                "ANTHROPIC_API_KEY=sk-ant-...\n"
                "ELEVENLABS_API_KEY=...",
            )
            root.destroy()
        except Exception:
            print(f"ERROR: Missing API keys: {', '.join(missing_keys)}")
            print("Create a .env file with ANTHROPIC_API_KEY and ELEVENLABS_API_KEY")
        sys.exit(1)

    app = FixMeApp()
    app.run()


if __name__ == "__main__":
    main()
