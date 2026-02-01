"""FixMe — Claude-like desktop UI with history panel and step-by-step transparency.

Uses pure tkinter (no customtkinter) to avoid macOS NSWindow threading crashes.
"""

import os
import sys
import math
import threading
import time
import json
import tkinter as tk
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Lazy-import heavy / Windows-specific modules to avoid macOS crashes.


# ─── Design Tokens ────────────────────────────────────────────────────────────

P = {
    # Dark theme matching landing page (zinc-950 base, indigo accent)
    "bg":              "#09090B",
    "surface":         "#18181B",
    "surface_hover":   "#27272A",
    "sidebar_bg":      "#0F0F12",
    "sidebar_hover":   "#1C1C21",
    "sidebar_active":  "#27272A",
    "border":          "#27272A",
    "text":            "#FAFAFA",
    "text_secondary":  "#A1A1AA",
    "text_muted":      "#71717A",
    "brand":           "#6366F1",
    "brand_light":     "#818CF8",
    "brand_dark":      "#4F46E5",
    "brand_bg":        "#1E1B4B",
    "success":         "#10B981",
    "success_bg":      "#052E16",
    "warning":         "#F59E0B",
    "warning_bg":      "#422006",
    "error":           "#EF4444",
    "error_bg":        "#450A0A",
    "orb":             "#6366F1",
    "orb_ring_1":      "#818CF8",
    "orb_ring_2":      "#A78BFA",
    "orb_ring_3":      "#C084FC",
    "orb_process":     "#8B5CF6",
    "bubble_user":     "#6366F1",
    "bubble_ai":       "#18181B",
}

FONT = ("SF Pro Display", 13) if sys.platform == "darwin" else ("Segoe UI", 10)
FONT_SM = (FONT[0], FONT[1] - 2)
FONT_XS = (FONT[0], FONT[1] - 4)
FONT_LG_BOLD = (FONT[0], FONT[1] + 1, "bold")
FONT_BOLD = (FONT[0], FONT[1], "bold")

HISTORY_PATH = Path.home() / ".fixme" / "history.json"


# ─── History Manager ──────────────────────────────────────────────────────────

class HistoryManager:
    def __init__(self):
        HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._sessions = self._load()

    def _load(self):
        if HISTORY_PATH.exists():
            try:
                return json.loads(HISTORY_PATH.read_text())
            except Exception:
                return []
        return []

    def _save(self):
        try:
            HISTORY_PATH.write_text(json.dumps(self._sessions, indent=2))
        except Exception:
            pass

    def new_session(self, title=None):
        s = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "title": title or "New conversation",
            "created": datetime.now().isoformat(),
            "messages": [],
        }
        self._sessions.insert(0, s)
        self._save()
        return s

    def add_message(self, session_id, role, text):
        for s in self._sessions:
            if s["id"] == session_id:
                s["messages"].append({
                    "role": role, "text": text,
                    "time": datetime.now().isoformat(),
                })
                if role == "user" and s["title"] == "New conversation":
                    s["title"] = text[:50] + ("..." if len(text) > 50 else "")
                self._save()
                return

    def get_sessions(self):
        return self._sessions

    def get_session(self, sid):
        for s in self._sessions:
            if s["id"] == sid:
                return s
        return None


# ─── Voice Orb ────────────────────────────────────────────────────────────────

