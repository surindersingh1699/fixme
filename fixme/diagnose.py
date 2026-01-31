"""Claude Vision API integration for IT issue diagnosis from screenshots."""

import base64
import json
import os

import anthropic

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2048

SYSTEM_PROMPT = """You are an IT support diagnostic assistant. You are given a screenshot of a user's Windows PC screen.

Analyze the screenshot and:
1. Diagnose any visible IT issue (error dialog, network problem indicator, system alert, etc.)
2. Categorize it into exactly ONE of these categories:
   - "wifi" (Wi-Fi disconnected, no internet, network error)
   - "dns" (DNS resolution failures, cannot reach websites but network connected)
   - "password" (credential prompts, password expired dialogs, credential errors)
   - "other" (anything else)
3. Provide step-by-step fix instructions using Windows commands.

Respond in JSON only, no markdown fences:
{
  "diagnosis": "Human-readable explanation of the issue seen on screen",
  "category": "wifi" | "dns" | "password" | "other",
  "fix_id": "toggle_wifi" | "flush_dns" | "restart_network" | "open_credential_manager" | null,
  "fix_description": "Human-readable description of the recommended fix",
  "steps": [
    {
      "step": 1,
      "description": "What this step does in plain language",
      "command": "the Windows command to execute",
      "needs_admin": false,
      "ui_highlight": {"element": "UI element name", "location": "taskbar right", "action": "circle"} or null
    }
  ]
}

If you cannot identify any IT issue on screen, set category to "other", fix_id to null, and steps to an empty array.
Valid ui_highlight locations: "taskbar right", "taskbar left", "taskbar center", "center", "top right", "top left".
Valid ui_highlight actions: "circle", "arrow", "box"."""


def diagnose_screenshot(image_path: str) -> dict:
    """Send a screenshot to Claude Vision API and get a structured IT diagnosis.

    Args:
        image_path: Path to a PNG screenshot file.

    Returns:
        Dict with diagnosis, category, fix_id, fix_description, and steps.

    Raises:
        FileNotFoundError: If image_path doesn't exist.
        ValueError: If the API response can't be parsed as JSON.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Screenshot not found: {image_path}")

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "What IT issue do you see on this screen? Diagnose and suggest a fix.",
                    },
                ],
            }
        ],
    )

    response_text = message.content[0].text

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse Claude response as JSON: {e}\nRaw response: {response_text}"
        ) from e
