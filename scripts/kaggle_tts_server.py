# ============================================================
# CELL 1 — Install dependencies
# ============================================================
# !pip install qwen-tts pyngrok flask soundfile

# ============================================================
# CELL 2 — Load Qwen3-TTS 1.7B-Base model
# ============================================================
import torch
from qwen_tts import Qwen3TTSModel

print("[TTS] Loading Qwen3-TTS 1.7B-Base model...")
model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    device_map="cuda:0",
    dtype=torch.bfloat16,
    attn_implementation="sdpa",
)
print("[TTS] Model loaded.")

# ============================================================
# CELL 3 — Upload reference audio and create voice clone prompt
# ============================================================
#
# HOW TO ADD YOUR REFERENCE AUDIO:
#   Option A: Create a Kaggle Dataset with your voice files,
#             attach it to this notebook, then set the path below.
#   Option B: Use the file upload widget:
#             from google.colab import files (works on Colab only)
#   Option C: For quick testing, paste a direct URL to a .wav file.
#
# After uploading, set REF_AUDIO_PATH to the file location.
# Examples:
#   REF_AUDIO_PATH = "/kaggle/input/your-dataset-name/reference_audio.wav"
#   REF_AUDIO_PATH = "https://example.com/reference_audio.wav"
# ============================================================

import os

REF_AUDIO_PATH = None
REF_TEXT = "Since our last adventure when we were searching for Cetus the Tidebreaker. I've been wanting to find a way to thank you."

voice_clone_prompt = None

if REF_AUDIO_PATH and (os.path.exists(REF_AUDIO_PATH) or REF_AUDIO_PATH.startswith("http")):
    print(f"[Voice] Creating voice clone prompt from: {REF_AUDIO_PATH}")
    voice_clone_prompt = model.create_voice_clone_prompt(
        ref_audio=REF_AUDIO_PATH,
        ref_text=REF_TEXT,
    )
    print("[Voice] Voice clone prompt ready.")
else:
    print("[Voice] No reference audio set. Will generate without voice cloning.")
    print("[Voice] To enable cloning, set REF_AUDIO_PATH in Cell 3.")

# ============================================================
# CELL 4 — Start Flask API server + ngrok tunnel
# ============================================================
import io
import os
import soundfile as sf
from flask import Flask, request, jsonify, send_file
from pyngrok import ngrok

NGROK_TOKEN = "YOUR_NGROK_TOKEN_HERE"
ngrok.set_auth_token(NGROK_TOKEN)

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model": "Qwen3-TTS-12Hz-1.7B-Base",
        "voice_clone": voice_clone_prompt is not None,
    })


@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json()
    text = data.get("text", "").strip()
    language = data.get("language", "Auto")

    if not text:
        return jsonify({"error": "Empty text"}), 400

    try:
        if voice_clone_prompt:
            wavs, sr = model.generate_voice_clone(
                text=text,
                language=language,
                voice_clone_prompt=voice_clone_prompt,
            )
        else:
            wavs, sr = model.generate_voice_clone(
                text=text,
                language=language,
            )

        buf = io.BytesIO()
        sf.write(buf, wavs[0], sr, format="WAV")
        buf.seek(0)

        return send_file(buf, mimetype="audio/wav")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


ngrok.kill()
public_url = ngrok.connect(5000, bind_tls=True)

print(f"\n{'='*60}")
print(f"  TTS Server is LIVE!")
print(f"  URL: {public_url}")
print(f"  Health: GET  {public_url}/health")
print(f"  TTS:    POST {public_url}/tts")
print(f"  Body:   {{'text': '...', 'language': 'Auto'}}")
print(f"{'='*60}")
print(f"\n  Copy this URL to your local config.py:")
print(f"  REMOTE_TTS_URL = \"{public_url}\"")
print(f"{'='*60}\n")

app.run(host="0.0.0.0", port=5000, debug=False)
