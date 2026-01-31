"""Bilingual text-to-speech using ElevenLabs API with Spanish translation via Claude."""

import os
import tempfile
import warnings

import anthropic

try:
    from elevenlabs import ElevenLabs
except ImportError:
    ElevenLabs = None

# Configurable voice IDs — update these with your preferred ElevenLabs voices
ENGLISH_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # "Rachel" - default English voice
SPANISH_VOICE_ID = "ThT5KcBeYPX3keUQqHPh"  # "Dorothy" - works well for Spanish

TRANSLATE_MODEL = "claude-sonnet-4-20250514"


def translate_to_spanish(text: str) -> str:
    """Translate English text to natural Spanish using Claude.

    Args:
        text: English text to translate.

    Returns:
        Translated Spanish text.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        warnings.warn("ANTHROPIC_API_KEY not set, returning original text")
        return text

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=TRANSLATE_MODEL,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Translate the following text to natural Spanish. "
                        "Return only the translation, nothing else:\n\n"
                        f"{text}"
                    ),
                }
            ],
        )
        return message.content[0].text.strip()
    except Exception as e:
        warnings.warn(f"Translation failed, using English: {e}")
        return text


def speak(text: str, lang: str = "en") -> None:
    """Convert text to speech and play it.

    For Spanish, translates the text first via Claude, then uses ElevenLabs
    with a Spanish voice.

    Args:
        text: The text to speak.
        lang: Language code - "en" for English, "es" for Spanish.
    """
    if ElevenLabs is None:
        print(f"[TTS] ({lang}): {text}")
        return

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print(f"[TTS] ({lang}): {text}")
        return

    # Translate if Spanish
    speak_text = text
    if lang == "es":
        speak_text = translate_to_spanish(text)

    voice_id = SPANISH_VOICE_ID if lang == "es" else ENGLISH_VOICE_ID

    try:
        client = ElevenLabs(api_key=api_key)
        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            text=speak_text,
            model_id="eleven_multilingual_v2",
        )

        # Collect audio bytes from generator
        audio_bytes = b"".join(audio_generator)

        # Save to temp file and play
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp.write(audio_bytes)
        tmp.close()

        # Play audio
        try:
            os.startfile(tmp.name)  # Windows
        except AttributeError:
            # Fallback for non-Windows (e.g., macOS during development)
            import subprocess
            subprocess.Popen(["open", tmp.name])

    except Exception as e:
        warnings.warn(f"TTS failed, printing instead: {e}")
        print(f"[TTS] ({lang}): {speak_text}")