class VoiceOrb(tk.Canvas):
    SIZE = 130
    R = 34

    COLORS = {
        "idle": P["orb"], "listening": P["brand"],
        "processing": P["orb_process"], "success": P["success"], "error": P["error"],
    }

    def __init__(self, master, command=None, **kw):
        super().__init__(master, width=self.SIZE, height=self.SIZE,
                         bg=P["surface"], highlightthickness=0, **kw)
        self._cmd = command
        self._state = "idle"
        self._phase = 0.0
        self._anim = False
        self.bind("<Button-1>", self._click)
        self._draw()

    def _click(self, e):
        if math.hypot(e.x - self.SIZE / 2, e.y - self.SIZE / 2) <= self.R + 18:
            if self._cmd:
                self._cmd()

    def set_state(self, s):
        self._state = s
        if s in ("listening", "processing"):
            if not self._anim:
                self._anim = True
                self._tick()
        else:
            self._anim = False
            self._draw()

    def _tick(self):
        if not self._anim:
            return
        self._phase += 0.05
        self._draw()
        self.after(25, self._tick)

    def _draw(self):
        self.delete("all")
        cx, cy = self.SIZE / 2, self.SIZE / 2
        r = self.R
        c = self.COLORS.get(self._state, P["orb"])

        if self._state in ("listening", "processing"):
            p = self._phase
            for i, ring_c in enumerate([P["orb_ring_1"], P["orb_ring_2"], P["orb_ring_3"]]):
                w = math.sin(p + i * 0.7) * 0.5 + 0.5
                rr = r + 8 + i * 8 + w * 7
                self.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                                 outline=ring_c, width=1.3 + w)
            self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=c, outline="")
            if self._state == "listening":
                bw, gap, n = 3, 4, 5
                sx = cx - (n * bw + (n - 1) * gap) / 2
                for i in range(n):
                    h = 4 + math.sin(p * 3 + i * 0.9) * 8
                    x = sx + i * (bw + gap)
                    self.create_rectangle(x, cy - h / 2, x + bw, cy + h / 2,
                                          fill="#FFF", outline="")
            else:
                for i in range(3):
                    a = p * 2 + i * (2 * math.pi / 3)
                    dx, dy = math.cos(a) * 8, math.sin(a) * 8
                    self.create_oval(cx + dx - 2.5, cy + dy - 2.5,
                                     cx + dx + 2.5, cy + dy + 2.5, fill="#FFF", outline="")
        elif self._state == "success":
            self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=P["success"], outline="")
            self.create_text(cx, cy, text="\u2713", fill="#FFF", font=(FONT[0], 18, "bold"))
        elif self._state == "error":
            self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=P["error"], outline="")
            self.create_text(cx, cy, text="\u2715", fill="#FFF", font=(FONT[0], 18, "bold"))
        else:
            for i in range(3):
                gr = r + 10 + i * 8
                self.create_oval(cx - gr, cy - gr, cx + gr, cy + gr,
                                 outline=P["orb_ring_1"], width=0.8)
            self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=c, outline="")
            self.create_text(cx, cy - 2, text="\U0001f3a4", font=(FONT[0], 16))


# ─── Scrollable Frame ─────────────────────────────────────────────────────────

class ScrollFrame(tk.Frame):
    def __init__(self, master, bg="#FFFFFF", **kw):
        super().__init__(master, bg=bg, **kw)
        self._canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self._canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self._canvas, bg=bg)
        self._win = self._canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", lambda e: self._canvas.configure(
            scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(
            self._win, width=e.width))
        self._canvas.bind("<MouseWheel>", lambda e: self._canvas.yview_scroll(
            int(-1 * (e.delta / 120)), "units"))
        self.inner.bind("<MouseWheel>", lambda e: self._canvas.yview_scroll(
            int(-1 * (e.delta / 120)), "units"))

    def scroll_to_bottom(self):
        self._canvas.update_idletasks()
        self._canvas.yview_moveto(1.0)

    def clear(self):
        for w in self.inner.winfo_children():
            w.destroy()


# ─── Sidebar ──────────────────────────────────────────────────────────────────

