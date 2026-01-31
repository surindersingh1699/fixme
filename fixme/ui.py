"""Modern desktop UI for FixMe — Apple-inspired design with Siri-like voice button."""

import os
import sys
import math
import threading
import time
import warnings
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

import customtkinter as ctk
from PIL import Image, ImageDraw

from fixme import screenshot, diagnose, fixes, tts, voice_input
from fixme.conversation import ConversationFlow
from fixme.overlay import Overlay
from fixme.recorder import ScreenRecorder


# ─── Theme ───────────────────────────────────────────────────────────────────

COLORS = {
    "bg": "#0A0A0A",
    "surface": "#1A1A1A",
    "surface_hover": "#252525",
    "border": "#2A2A2A",
    "text": "#FAFAFA",
    "text_secondary": "#8E8E93",
    "accent": "#007AFF",
    "accent_hover": "#0056CC",
    "green": "#30D158",
    "orange": "#FF9F0A",
    "red": "#FF453A",
    "purple": "#BF5AF2",
    "voice_ring_1": "#007AFF",
    "voice_ring_2": "#5856D6",
    "voice_ring_3": "#AF52DE",
    "chat_user": "#1C1C1E",
    "chat_assistant": "#007AFF",
}

FONT_FAMILY = "SF Pro Display" if sys.platform == "darwin" else "Segoe UI"


# ─── Animated Voice Button ───────────────────────────────────────────────────

class VoiceButton(ctk.CTkCanvas):
    """Large animated Siri-like voice button with pulsing rings."""

    SIZE = 180
    INNER_R = 55

    def __init__(self, master, command=None, **kwargs):
        super().__init__(
            master,
            width=self.SIZE,
            height=self.SIZE,
            bg=COLORS["bg"],
            highlightthickness=0,
            **kwargs,
        )
        self._command = command
        self._state = "idle"  # idle | listening | processing | success | error
        self._pulse_phase = 0.0
        self._animating = False
        self._rings = []

        self.bind("<Button-1>", self._on_click)
        self._draw_idle()

    def _on_click(self, event):
        cx, cy = self.SIZE / 2, self.SIZE / 2
        dx, dy = event.x - cx, event.y - cy
        if math.sqrt(dx * dx + dy * dy) <= self.INNER_R + 10:
            if self._command:
                self._command()

    def set_state(self, state: str):
        self._state = state
        if state in ("listening", "processing"):
            self._start_animation()
        else:
            self._stop_animation()
            self._draw_static()

    def _start_animation(self):
        if not self._animating:
            self._animating = True
            self._animate()

    def _stop_animation(self):
        self._animating = False

    def _animate(self):
        if not self._animating:
            return
        self._pulse_phase += 0.08
        self._draw_animated()
        self.after(30, self._animate)

    def _draw_idle(self):
        self.delete("all")
        cx, cy = self.SIZE / 2, self.SIZE / 2
        r = self.INNER_R

        # Subtle outer glow
        for i in range(3):
            offset = (3 - i) * 8
            alpha_hex = format(int(20 + i * 10), "02x")
            color = COLORS["accent"] + alpha_hex if len(COLORS["accent"]) == 7 else COLORS["accent"]
            self.create_oval(
                cx - r - offset, cy - r - offset,
                cx + r + offset, cy + r + offset,
                outline=COLORS["voice_ring_1"], width=1, stipple="gray25",
            )

        # Main circle
        self.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=COLORS["accent"], outline="",
        )

        # Mic icon (simplified)
        self._draw_mic_icon(cx, cy, "white")

    def _draw_animated(self):
        self.delete("all")
        cx, cy = self.SIZE / 2, self.SIZE / 2
        r = self.INNER_R
        phase = self._pulse_phase

        ring_colors = [COLORS["voice_ring_1"], COLORS["voice_ring_2"], COLORS["voice_ring_3"]]

        # Pulsing rings
        for i in range(3):
            pulse = math.sin(phase + i * 0.7) * 0.5 + 0.5
            ring_r = r + 15 + i * 12 + pulse * 8
            width = 2.0 + pulse * 1.5
            self.create_oval(
                cx - ring_r, cy - ring_r,
                cx + ring_r, cy + ring_r,
                outline=ring_colors[i % 3], width=width,
            )

        # Main circle with slight scale pulse
        scale = 1.0 + math.sin(phase * 1.5) * 0.03
        sr = r * scale
        fill = COLORS["accent"] if self._state == "listening" else COLORS["purple"]
        self.create_oval(
            cx - sr, cy - sr, cx + sr, cy + sr,
            fill=fill, outline="",
        )

        # Icon
        if self._state == "listening":
            self._draw_mic_icon(cx, cy, "white")
        else:
            self._draw_dots(cx, cy, phase)

    def _draw_static(self):
        self.delete("all")
        cx, cy = self.SIZE / 2, self.SIZE / 2
        r = self.INNER_R

        if self._state == "success":
            self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=COLORS["green"], outline="")
            self.create_text(cx, cy, text="✓", fill="white", font=(FONT_FAMILY, 36, "bold"))
        elif self._state == "error":
            self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=COLORS["red"], outline="")
            self.create_text(cx, cy, text="✕", fill="white", font=(FONT_FAMILY, 36, "bold"))
        else:
            self._draw_idle()

    def _draw_mic_icon(self, cx, cy, color):
        # Mic body
        self.create_rounded_rectangle(cx - 8, cy - 22, cx + 8, cy + 2, radius=8, fill=color, outline="")
        # Mic arc
        self.create_arc(cx - 16, cy - 18, cx + 16, cy + 14, start=180, extent=180, style="arc", outline=color, width=2.5)
        # Mic stand
        self.create_line(cx, cy + 14, cx, cy + 22, fill=color, width=2.5)
        self.create_line(cx - 8, cy + 22, cx + 8, cy + 22, fill=color, width=2.5)

    def _draw_dots(self, cx, cy, phase):
        for i in range(3):
            offset = (i - 1) * 14
            bounce = math.sin(phase * 2 + i * 0.8) * 4
            self.create_oval(
                cx + offset - 4, cy + bounce - 4,
                cx + offset + 4, cy + bounce + 4,
                fill="white", outline="",
            )

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
        points = [
            x1 + radius, y1, x2 - radius, y1,
            x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2,
            x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius,
            x1, y1 + radius, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)


