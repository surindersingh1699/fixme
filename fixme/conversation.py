"""Voice conversation flow orchestrator enforcing ask-before-every-action permission."""

import os
import warnings

import anthropic

from fixme.voice_input import is_affirmative, is_negative

MODEL = "claude-sonnet-4-20250514"


class ConversationFlow:
    """Orchestrates voice-guided IT fix execution with per-step permission."""

    def __init__(self, lang, tts, voice_input_module, overlay, fixes):
        """Initialize the conversation flow.

        Args:
            lang: Language code ("en" or "es").
            tts: The tts module (must have speak function).
            voice_input_module: The voice_input module (must have listen function).
            overlay: An Overlay instance.
            fixes: The fixes module (must have execute function).
        """
        self.lang = lang
        self.tts = tts
        self.voice_input = voice_input_module
        self.overlay = overlay
        self.fixes = fixes

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        self._client = anthropic.Anthropic(api_key=api_key) if api_key else None

    def run_fix(self, diagnosis_result: dict) -> None:
        """Execute a diagnosed fix with per-step voice permission.

        Args:
            diagnosis_result: Dict from diagnose_screenshot() with diagnosis,
                              steps, etc.
        """
        steps = diagnosis_result.get("steps", [])
        diagnosis = diagnosis_result.get("diagnosis", "Unknown issue")

        if not steps:
            self.tts.speak(
                f"I found an issue: {diagnosis}. However, there are no automated "
                "fix steps available. You may need to resolve this manually.",
                self.lang,
            )
            return

        # Announce the diagnosis
        self.tts.speak(
            f"I found the issue: {diagnosis}. "
            f"I have {len(steps)} steps to fix it. Let's go through each one.",
            self.lang,
        )

        fixes_applied = 0

        for i, step in enumerate(steps):
            step_num = i + 1
            description = step.get("description", "Unknown step")
            command = step.get("command", "")
            needs_admin = step.get("needs_admin", False)
            ui_highlight = step.get("ui_highlight")

            # Show overlay
            self.overlay.show_step(step_num, len(steps), description, ui_highlight)

            # Ask permission
            permission = self._ask_permission(step_num, step)

            if permission == "yes":
                self.tts.speak(
                    f"Executing step {step_num}...",
                    self.lang,
                )
                success, msg = self.fixes.execute(command, needs_admin)

                if success:
                    self.overlay.show_success(step_num)
                    self.tts.speak(
                        f"Step {step_num} complete. {msg}",
                        self.lang,
                    )
                    fixes_applied += 1
                else:
                    self.tts.speak(
                        f"Step {step_num} failed: {msg}. Moving on.",
                        self.lang,
                    )

            elif permission == "skip":
                self.tts.speak(f"Skipping step {step_num}.", self.lang)

            elif permission == "abort":
                self.tts.speak("Stopping the fix process.", self.lang)
                self.overlay.clear_step()
                break

            self.overlay.clear_step()

        # Summary
        if fixes_applied == 0:
            self.tts.speak("No fixes were applied.", self.lang)
        else:
            self.tts.speak(
                f"All done! {fixes_applied} of {len(steps)} steps were applied. "
                "The fix process is complete.",
                self.lang,
            )

    def _ask_permission(self, step_num: int, step: dict) -> str:
        """Ask the user for permission to execute a step.

        Loops until a clear yes/no/abort is received. Questions from the user
        are answered via Claude and then permission is re-asked.

        Args:
            step_num: The current step number.
            step: The step dict with description, command, etc.

        Returns:
            "yes", "skip", or "abort".
        """
        description = step.get("description", "Unknown step")

        while True:
            self.tts.speak(
                f"Step {step_num}: I want to {description}. "
                "Shall I proceed? Say yes, no, or ask me a question.",
                self.lang,
            )

            response = self.voice_input.listen(
                mode="open", lang=self.lang, timeout=15
            )

            if not response or not response.strip():
                # No response, ask again
                continue

            response_lower = response.lower().strip()

            if is_affirmative(response, self.lang):
                return "yes"

            if is_negative(response, self.lang):
                return "skip"

            # Check for abort keywords
            abort_keywords = {"stop", "abort", "quit", "exit", "para", "detener"}
            if any(kw in response_lower for kw in abort_keywords):
                return "abort"

            # User asked a question — answer it
            if response_lower == "__question__":
                # Came from tkinter "Ask a question" button, need to get actual question
                self.tts.speak("What would you like to know?", self.lang)
                response = self.voice_input.listen(
                    mode="open", lang=self.lang, timeout=15
                )

            answer = self._answer_question(response, step)
            self.tts.speak(answer, self.lang)
            # Loop back to re-ask permission

    def _answer_question(self, question: str, step: dict) -> str:
        """Answer a user question about the current fix step using Claude.

        Args:
            question: The user's question.
            step: The current step dict for context.

        Returns:
            Claude's answer as a string.
        """
        if not self._client:
            return (
                "Sorry, I cannot answer questions right now because the API "
                "is not configured."
            )

        description = step.get("description", "Unknown step")
        command = step.get("command", "Unknown command")

        try:
            message = self._client.messages.create(
                model=MODEL,
                max_tokens=512,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "You are helping a user through an IT fix on their Windows PC. "
                            "They are on a step that will do the following:\n\n"
                            f"Step description: {description}\n"
                            f"Command: {command}\n\n"
                            f"The user asks: {question}\n\n"
                            "Answer helpfully, concisely, and in plain language. "
                            "If they ask about safety, explain whether the action is "
                            "reversible and what risks exist."
                        ),
                    }
                ],
            )
            return message.content[0].text.strip()
        except Exception as e:
            warnings.warn(f"Question answering failed: {e}")
            return "Sorry, I couldn't answer that. Let me ask again about this step."
