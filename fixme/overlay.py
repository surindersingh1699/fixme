"""Transparent click-through screen overlay for highlighting and annotating UI elements."""

import threading
import warnings


class Overlay:
    """Fullscreen transparent overlay for drawing highlights and annotations."""

    def __init__(self):
        self._root = None
        self._canvas = None
        self._thread = None
        self._ready = threading.Event()
        self._screen_width = 0
        self._screen_height = 0
        self._start()

    def _start(self):
        """Start the overlay window in a dedicated thread."""
        self._thread = threading.Thread(target=self._run_tk, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5)

    def _run_tk(self):
        """Run tkinter mainloop in a dedicated thread."""
        try:
            import tkinter as tk

            self._root = tk.Tk()
            self._root.title("FixMe Overlay")
            self._root.attributes("-fullscreen", True)
            self._root.attributes("-topmost", True)
            self._root.attributes("-alpha", 0.8)

            # Make white areas transparent and click-through on Windows
            self._root.wm_attributes("-transparentcolor", "white")

            # Remove window decorations
            self._root.overrideredirect(True)

            self._screen_width = self._root.winfo_screenwidth()
            self._screen_height = self._root.winfo_screenheight()

            self._canvas = tk.Canvas(
                self._root,
                bg="white",
                highlightthickness=0,
                width=self._screen_width,
                height=self._screen_height,
            )
            self._canvas.pack(fill=tk.BOTH, expand=True)

            # Start hidden
            self._root.withdraw()
            self._ready.set()
            self._root.mainloop()

        except Exception as e:
            warnings.warn(f"Overlay initialization failed: {e}")
            self._ready.set()

    def _schedule(self, func, *args):
        """Schedule a function to run on the tkinter thread."""
        if self._root:
            try:
                self._root.after(0, func, *args)
            except Exception:
                pass

    def _get_location_coords(self, ui_highlight: dict) -> tuple[int, int, int]:
        """Map a ui_highlight location to screen pixel coordinates.

        Returns:
            Tuple of (x, y, radius).
        """
        if not ui_highlight:
            return self._screen_width // 2, self._screen_height // 2, 60

        # Check for explicit coordinates
        if "x" in ui_highlight and "y" in ui_highlight:
            return (
                ui_highlight["x"],
                ui_highlight["y"],
                ui_highlight.get("radius", 40),
            )

        location = ui_highlight.get("location", "center")
        sw, sh = self._screen_width, self._screen_height

        location_map = {
            "taskbar right": (sw - 100, sh - 30, 40),
            "taskbar left": (50, sh - 30, 40),
            "taskbar center": (sw // 2, sh - 30, 40),
            "center": (sw // 2, sh // 2, 60),
            "top right": (sw - 100, 50, 40),
            "top left": (50, 50, 40),
        }

        return location_map.get(location, (sw // 2, sh // 2, 60))

    def show_step(
        self,
        step_num: int,
        total_steps: int,
        description: str,
        ui_highlight: dict | None = None,
    ):
        """Display step information and highlight on the overlay.

        Args:
            step_num: Current step number (1-based).
            total_steps: Total number of steps.
            description: Description text for this step.
            ui_highlight: Optional dict with "element", "location", "action" keys.
        """
        self._schedule(self._draw_step, step_num, total_steps, description, ui_highlight)

    def _draw_step(self, step_num, total_steps, description, ui_highlight):
        """Draw step info on the canvas (must run on tk thread)."""
        if not self._canvas:
            return

        self._canvas.delete("all")
        self._root.deiconify()

        sw = self._screen_width

        # Background box for step info at top center
        box_width = 500
        box_x = (sw - box_width) // 2
        self._canvas.create_rectangle(
            box_x, 20, box_x + box_width, 110,
            fill="#1a1a2e", outline="#e94560", width=2,
        )

        # Step progress text
        self._canvas.create_text(
            sw // 2, 45,
            text=f"Step {step_num} of {total_steps}",
            fill="#e94560", font=("Segoe UI", 18, "bold"),
        )

        # Description text
        self._canvas.create_text(
            sw // 2, 80,
            text=description,
            fill="white", font=("Segoe UI", 12),
            width=box_width - 40,
        )

        # Draw highlight if provided
        if ui_highlight:
            x, y, r = self._get_location_coords(ui_highlight)
            action = ui_highlight.get("action", "circle")

            if action == "circle":
                self._canvas.create_oval(
                    x - r, y - r, x + r, y + r,
                    outline="#e94560", width=3,
                )
            elif action == "arrow":
                # Draw arrow pointing to the location
                self._canvas.create_line(
                    x - r - 40, y - r - 40, x - 5, y - 5,
                    fill="#e94560", width=3, arrow="last", arrowshape=(12, 15, 5),
                )
            elif action == "box":
                self._canvas.create_rectangle(
                    x - r, y - r, x + r, y + r,
                    outline="#e94560", width=3,
                )

            # Label for the highlighted element
            element_name = ui_highlight.get("element", "")
            if element_name:
                self._canvas.create_text(
                    x, y - r - 15,
                    text=element_name,
                    fill="#e94560", font=("Segoe UI", 10, "bold"),
                )

    def show_success(self, step_num: int):
        """Show a green checkmark for a completed step."""
        self._schedule(self._draw_success, step_num)

    def _draw_success(self, step_num):
        """Draw success indicator (must run on tk thread)."""
        if not self._canvas:
            return

        sw = self._screen_width
        self._canvas.create_text(
            sw // 2, 140,
            text=f"✓ Step {step_num} Complete",
            fill="#4CAF50", font=("Segoe UI", 16, "bold"),
        )

    def clear_step(self):
        """Clear all drawings from the overlay."""
        self._schedule(self._clear)

    def _clear(self):
        """Clear canvas and hide window (must run on tk thread)."""
        if self._canvas:
            self._canvas.delete("all")
        if self._root:
            self._root.withdraw()

    def show_recording_indicator(self):
        """Show a red recording dot in the top-right corner."""
        self._schedule(self._draw_recording)

    def _draw_recording(self):
        """Draw recording indicator (must run on tk thread)."""
        if not self._canvas:
            return

        self._root.deiconify()
        sw = self._screen_width
        # Red filled circle
        self._canvas.create_oval(
            sw - 50, 15, sw - 30, 35,
            fill="red", outline="red", tags="rec",
        )
        self._canvas.create_text(
            sw - 65, 25,
            text="REC", fill="red", font=("Segoe UI", 9, "bold"), tags="rec",
        )

    def hide_recording_indicator(self):
        """Remove the recording indicator."""
        self._schedule(self._hide_recording)

    def _hide_recording(self):
        """Remove recording indicator (must run on tk thread)."""
        if self._canvas:
            self._canvas.delete("rec")

    def destroy(self):
        """Close the overlay window."""
        if self._root:
            try:
                self._root.after(0, self._root.destroy)
            except Exception:
                pass