# ─── Chat Message Bubble ────────────────────────────────────────────────────

class ChatBubble(ctk.CTkFrame):
    """Single chat message bubble."""

    def __init__(self, master, text: str, role: str = "assistant", **kwargs):
        is_user = role == "user"
        super().__init__(
            master,
            fg_color=COLORS["chat_user"] if is_user else COLORS["chat_assistant"],
            corner_radius=16,
            **kwargs,
        )

        label = ctk.CTkLabel(
            self,
            text=text,
            text_color="white",
            font=(FONT_FAMILY, 13),
            wraplength=340,
            justify="left",
            anchor="w",
        )
        label.pack(padx=14, pady=10)


# ─── Status Indicator ────────────────────────────────────────────────────────

class StatusBar(ctk.CTkFrame):
    """Top status bar showing connection and recording status."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["surface"], height=36, corner_radius=0, **kwargs)
        self.pack_propagate(False)

        self._status_dot = ctk.CTkLabel(
            self, text="●", text_color=COLORS["green"],
            font=(FONT_FAMILY, 10), width=20,
        )
        self._status_dot.pack(side="left", padx=(12, 4), pady=6)

        self._status_text = ctk.CTkLabel(
            self, text="Ready", text_color=COLORS["text_secondary"],
            font=(FONT_FAMILY, 11),
        )
        self._status_text.pack(side="left", pady=6)

        self._rec_label = ctk.CTkLabel(
            self, text="", text_color=COLORS["red"],
            font=(FONT_FAMILY, 11, "bold"),
        )
        self._rec_label.pack(side="right", padx=12, pady=6)

    def set_status(self, text: str, color: str = None):
        self._status_text.configure(text=text)
        if color:
            self._status_dot.configure(text_color=color)

    def set_recording(self, active: bool):
        self._rec_label.configure(text="● REC" if active else "")


# ─── Main Application ────────────────────────────────────────────────────────

class FixMeUI(ctk.CTk):
    """Main FixMe desktop application with modern UI."""

    WIDTH = 440
    HEIGHT = 720

    def __init__(self):
        super().__init__()

        # Window setup
        self.title("FixMe")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(400, 600)
        self.configure(fg_color=COLORS["bg"])
        self.resizable(True, True)

        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.WIDTH) // 2
        y = (self.winfo_screenheight() - self.HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

        # State
        self.lang = "en"
        self.overlay = None
        self.recorder = ScreenRecorder(fps=10)
        self._diagnosing = False
        self._messages = []

        # Build UI
        self._build_ui()

        # Welcome message
        self.after(500, lambda: self._add_message(
            "Hi! I'm FixMe. Tap the mic to describe your issue, "
            "or use the buttons below to diagnose your screen.",
            "assistant",
        ))

    def _build_ui(self):
        # ── Status bar ──
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill="x")

        # ── Separator ──
        ctk.CTkFrame(self, fg_color=COLORS["border"], height=1).pack(fill="x")

        # ── Chat area (scrollable) ──
        self._chat_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["surface"],
            scrollbar_button_hover_color=COLORS["surface_hover"],
        )
        self._chat_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # ── Voice button area ──
        voice_area = ctk.CTkFrame(self, fg_color=COLORS["bg"], height=220)
        voice_area.pack(fill="x")
        voice_area.pack_propagate(False)

        # Siri-like voice button
        self.voice_btn = VoiceButton(voice_area, command=self._on_voice_tap)
        self.voice_btn.pack(pady=(15, 5))

        # State label under button
        self._voice_label = ctk.CTkLabel(
            voice_area,
            text="Tap to speak",
            text_color=COLORS["text_secondary"],
            font=(FONT_FAMILY, 12),
        )
        self._voice_label.pack(pady=(0, 10))

        # ── Separator ──
        ctk.CTkFrame(self, fg_color=COLORS["border"], height=1).pack(fill="x")

        # ── Bottom action bar ──
        bottom_bar = ctk.CTkFrame(self, fg_color=COLORS["surface"], height=110, corner_radius=0)
        bottom_bar.pack(fill="x", side="bottom")
        bottom_bar.pack_propagate(False)

        # Text input row
        input_row = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        input_row.pack(fill="x", padx=12, pady=(10, 6))

        self._text_input = ctk.CTkEntry(
            input_row,
            placeholder_text="Type a message or describe your issue...",
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_secondary"],
            font=(FONT_FAMILY, 13),
            height=38,
            corner_radius=19,
        )
        self._text_input.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._text_input.bind("<Return>", self._on_text_submit)

        send_btn = ctk.CTkButton(
            input_row,
            text="↑",
            width=38,
            height=38,
            corner_radius=19,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=(FONT_FAMILY, 18, "bold"),
            command=self._on_text_submit,
        )
        send_btn.pack(side="right")

        # Action buttons row
        btn_row = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(0, 10))

        self._diagnose_btn = ctk.CTkButton(
            btn_row,
            text="🔍  Diagnose Screen",
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=(FONT_FAMILY, 12, "bold"),
            height=34,
            corner_radius=17,
            command=self._on_diagnose,
        )
        self._diagnose_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self._screenshot_btn = ctk.CTkButton(
            btn_row,
            text="📷  Screenshot",
            fg_color=COLORS["surface_hover"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=(FONT_FAMILY, 12),
            height=34,
            corner_radius=17,
            command=self._on_screenshot,
        )
        self._screenshot_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))

    # ── Chat Methods ──────────────────────────────────────────────────────────

    def _add_message(self, text: str, role: str = "assistant"):
        """Add a message bubble to the chat."""
        self._messages.append({"text": text, "role": role, "time": datetime.now()})

        # Container for alignment
        container = ctk.CTkFrame(self._chat_frame, fg_color="transparent")
        container.pack(fill="x", padx=12, pady=4)

        bubble = ChatBubble(container, text=text, role=role)

        if role == "user":
            bubble.pack(anchor="e", padx=(40, 0))
        else:
            bubble.pack(anchor="w", padx=(0, 40))

        # Auto-scroll to bottom
        self._chat_frame.after(50, lambda: self._chat_frame._parent_canvas.yview_moveto(1.0))

    def _add_step_message(self, step_num: int, total: int, description: str, status: str = "pending"):
        """Add a step progress message."""
        icons = {"pending": "○", "running": "◉", "done": "✓", "failed": "✕", "skipped": "◌"}
        colors = {"pending": COLORS["text_secondary"], "running": COLORS["orange"],
                  "done": COLORS["green"], "failed": COLORS["red"], "skipped": COLORS["text_secondary"]}

        icon = icons.get(status, "○")
        text = f"{icon}  Step {step_num}/{total}: {description}"

        container = ctk.CTkFrame(self._chat_frame, fg_color="transparent")
        container.pack(fill="x", padx=12, pady=2)

        label = ctk.CTkLabel(
            container,
            text=text,
            text_color=colors.get(status, COLORS["text"]),
            font=(FONT_FAMILY, 12),
            anchor="w",
        )
        label.pack(anchor="w")

        self._chat_frame.after(50, lambda: self._chat_frame._parent_canvas.yview_moveto(1.0))

    # ── Voice Interaction ─────────────────────────────────────────────────────

    def _on_voice_tap(self):
        if self._diagnosing:
            return
        self.voice_btn.set_state("listening")
        self._voice_label.configure(text="Listening...", text_color=COLORS["accent"])
        self.status_bar.set_status("Listening...", COLORS["accent"])
        threading.Thread(target=self._voice_listen, daemon=True).start()

    def _voice_listen(self):
        try:
            response = voice_input.listen(mode="open", lang=self.lang, timeout=10)
            if response and response.strip():
                self.after(0, lambda: self._add_message(response, "user"))
                self.after(0, lambda: self.voice_btn.set_state("processing"))
                self.after(0, lambda: self._voice_label.configure(
                    text="Processing...", text_color=COLORS["purple"]))
                self.after(0, lambda: self.status_bar.set_status("Analyzing...", COLORS["orange"]))

                # Send to Claude for a response
                self._handle_user_input(response)
            else:
                self.after(0, lambda: self.voice_btn.set_state("idle"))
                self.after(0, lambda: self._voice_label.configure(
                    text="Tap to speak", text_color=COLORS["text_secondary"]))
                self.after(0, lambda: self.status_bar.set_status("Ready", COLORS["green"]))
        except Exception as e:
            self.after(0, lambda: self.voice_btn.set_state("error"))
            self.after(0, lambda: self._voice_label.configure(
                text="Error — tap to retry", text_color=COLORS["red"]))
            self.after(2000, lambda: self.voice_btn.set_state("idle"))
            self.after(2000, lambda: self._voice_label.configure(
                text="Tap to speak", text_color=COLORS["text_secondary"]))

    # ── Text Input ────────────────────────────────────────────────────────────

    def _on_text_submit(self, event=None):
        text = self._text_input.get().strip()
        if not text or self._diagnosing:
            return
        self._text_input.delete(0, "end")
        self._add_message(text, "user")
        self.voice_btn.set_state("processing")
        self._voice_label.configure(text="Processing...", text_color=COLORS["purple"])
        self.status_bar.set_status("Analyzing...", COLORS["orange"])
        threading.Thread(target=self._handle_user_input, args=(text,), daemon=True).start()

    def _handle_user_input(self, text: str):
        """Process user text input — either diagnose or answer."""
        import anthropic

        try:
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                system=(
                    "You are FixMe, a friendly Windows IT support assistant. "
                    "Keep responses short (2-3 sentences). If the user describes an IT issue, "
                    "suggest they use the 'Diagnose Screen' button for a full diagnosis. "
                    "Be warm and helpful."
                ),
                messages=[{"role": "user", "content": text}],
            )
            reply = message.content[0].text.strip()
        except Exception as e:
            reply = f"I had trouble connecting. Try the Diagnose Screen button instead."

        self.after(0, lambda: self._add_message(reply, "assistant"))
        self.after(0, lambda: self._speak_async(reply))
        self.after(0, lambda: self.voice_btn.set_state("idle"))
        self.after(0, lambda: self._voice_label.configure(
            text="Tap to speak", text_color=COLORS["text_secondary"]))
        self.after(0, lambda: self.status_bar.set_status("Ready", COLORS["green"]))

    # ── Diagnosis Flow ────────────────────────────────────────────────────────

    def _on_diagnose(self):
        if self._diagnosing:
            return
        self._diagnosing = True
        self._diagnose_btn.configure(state="disabled", text="⏳  Diagnosing...")
        self.voice_btn.set_state("processing")
        self._voice_label.configure(text="Scanning screen...", text_color=COLORS["orange"])
        self.status_bar.set_status("Taking screenshot...", COLORS["orange"])
        self._add_message("Starting screen diagnosis...", "assistant")
        threading.Thread(target=self._run_diagnosis, daemon=True).start()

    def _run_diagnosis(self):
        try:
            # Step 1: Screenshot
            self.after(0, lambda: self.status_bar.set_status("Capturing screen...", COLORS["orange"]))
            image_path = screenshot.take_screenshot()

            # Step 2: Diagnose
            self.after(0, lambda: self.status_bar.set_status("Analyzing with AI...", COLORS["purple"]))
            self.after(0, lambda: self._voice_label.configure(
                text="Analyzing...", text_color=COLORS["purple"]))
            result = diagnose.diagnose_screenshot(image_path)

            # Clean up screenshot
            try:
                os.unlink(image_path)
            except OSError:
                pass

            diagnosis_text = result.get("diagnosis", "Unknown issue")
            steps = result.get("steps", [])

            # Show diagnosis
            self.after(0, lambda: self._add_message(
                f"🔍 **Diagnosis:** {diagnosis_text}", "assistant"))
            self.after(0, lambda: self._speak_async(f"I found the issue: {diagnosis_text}"))

            if not steps:
                self.after(0, lambda: self._add_message(
                    "No automated fix steps available. You may need to resolve this manually.",
                    "assistant"))
                return

            self.after(0, lambda: self._add_message(
                f"I have {len(steps)} steps to fix this. Let me walk you through each one.",
                "assistant"))

            time.sleep(1)

            # Initialize overlay
            self.overlay = Overlay()

            # Execute steps with permission
            fixes_applied = 0
            for i, step in enumerate(steps):
                step_num = i + 1
                desc = step.get("description", "Unknown step")
                command = step.get("command", "")
                needs_admin = step.get("needs_admin", False)
                ui_highlight = step.get("ui_highlight")

                self.after(0, lambda d=desc, n=step_num, t=len(steps):
                    self._add_step_message(n, t, d, "running"))
                self.after(0, lambda d=desc, n=step_num, t=len(steps):
                    self.status_bar.set_status(f"Step {n}/{t}: {d}", COLORS["orange"]))

                if self.overlay:
                    self.overlay.show_step(step_num, len(steps), desc, ui_highlight)

                # Ask permission
                self.after(0, lambda d=desc, n=step_num:
                    self._speak_async(f"Step {n}: I want to {d}. Shall I proceed?"))
                self.after(0, lambda: self.voice_btn.set_state("listening"))
                self.after(0, lambda: self._voice_label.configure(
                    text="Say yes, no, or ask a question", text_color=COLORS["accent"]))

                response = voice_input.listen(mode="open", lang=self.lang, timeout=15)

                if response:
                    self.after(0, lambda r=response: self._add_message(r, "user"))

                from fixme.voice_input import is_affirmative, is_negative

                if response and is_affirmative(response, self.lang):
                    self.after(0, lambda: self.voice_btn.set_state("processing"))
                    self.after(0, lambda n=step_num: self._voice_label.configure(
                        text=f"Executing step {n}...", text_color=COLORS["orange"]))

                    success, msg = fixes.execute(command, needs_admin)

                    if success:
                        fixes_applied += 1
                        self.after(0, lambda d=desc, n=step_num, t=len(steps):
                            self._add_step_message(n, t, d, "done"))
                        self.after(0, lambda n=step_num, m=msg:
                            self._add_message(f"✓ Step {n} complete. {m}", "assistant"))
                        if self.overlay:
                            self.overlay.show_success(step_num)
                    else:
                        self.after(0, lambda d=desc, n=step_num, t=len(steps):
                            self._add_step_message(n, t, d, "failed"))
                        self.after(0, lambda n=step_num, m=msg:
                            self._add_message(f"✕ Step {n} failed: {m}", "assistant"))

                elif response and is_negative(response, self.lang):
                    self.after(0, lambda d=desc, n=step_num, t=len(steps):
                        self._add_step_message(n, t, d, "skipped"))
                    self.after(0, lambda n=step_num:
                        self._add_message(f"Skipped step {n}.", "assistant"))

                elif response and any(kw in response.lower() for kw in ("stop", "abort", "quit")):
                    self.after(0, lambda: self._add_message("Stopping the fix process.", "assistant"))
                    break

                if self.overlay:
                    self.overlay.clear_step()

                time.sleep(0.5)

            # Summary
            if fixes_applied > 0:
                summary = f"Done! {fixes_applied} of {len(steps)} steps applied successfully."
            else:
                summary = "No fixes were applied."
            self.after(0, lambda: self._add_message(summary, "assistant"))
            self.after(0, lambda: self._speak_async(summary))

        except Exception as e:
            self.after(0, lambda: self._add_message(f"Diagnosis failed: {e}", "assistant"))
        finally:
            self._diagnosing = False
            self.after(0, lambda: self._diagnose_btn.configure(
                state="normal", text="🔍  Diagnose Screen"))
            self.after(0, lambda: self.voice_btn.set_state("idle"))
            self.after(0, lambda: self._voice_label.configure(
                text="Tap to speak", text_color=COLORS["text_secondary"]))
            self.after(0, lambda: self.status_bar.set_status("Ready", COLORS["green"]))
            if self.overlay:
                self.overlay.destroy()
                self.overlay = None

    # ── Screenshot Submit ─────────────────────────────────────────────────────

    def _on_screenshot(self):
        if self._diagnosing:
            return
        self._add_message("Taking a screenshot...", "assistant")
        self.status_bar.set_status("Capturing...", COLORS["orange"])
        threading.Thread(target=self._take_and_show_screenshot, daemon=True).start()

    def _take_and_show_screenshot(self):
        try:
            image_path = screenshot.take_screenshot()
            self.after(0, lambda: self._add_message(
                f"📷 Screenshot captured: {os.path.basename(image_path)}\n"
                "Use 'Diagnose Screen' to analyze it, or describe your issue.",
                "assistant"))
            self.after(0, lambda: self.status_bar.set_status("Ready", COLORS["green"]))
        except Exception as e:
            self.after(0, lambda: self._add_message(f"Screenshot failed: {e}", "assistant"))
            self.after(0, lambda: self.status_bar.set_status("Ready", COLORS["green"]))

    # ── TTS Helper ────────────────────────────────────────────────────────────

    def _speak_async(self, text: str):
        threading.Thread(target=tts.speak, args=(text, self.lang), daemon=True).start()


# ─── Entry Point ─────────────────────────────────────────────────────────────

def main():
    """Launch the FixMe desktop application."""
    missing_keys = []
    if not os.environ.get("ANTHROPIC_API_KEY"):
        missing_keys.append("ANTHROPIC_API_KEY")
    if not os.environ.get("ELEVENLABS_API_KEY"):
        missing_keys.append("ELEVENLABS_API_KEY")

    if missing_keys:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "FixMe — Setup Required",
            f"Missing API keys: {', '.join(missing_keys)}\n\n"
            "Create a .env file with:\n"
            "ANTHROPIC_API_KEY=sk-ant-...\n"
            "ELEVENLABS_API_KEY=...",
        )
        root.destroy()
        sys.exit(1)

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = FixMeUI()
    app.mainloop()


if __name__ == "__main__":
    main()
