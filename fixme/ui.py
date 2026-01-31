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
    "bg":              "#FFFFFF",
    "surface":         "#F7F7F8",
    "surface_hover":   "#EFEFEF",
    "sidebar_bg":      "#F4F4F5",
    "sidebar_hover":   "#E8E8EA",
    "sidebar_active":  "#DDDDE0",
    "border":          "#E5E5E7",
    "text":            "#0D0D0D",
    "text_secondary":  "#6B6B6F",
    "text_muted":      "#9A9A9F",
    "brand":           "#6366F1",
    "brand_light":     "#818CF8",
    "brand_dark":      "#4338CA",
    "brand_bg":        "#EEF2FF",
    "success":         "#10B981",
    "success_bg":      "#ECFDF5",
    "warning":         "#F59E0B",
    "warning_bg":      "#FFFBEB",
    "error":           "#EF4444",
    "error_bg":        "#FEF2F2",
    "orb":             "#6366F1",
    "orb_ring_1":      "#818CF8",
    "orb_ring_2":      "#A78BFA",
    "orb_ring_3":      "#C084FC",
    "orb_process":     "#8B5CF6",
    "bubble_user":     "#6366F1",
    "bubble_ai":       "#F7F7F8",
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
        self.orb.set_state("listening")
        self._orb_lbl.configure(text="Listening...", fg=P["brand"])
        self._set_status("Listening", P["brand"])
        threading.Thread(target=self._voice_work, daemon=True).start()

    def _voice_work(self):
        try:
            from fixme import voice_input
            r = voice_input.listen(mode="open", lang=self.sidebar.lang_code, timeout=10)
            if r and r.strip():
                self.after(0, lambda: self._msg(r, "user"))
                self.after(0, lambda: self.orb.set_state("processing"))
                self.after(0, lambda: self._orb_lbl.configure(text="Thinking...", fg=P["orb_process"]))
                self.after(0, lambda: self._set_status("Processing", P["orb_process"]))
                self._handle(r)
            else:
                self._reset()
        except Exception:
            self.after(0, lambda: self.orb.set_state("error"))
            self.after(0, lambda: self._orb_lbl.configure(text="Couldn't hear \u2014 tap again", fg=P["error"]))
            self.after(2500, self._reset)

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
        try:
            import anthropic
            cl = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            lang = self.sidebar.lang_code
            names = {"en": "English", "es": "Spanish", "pa": "Punjabi",
                     "hi": "Hindi", "fr": "French"}
            m = cl.messages.create(
                model="claude-sonnet-4-20250514", max_tokens=512,
                system=(
                    f"You are FixMe, a warm IT support assistant. Respond in {names.get(lang, 'English')}. "
                    "Keep responses concise (2-3 sentences). If the user describes a "
                    "computer issue, suggest using the Diagnose Screen button. "
                    "Be empathetic \u2014 many users are frustrated about tech issues."
                ),
                messages=[{"role": "user", "content": text}],
            )
            reply = m.content[0].text.strip()
        except Exception:
            reply = "I had trouble connecting. Try the Diagnose Screen button instead."
        self.after(0, lambda: self._msg(reply, "assistant"))
        self.after(0, lambda: self._speak(reply))
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

                from fixme import voice_input
                resp = voice_input.listen(mode="open", lang=lang, timeout=15)
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
        except Exception as e:
            self.after(0, lambda: self._msg(f"Diagnosis failed: {e}", "assistant"))
        finally:
            self._busy = False
            self.after(0, lambda: self._dbtn.configure(state="normal", text="Diagnose Screen"))
            self._reset()

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

    app = FixMeUI()
    app.mainloop()


if __name__ == "__main__":
    main()
