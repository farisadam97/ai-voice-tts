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

TTS_MODEL_NAME = "chatterbox-turbo"
TTS_MODEL = os.path.join(_BASE_DIR, "models", "tts")
TTS_TOKENIZER = os.path.join(_BASE_DIR, "models", "tokenizer")
TTS_LANGUAGE = "Auto"
REF_AUDIO_PATH = os.path.join(_BASE_DIR, "voice_samples", "reference_audio.wav")
REF_TEXT_PATH = os.path.join(_BASE_DIR, "voice_samples", "reference_text.txt")

OUTPUT_DIR = os.path.join(_BASE_DIR, "output", "response_audio")

TTS_TEMPERATURE = 1.05        # Controls randomness. Higher (0.9-1.0) = more expressive/varied. Lower (0.5-0.7) = more consistent/stable.
TTS_TOP_P = 0.81             # Nucleus sampling. Lower (0.8) = more focused/predictable. Higher (1.0) = more diverse/creative.
TTS_TOP_K = 1000             # Limits candidate tokens. Lower (100-500) = fewer choices, safer. Higher = more variety.
TTS_REPETITION_PENALTY = 1.25 # Penalizes repeating sounds/phrases. Higher (1.3-1.5) = less repetitive. Lower (1.0) = no penalty.
TTS_MIN_P = 0              # Minimum probability filter. Higher (0.05-0.1) = filters out unlikely tokens, cleaner output.
TTS_NORM_LOUDNESS = False     # Normalizes output volume. True = consistent loudness. False = raw dynamic range.

AUDIO_OUTPUT_DEVICE = None