class Sidebar(tk.Frame):
    LANGS = [("en", "EN"), ("es", "ES"), ("pa", "PA"), ("hi", "HI"), ("fr", "FR")]

    def __init__(self, master, on_select, on_new, **kw):
        super().__init__(master, bg=P["sidebar_bg"], width=220, **kw)
        self.pack_propagate(False)
        self._on_select = on_select
        self._lang = "en"
        self._lang_btns = []

        hdr = tk.Frame(self, bg=P["sidebar_bg"], height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="FixMe", bg=P["sidebar_bg"], fg=P["text"],
                 font=(FONT[0], 15, "bold")).pack(side="left", padx=12, pady=8)
        tk.Button(hdr, text="+", bg=P["sidebar_hover"], fg=P["text"],
                  font=(FONT[0], 14), relief="flat", bd=0,
                  activebackground=P["sidebar_active"],
                  command=on_new).pack(side="right", padx=8, pady=8)

        tk.Frame(self, bg=P["border"], height=1).pack(fill="x")

        self._list = ScrollFrame(self, bg=P["sidebar_bg"])
        self._list.pack(fill="both", expand=True)

        tk.Frame(self, bg=P["border"], height=1).pack(fill="x", side="bottom")
        foot = tk.Frame(self, bg=P["sidebar_bg"], height=40)
        foot.pack(fill="x", side="bottom")
        foot.pack_propagate(False)
        lang_row = tk.Frame(foot, bg=P["sidebar_bg"])
        lang_row.pack(padx=6, pady=6, fill="x")

        for code, label in self.LANGS:
            bg = P["brand"] if code == "en" else P["sidebar_hover"]
            fg = "#FFF" if code == "en" else P["text_secondary"]
            btn = tk.Button(lang_row, text=label, bg=bg, fg=fg,
                            font=(FONT[0], 9, "bold"), relief="flat", bd=0,
                            width=3, activebackground=P["brand_dark"],
                            command=lambda c=code: self._set_lang(c))
            btn.pack(side="left", padx=1, expand=True, fill="x")
            self._lang_btns.append((code, btn))

    def _set_lang(self, code):
        self._lang = code
        for c, btn in self._lang_btns:
            if c == code:
                btn.configure(bg=P["brand"], fg="#FFF")
            else:
                btn.configure(bg=P["sidebar_hover"], fg=P["text_secondary"])

    @property
    def lang_code(self):
        return self._lang

    def refresh(self, sessions, active_id=None):
        self._list.clear()
        today = datetime.now().strftime("%Y-%m-%d")
        last_group = None
        for s in sessions:
            created = s.get("created", "")[:10]
            group = "Today" if created == today else "Earlier"
            if group != last_group:
                tk.Label(self._list.inner, text=group, bg=P["sidebar_bg"],
                         fg=P["text_muted"], font=(FONT[0], 9, "bold"),
                         anchor="w").pack(fill="x", padx=12, pady=(8, 2))
                last_group = group

            is_active = s["id"] == active_id
            bg = P["sidebar_active"] if is_active else P["sidebar_bg"]
            fg = P["text"] if is_active else P["text_secondary"]
            tk.Button(self._list.inner, text=s.get("title", "Untitled")[:30],
                      bg=bg, fg=fg, anchor="w", font=FONT_SM, relief="flat",
                      bd=0, padx=12, pady=4, activebackground=P["sidebar_hover"],
                      command=lambda sid=s["id"]: self._on_select(sid),
                      ).pack(fill="x", padx=4, pady=1)


# ─── Main App ─────────────────────────────────────────────────────────────────

