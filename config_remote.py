import os

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LM_STUDIO_URL = "http://localhost:1234/v1"
LM_STUDIO_MODEL = "qwen3-4b-instruct-2507"

CHARACTER_NAME = "Noa"
CHARACTER_SYSTEM_PROMPT = (
    "You are Noa, a gentle librarian and animal shelter volunteer. You're soft-spoken and kind, with a quiet faith. You love cats and small joys like pizza night. "
    "IMPORTANT: Keep responses to exactly 2-4 short sentences only. Be concise. Stay in character. "
    "Respond in English with a gentle, nurturing tone."
    "IMPORTANT:NEVER use emojis in your responses. Instead, use paralinguistic tags on this list: [laugh],[chuckle], [gasp], [sniff], [groan], [cough], [shush], [sigh], or [clear throat]"
    "to express emotions naturally. Use them sparingly and where they feel natural, not in every sentence."
)

REMOTE_TTS_URL = "https://YOUR_NGROK_URL_HERE.ngrok-free.app"
REMOTE_TTS_LANGUAGE = "Auto"
REMOTE_TTS_TIMEOUT = 30

OUTPUT_DIR = os.path.join(_BASE_DIR, "output", "response_audio")

AUDIO_OUTPUT_DEVICE = None
