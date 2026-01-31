"""Windows SAPI speech recognition with tkinter fallback."""

import threading
import warnings

AFFIRMATIVE_EN = {"yes", "yeah", "yep", "sure", "okay", "ok", "go ahead", "proceed", "do it"}
AFFIRMATIVE_ES = {"sí", "si", "claro", "dale", "adelante", "hazlo", "ok", "okay"}

NEGATIVE_EN = {"no", "nope", "nah", "skip", "don't", "cancel"}
NEGATIVE_ES = {"no", "cancelar", "saltar", "para"}


def is_affirmative(text: str, lang: str = "en") -> bool:
    """Check if the text is an affirmative response.

    Args:
        text: Transcribed text to check.
        lang: Language code - "en" or "es".

    Returns:
        True if the response is affirmative.
    """
    words = text.lower().strip()
    patterns = AFFIRMATIVE_ES if lang == "es" else AFFIRMATIVE_EN
    return words in patterns or any(p in words for p in patterns)


def is_negative(text: str, lang: str = "en") -> bool:
    """Check if the text is a negative response.

    Args:
        text: Transcribed text to check.
        lang: Language code - "en" or "es".

    Returns:
        True if the response is negative.
    """
    words = text.lower().strip()
    patterns = NEGATIVE_ES if lang == "es" else NEGATIVE_EN
    return words in patterns or any(p in words for p in patterns)


def _tkinter_fallback(mode: str = "permission", lang: str = "en") -> str:
    """Show a tkinter popup as fallback when voice recognition is unavailable.

    Args:
        mode: "permission" for yes/no buttons, "open" for text entry.
        lang: Language code for button labels.

    Returns:
        The selected option or entered text.
    """
    import tkinter as tk

    result = {"value": ""}

    def on_select(value):
        result["value"] = value
        root.destroy()

    root = tk.Tk()
    root.title("FixMe - Voice Input")
    root.attributes("-topmost", True)
    root.geometry("400x200")
    root.resizable(False, False)

    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 400) // 2
    y = (root.winfo_screenheight() - 200) // 2
    root.geometry(f"+{x}+{y}")

    if mode == "permission":
        yes_label = "Sí" if lang == "es" else "Yes"
        no_label = "No"
        question_label = "Hacer pregunta" if lang == "es" else "Ask a question"

        tk.Label(
            root,
            text="¿Proceder?" if lang == "es" else "Proceed?",
            font=("Segoe UI", 14),
        ).pack(pady=15)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame, text=yes_label, width=12, height=2,
            bg="#4CAF50", fg="white", font=("Segoe UI", 11),
            command=lambda: on_select("yes"),
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text=no_label, width=12, height=2,
            bg="#f44336", fg="white", font=("Segoe UI", 11),
            command=lambda: on_select("no"),
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            root, text=question_label, width=20,
            font=("Segoe UI", 10),
            command=lambda: on_select("__question__"),
        ).pack(pady=5)

    else:  # open mode
        prompt_text = "Escriba su pregunta:" if lang == "es" else "Type your question:"
        tk.Label(root, text=prompt_text, font=("Segoe UI", 12)).pack(pady=10)

        entry = tk.Entry(root, width=40, font=("Segoe UI", 11))
        entry.pack(pady=5)
        entry.focus_set()

        submit_label = "Enviar" if lang == "es" else "Submit"
        tk.Button(
            root, text=submit_label, width=15, height=2,
            font=("Segoe UI", 11),
            command=lambda: on_select(entry.get()),
        ).pack(pady=10)

        root.bind("<Return>", lambda e: on_select(entry.get()))

    root.mainloop()
    return result["value"]


def _try_sapi_listen(lang: str = "en", timeout: int = 10) -> str | None:
    """Attempt to listen using Windows SAPI speech recognition.

    Returns:
        Transcribed text, or None if SAPI is unavailable or no speech detected.
    """
    try:
        import win32com.client

        recognizer = win32com.client.Dispatch("SAPI.SpRecognizer")
        context = recognizer.CreateRecoContext()
        grammar = context.CreateGrammar()
        grammar.DictationSetState(1)  # Enable dictation

        # Set up event handling
        result_text = {"value": None}
        event = threading.Event()

        class ContextEvents:
            def OnRecognition(self, _stream_number, _stream_position, _recognition_type, recognition_result):
                result_text["value"] = recognition_result.PhraseInfo.GetText()
                event.set()

        # Connect events
        import win32com.client as wc
        wc.WithEvents(context, ContextEvents)

        # Wait for result or timeout
        event.wait(timeout=timeout)
        grammar.DictationSetState(0)

        return result_text["value"]

    except ImportError:
        return None
    except Exception as e:
        warnings.warn(f"SAPI recognition failed: {e}")
        return None


def listen(mode: str = "permission", lang: str = "en", timeout: int = 10) -> str:
    """Listen for user voice input, falling back to tkinter popup on timeout.

    Args:
        mode: "permission" for yes/no, "open" for free-form speech.
        lang: Language code - "en" or "es".
        timeout: Seconds to wait for voice input before showing fallback.

    Returns:
        Transcribed text or selected button value.
    """
    # Try SAPI first
    result = _try_sapi_listen(lang=lang, timeout=timeout)

    if result:
        return result

    # Fall back to tkinter
    return _tkinter_fallback(mode=mode, lang=lang)