class FixMeUI(tk.Tk):
    W, H = 880, 680

    def __init__(self):
        super().__init__()
        self.title("FixMe")
        self.geometry(f"{self.W}x{self.H}")
        self.minsize(680, 480)
        self.configure(bg=P["bg"])

        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.W) // 2
        y = (self.winfo_screenheight() - self.H) // 2
        self.geometry(f"+{x}+{y}")

        self._history = HistoryManager()
        self._session = None
        self._busy = False
        self._build()
        self._new_session()

    def _build(self):
        self.sidebar = Sidebar(self, on_select=self._load_session,
                                on_new=self._new_session)
        self.sidebar.pack(side="left", fill="y")
        tk.Frame(self, bg=P["border"], width=1).pack(side="left", fill="y")

        main = tk.Frame(self, bg=P["bg"])
        main.pack(side="left", fill="both", expand=True)

        top = tk.Frame(main, bg=P["bg"], height=44)
        top.pack(fill="x")
        top.pack_propagate(False)
        self._title_lbl = tk.Label(top, text="New conversation", bg=P["bg"],
                                    fg=P["text"], font=FONT_LG_BOLD)
        self._title_lbl.pack(side="left", padx=16, pady=8)
        self._status_lbl = tk.Label(top, text="\u25cf Ready", bg=P["success_bg"],
                                     fg=P["success"], font=FONT_XS, padx=8, pady=2)
        self._status_lbl.pack(side="right", padx=16, pady=10)
        tk.Frame(main, bg=P["border"], height=1).pack(fill="x")

        self._chat = ScrollFrame(main, bg=P["bg"])
        self._chat.pack(fill="both", expand=True)

        bottom = tk.Frame(main, bg=P["surface"])
        bottom.pack(fill="x", side="bottom")

        orb_row = tk.Frame(bottom, bg=P["surface"])
        orb_row.pack(pady=(8, 0))
        self.orb = VoiceOrb(orb_row, command=self._tap_voice)
        self.orb.pack()
        self._orb_lbl = tk.Label(bottom, text="Tap to speak", bg=P["surface"],
                                  fg=P["text_secondary"], font=FONT_SM)
        self._orb_lbl.pack(pady=(0, 4))

        irow = tk.Frame(bottom, bg=P["surface"])
        irow.pack(fill="x", padx=12, pady=(0, 8))
        self._inp = tk.Entry(irow, font=FONT, bg=P["bg"], fg=P["text"],
                              insertbackground=P["text"], relief="solid", bd=1,
                              highlightthickness=0)
        self._inp.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        self._inp.bind("<Return>", self._submit_text)
        tk.Button(irow, text="\u2191", bg=P["brand"], fg="#FFF",
                  font=(FONT[0], 14, "bold"), relief="flat", bd=0, width=3,
                  activebackground=P["brand_dark"],
                  command=self._submit_text).pack(side="right")

        brow = tk.Frame(bottom, bg=P["surface"])
        brow.pack(fill="x", padx=12, pady=(0, 8))
        self._dbtn = tk.Button(brow, text="Diagnose Screen", bg=P["brand"],
                                fg="#FFF", font=FONT_BOLD, relief="flat", bd=0,
                                activebackground=P["brand_dark"], pady=6,
                                command=self._on_diagnose)
        self._dbtn.pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Button(brow, text="Screenshot", bg=P["surface_hover"],
                  fg=P["text_secondary"], font=FONT_SM, relief="flat", bd=0,
                  activebackground=P["border"], pady=6,
                  command=self._on_ss).pack(side="left", fill="x", expand=True, padx=(4, 0))

    # ── Sessions ──────────────────────────────────────────────────────────────

    def _new_session(self):
        self._session = self._history.new_session()
        self._refresh_sidebar()
        self._clear_chat()
        self._title_lbl.configure(text="New conversation")
        self.after(300, lambda: self._msg(
            "Hey! I'm FixMe, your AI IT assistant.\n\n"
            "Tell me what's wrong \u2014 in any language.\n"
            "I'll diagnose it, walk you through each fix step by step, "
            "and ask your permission before doing anything.", "assistant"))

    def _load_session(self, sid):
        s = self._history.get_session(sid)
        if not s:
            return
        self._session = s
        self._refresh_sidebar()
        self._clear_chat()
        self._title_lbl.configure(text=s.get("title", "Conversation"))
        for m in s.get("messages", []):
            self._msg(m["text"], m["role"], save=False)

    def _refresh_sidebar(self):
        active = self._session["id"] if self._session else None
        self.sidebar.refresh(self._history.get_sessions(), active)

    def _clear_chat(self):
        self._chat.clear()

    # ── Chat ──────────────────────────────────────────────────────────────────

    def _msg(self, text, role="assistant", save=True):
        if save and self._session:
            self._history.add_message(self._session["id"], role, text)
            if role == "user":
                self._refresh_sidebar()

        is_user = role == "user"
        bg = P["bubble_user"] if is_user else P["bubble_ai"]
        fg = "#FFFFFF" if is_user else P["text"]
        anchor = "e" if is_user else "w"

        row = tk.Frame(self._chat.inner, bg=P["bg"])
        row.pack(fill="x", padx=12, pady=4)
        bubble = tk.Frame(row, bg=bg, padx=12, pady=8)
        bubble.pack(anchor=anchor, padx=(60, 0) if is_user else (0, 60))
        tk.Label(bubble, text=text, bg=bg, fg=fg, font=FONT,
                 wraplength=400, justify="left", anchor="w").pack(anchor="w")
        tk.Label(bubble, text=datetime.now().strftime("%I:%M %p"), bg=bg,
                 fg="#C7D2FE" if is_user else P["text_muted"],
                 font=FONT_XS).pack(anchor=anchor)
        self._chat.after(50, self._chat.scroll_to_bottom)

    def _step(self, num, total, desc, status="pending"):
        icons = {"pending": "\u25cb", "running": "\u25cf", "done": "\u2713",
                 "failed": "\u2715", "skipped": "\u2013"}
        clrs = {"running": P["warning"], "done": P["success"],
                "failed": P["error"], "pending": P["text_muted"]}
        bgs = {"running": P["warning_bg"], "done": P["success_bg"],
               "failed": P["error_bg"]}

        row = tk.Frame(self._chat.inner, bg=P["bg"])
        row.pack(fill="x", padx=12, pady=2)
        card = tk.Frame(row, bg=bgs.get(status, P["surface"]), padx=10, pady=6)
        card.pack(fill="x")
        tk.Label(card, text=icons.get(status, "\u25cb"), bg=card["bg"],
                 fg=clrs.get(status, P["text_muted"]),
                 font=FONT_BOLD).pack(side="left")
        tk.Label(card, text=f"Step {num}/{total}", bg=card["bg"],
                 fg=P["text_muted"], font=FONT_XS).pack(side="left", padx=(6, 10))
        tk.Label(card, text=desc, bg=card["bg"], fg=P["text"],
                 font=FONT_SM, anchor="w").pack(side="left", fill="x", expand=True)
        self._chat.after(50, self._chat.scroll_to_bottom)

    def _set_status(self, text, color=None):
        c = color or P["success"]
        bg_map = {P["success"]: P["success_bg"], P["warning"]: P["warning_bg"],
                  P["error"]: P["error_bg"], P["brand"]: P["brand_bg"]}
        self._status_lbl.configure(text=f"\u25cf {text}", fg=c,
                                    bg=bg_map.get(c, P["surface"]))

    # ── Voice ─────────────────────────────────────────────────────────────────

    def _tap_voice(self):
        if self._busy:
            return
        # Show a voice-input dialog on the main thread (avoids NSWindow crash)
        self.orb.set_state("listening")
        self._orb_lbl.configure(text="Listening...", fg=P["brand"])
        self._set_status("Listening", P["brand"])
        self._show_voice_dialog()

    def _show_voice_dialog(self):
        """Main-thread voice input dialog using tk.Toplevel."""
        dlg = tk.Toplevel(self)
        dlg.title("FixMe — Voice Input")
        dlg.geometry("420x160")
        dlg.resizable(False, False)
        dlg.configure(bg=P["bg"])
        dlg.transient(self)
        dlg.grab_set()

        dlg.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 420) // 2
        y = self.winfo_y() + (self.winfo_height() - 160) // 2
        dlg.geometry(f"+{x}+{y}")

        lang = self.sidebar.lang_code
        prompt = {
            "en": "Type your message:", "es": "Escriba su mensaje:",
            "pa": "ਆਪਣਾ ਸੁਨੇਹਾ ਟਾਈਪ ਕਰੋ:", "hi": "अपना संदेश टाइप करें:",
            "fr": "Tapez votre message:",
        }.get(lang, "Type your message:")

        tk.Label(dlg, text=prompt, bg=P["bg"], fg=P["text"],
                 font=FONT_LG_BOLD).pack(pady=(16, 8))

        entry = tk.Entry(dlg, font=FONT, bg=P["surface"], fg=P["text"],
                         insertbackground=P["text"], relief="solid", bd=1,
                         highlightthickness=0, width=40)
        entry.pack(padx=16, ipady=6)
        entry.focus_set()

        def submit(e=None):
            t = entry.get().strip()
            dlg.destroy()
            if t:
                self._msg(t, "user")
                self.orb.set_state("processing")
                self._orb_lbl.configure(text="Thinking...", fg=P["orb_process"])
                self._set_status("Processing", P["orb_process"])
                threading.Thread(target=self._handle, args=(t,), daemon=True).start()
            else:
                self._reset()

        def cancel():
            dlg.destroy()
            self._reset()

        entry.bind("<Return>", submit)
        dlg.protocol("WM_DELETE_WINDOW", cancel)

        btn_row = tk.Frame(dlg, bg=P["bg"])
        btn_row.pack(pady=(10, 0))
        tk.Button(btn_row, text="Send", bg=P["brand"], fg="#FFF",
                  font=FONT_BOLD, relief="flat", bd=0, width=10,
                  activebackground=P["brand_dark"],
                  command=submit).pack(side="left", padx=4)
        tk.Button(btn_row, text="Cancel", bg=P["surface_hover"],
                  fg=P["text_secondary"], font=FONT_SM, relief="flat",
                  bd=0, width=10, command=cancel).pack(side="left", padx=4)

    def _ask_permission(self, prompt_text, lang, answer_dict, event):
        """Show a Yes/No/Skip dialog on the main thread for diagnose steps."""
        dlg = tk.Toplevel(self)
        dlg.title("FixMe — Permission")
        dlg.geometry("400x160")
        dlg.resizable(False, False)
        dlg.configure(bg=P["bg"])
        dlg.transient(self)
        dlg.grab_set()

        dlg.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 160) // 2
        dlg.geometry(f"+{x}+{y}")

        tk.Label(dlg, text=prompt_text, bg=P["bg"], fg=P["text"],
                 font=FONT, wraplength=360, justify="center").pack(pady=(16, 12))

        def respond(val):
            answer_dict["value"] = val
            dlg.destroy()
            event.set()

        def on_close():
            respond("no")

        dlg.protocol("WM_DELETE_WINDOW", on_close)

        yes_lbl = "Sí" if lang == "es" else "Yes"
        no_lbl = "No"
        skip_lbl = "Saltar" if lang == "es" else "Skip"

        btn_row = tk.Frame(dlg, bg=P["bg"])
        btn_row.pack(pady=8)
        tk.Button(btn_row, text=yes_lbl, bg=P["success"], fg="#FFF",
                  font=FONT_BOLD, relief="flat", bd=0, width=8,
                  command=lambda: respond("yes")).pack(side="left", padx=4)
        tk.Button(btn_row, text=no_lbl, bg=P["error"], fg="#FFF",
                  font=FONT_BOLD, relief="flat", bd=0, width=8,
                  command=lambda: respond("no")).pack(side="left", padx=4)
        tk.Button(btn_row, text=skip_lbl, bg=P["surface_hover"],
                  fg=P["text_secondary"], font=FONT_SM, relief="flat",
                  bd=0, width=8, command=lambda: respond("skip")).pack(side="left", padx=4)

    def _reset(self):
        self.after(0, lambda: self.orb.set_state("idle"))
        self.after(0, lambda: self._orb_lbl.configure(text="Tap to speak", fg=P["text_secondary"]))
        self.after(0, lambda: self._set_status("Ready", P["success"]))

    # ── Text ──────────────────────────────────────────────────────────────────

    def _submit_text(self, e=None):
        t = self._inp.get().strip()
        if not t or self._busy:
            return
        self._inp.delete(0, "end")
        self._msg(t, "user")
        self.orb.set_state("processing")
        self._orb_lbl.configure(text="Thinking...", fg=P["orb_process"])
        self._set_status("Processing", P["orb_process"])
        threading.Thread(target=self._handle, args=(t,), daemon=True).start()

    def _handle(self, text):
        import anthropic
        _os = "macOS" if sys.platform == "darwin" else "Windows"
        try:
            cl = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            lang = self.sidebar.lang_code
            names = {"en": "English", "es": "Spanish", "pa": "Punjabi",
                     "hi": "Hindi", "fr": "French"}
            m = cl.messages.create(
                model="claude-sonnet-4-20250514", max_tokens=1024,
                system=(
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
                       if _os == "macOS" else
                       "- netsh for Wi-Fi, ipconfig for DNS/network\n"
                       "- rundll32 for credential manager\n")
                    + "\nIf the issue is conversational (greetings, questions about you, etc.), "
                    "just respond naturally without a commands block. "
                    "Be concise and empathetic."
                ),
                messages=[{"role": "user", "content": text}],
            )
            reply = m.content[0].text.strip()
        except Exception as e:
            reply = f"I had trouble connecting: {e}"
            self.after(0, lambda: self._msg(reply, "assistant"))
            self._reset()
            return

        # Parse commands block if present
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

        self.after(0, lambda: self._msg(display_reply, "assistant"))
        self.after(0, lambda: self._speak(display_reply))

        if commands:
            self.after(0, lambda: self._msg(
                f"I have {len(commands)} fix steps. I'll ask permission for each.", "assistant"))
            time.sleep(1)
            self._run_fix_steps(commands)
        else:
            self._reset()

    def _run_fix_steps(self, steps):
        """Execute a list of fix steps with permission dialogs."""
        from fixme.fixes import execute
        from fixme.voice_input import is_affirmative, is_negative
        lang = self.sidebar.lang_code
        applied = 0

        for i, step in enumerate(steps):
            n, t = i + 1, len(steps)
            desc = step.get("description", "Unknown")
            cmd = step.get("command", "")
            admin = step.get("needs_admin", False)

            self.after(0, lambda d=desc, sn=n, st=t: self._step(sn, st, d, "running"))
            self.after(0, lambda sn=n, st=t: self._set_status(f"Step {sn}/{st}", P["warning"]))

            answer = {"value": ""}
            evt = threading.Event()
            self.after(0, lambda d=desc, sn=n, c=cmd: self._ask_permission(
                f"Step {sn}: {d}\nCommand: {c}\nProceed?", lang, answer, evt))
            evt.wait(timeout=60)
            resp = answer["value"]

            if resp:
                self.after(0, lambda r=resp: self._msg(r, "user"))
            if resp and is_affirmative(resp, lang):
                self.after(0, lambda: self.orb.set_state("processing"))
                ok, msg = execute(cmd, admin)
                st_status = "done" if ok else "failed"
                applied += 1 if ok else 0
                self.after(0, lambda d=desc, sn=n, st=t, ss=st_status: self._step(sn, st, d, ss))
                self.after(0, lambda m=msg: self._msg(f"Result: {m}", "assistant"))
            elif resp and is_negative(resp, lang):
                self.after(0, lambda d=desc, sn=n, st=t: self._step(sn, st, d, "skipped"))
            elif resp and any(k in resp.lower() for k in ("stop", "abort", "quit")):
                break
            time.sleep(0.5)

        summary = f"Done! {applied}/{len(steps)} steps applied." if applied else "No fixes applied."
        self.after(0, lambda: self._msg(summary, "assistant"))
        self.after(0, lambda: self._speak(summary))
        self._reset()

    # ── Diagnose ──────────────────────────────────────────────────────────────

    def _on_diagnose(self):
        if self._busy:
            return
        self._busy = True
        self._dbtn.configure(state="disabled", text="Diagnosing...")
        self.orb.set_state("processing")
        self._set_status("Diagnosing", P["warning"])
        self._msg("Scanning your screen...", "assistant")
        threading.Thread(target=self._diag_work, daemon=True).start()

    def _diag_work(self):
        try:
            from fixme import screenshot, diagnose, fixes
            from fixme.voice_input import is_affirmative, is_negative
            lang = self.sidebar.lang_code

            self.after(0, lambda: self._set_status("Capturing", P["warning"]))
            img = screenshot.take_screenshot()
            self.after(0, lambda: self._set_status("Analyzing", P["orb_process"]))
            result = diagnose.diagnose_screenshot(img)
            try:
                os.unlink(img)
            except OSError:
                pass

            diag = result.get("diagnosis", "Unknown issue")
            steps = result.get("steps", [])
            self.after(0, lambda: self._msg(f"Diagnosis: {diag}", "assistant"))
            self.after(0, lambda: self._speak(f"I found the issue: {diag}"))

            if not steps:
                self.after(0, lambda: self._msg("No automated fix steps available.", "assistant"))
                return

            self.after(0, lambda: self._msg(
                f"I have {len(steps)} steps to fix this.", "assistant"))
            time.sleep(1)

            applied = 0
            for i, step in enumerate(steps):
                n, t = i + 1, len(steps)
                desc = step.get("description", "Unknown")
                cmd = step.get("command", "")

                self.after(0, lambda d=desc, sn=n, st=t: self._step(sn, st, d, "running"))
                self.after(0, lambda sn=n, st=t: self._set_status(f"Step {sn}/{st}", P["warning"]))
                self.after(0, lambda d=desc, sn=n: self._speak(f"Step {sn}: {d}. Shall I proceed?"))
                self.after(0, lambda: self.orb.set_state("listening"))

                # Ask permission on main thread, block worker until answered
                answer = {"value": ""}
                evt = threading.Event()
                self.after(0, lambda: self._ask_permission(
                    f"Step {n}: {desc}\nProceed?", lang, answer, evt))
                evt.wait(timeout=60)
                resp = answer["value"]

                if resp:
                    self.after(0, lambda r=resp: self._msg(r, "user"))
                if resp and is_affirmative(resp, lang):
                    self.after(0, lambda: self.orb.set_state("processing"))
                    ok, msg = fixes.execute(cmd, step.get("needs_admin", False))
                    st_status = "done" if ok else "failed"
                    applied += 1 if ok else 0
                    self.after(0, lambda d=desc, sn=n, st=t, ss=st_status: self._step(sn, st, d, ss))
                elif resp and is_negative(resp, lang):
                    self.after(0, lambda d=desc, sn=n, st=t: self._step(sn, st, d, "skipped"))
                elif resp and any(k in resp.lower() for k in ("stop", "abort", "quit")):
                    break
                time.sleep(0.5)

            summary = f"Done! {applied}/{len(steps)} steps applied." if applied else "No fixes applied."
            self.after(0, lambda: self._msg(summary, "assistant"))
            self.after(0, lambda: self._speak(summary))

            # Verification: re-capture screen and check if issue is resolved
            if applied > 0:
                time.sleep(2)
                self.after(0, lambda: self._set_status("Verifying fix", P["brand"]))
                self.after(0, lambda: self._msg("Verifying if the fix worked...", "assistant"))
                try:
                    verify_img = screenshot.take_screenshot()
                    verify_result = diagnose.diagnose_screenshot(verify_img)
                    try:
                        os.unlink(verify_img)
                    except OSError:
                        pass
                    v_diag = verify_result.get("diagnosis", "")
                    v_steps = verify_result.get("steps", [])
                    if not v_steps:
                        self.after(0, lambda: self._msg(
                            "Looks good! No issues detected on screen.", "assistant"))
                    else:
                        self.after(0, lambda d=v_diag: self._msg(
                            f"Still seeing an issue: {d}\nYou can try Diagnose again.", "assistant"))
                except Exception:
                    pass
        except Exception as e:
            self.after(0, lambda: self._msg(f"Diagnosis failed: {e}", "assistant"))
        finally:
            self._busy = False
            self.after(0, lambda: self._dbtn.configure(state="normal", text="Diagnose Screen"))
            self._reset()

    # ── GUI Automation ─────────────────────────────────────────────────────────

    def _click_at(self, x, y, description=""):
        """Click at screen coordinates using pyautogui."""
        try:
            import pyautogui
            pyautogui.FAILSAFE = True
            pyautogui.click(x, y)
            self.after(0, lambda: self._msg(
                f"Clicked at ({x}, {y})" + (f": {description}" if description else ""),
                "assistant"))
            return True
        except Exception as e:
            self.after(0, lambda: self._msg(f"Click failed: {e}", "assistant"))
            return False

    def _type_text(self, text, interval=0.03):
        """Type text using pyautogui."""
        try:
            import pyautogui
            pyautogui.FAILSAFE = True
            pyautogui.typewrite(text, interval=interval)
            return True
        except Exception as e:
            self.after(0, lambda: self._msg(f"Typing failed: {e}", "assistant"))
            return False

    def _open_app(self, app_name):
        """Open an application by name (cross-platform)."""
        try:
            if sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", "-a", app_name])
            else:
                import subprocess
                subprocess.Popen(["start", app_name], shell=True)
            self.after(0, lambda: self._msg(f"Opened {app_name}", "assistant"))
            return True
        except Exception as e:
            self.after(0, lambda: self._msg(f"Failed to open {app_name}: {e}", "assistant"))
            return False

    # ── Screenshot ────────────────────────────────────────────────────────────

    def _on_ss(self):
        if self._busy:
            return
        self._set_status("Capturing", P["warning"])
        threading.Thread(target=self._ss_work, daemon=True).start()

    def _ss_work(self):
        try:
            from fixme import screenshot
            path = screenshot.take_screenshot()
            self.after(0, lambda: self._msg(
                f"Screenshot saved: {os.path.basename(path)}\nHit Diagnose to analyze it.", "assistant"))
        except Exception as e:
            self.after(0, lambda: self._msg(f"Screenshot failed: {e}", "assistant"))
        finally:
            self.after(0, lambda: self._set_status("Ready", P["success"]))

    # ── TTS ───────────────────────────────────────────────────────────────────

    def _speak(self, text):
        def w():
            try:
                from fixme import tts
                tts.speak(text, self.sidebar.lang_code)
            except Exception:
                pass
        threading.Thread(target=w, daemon=True).start()


# ─── Entry ────────────────────────────────────────────────────────────────────

def main():
    missing = []
    if not os.environ.get("ANTHROPIC_API_KEY"):
        missing.append("ANTHROPIC_API_KEY")
    if not os.environ.get("ELEVENLABS_API_KEY"):
        missing.append("ELEVENLABS_API_KEY")
    if missing:
        print(f"[FixMe] Missing: {', '.join(missing)}\n"
              "Create a .env file:\n  ANTHROPIC_API_KEY=sk-ant-...\n  ELEVENLABS_API_KEY=...\n")
        sys.exit(1)

    # Prevent uncaught thread exceptions from crashing the app
    def _thread_exc(args):
        print(f"[FixMe] Thread error: {args.exc_value}")
    threading.excepthook = _thread_exc

    app = FixMeUI()
    app.mainloop()


if __name__ == "__main__":
    main()
