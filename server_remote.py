import os
import time
import uuid
import signal
import sys

from flask import Flask, request, jsonify, send_from_directory

import pipeline.llm as llm
import pipeline.remote_tts as tts
import config_remote as config

app = Flask(__name__, static_folder="static")

_history: list[dict] = []


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    t0 = time.time()
    response = llm.get_response(user_input, _history)
    t1 = time.time()
    if not response:
        return jsonify({"error": "LLM returned empty response. Is LM Studio running?"}), 502

    print(f"[Timing] LLM: {t1 - t0:.2f}s | Response length: {len(response)} chars")

    _history.append({"role": "user", "content": user_input})
    _history.append({"role": "assistant", "content": response})
    if len(_history) > 20:
        del _history[: len(_history) - 20]

    audio_filename = f"{uuid.uuid4().hex}.wav"
    audio_path = os.path.join(config.OUTPUT_DIR, audio_filename)

    try:
        tts.synthesize(response, audio_path)
    except Exception as e:
        return jsonify({"text": response, "audio": None, "error": str(e)}), 500

    t2 = time.time()
    print(f"[Timing] TTS: {t2 - t1:.2f}s | Total: {t2 - t0:.2f}s")

    return jsonify({
        "text": response,
        "audio": f"/audio/{audio_filename}",
        "character": config.CHARACTER_NAME,
    })


@app.route("/audio/<path:filename>")
def audio(filename):
    return send_from_directory(config.OUTPUT_DIR, filename)


@app.route("/api/status")
def status():
    return jsonify({
        "character": config.CHARACTER_NAME,
        "mode": "remote",
        "remote_url": config.REMOTE_TTS_URL,
    })


def cleanup(signum=None, frame=None):
    print("\n[Shutdown] Bye!")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print(f"=== {config.CHARACTER_NAME} VTuber TTS — Remote Mode ===\n")
    print("Connecting to remote TTS server...")
    tts.load_model()
    print("")

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    print("Server starting at http://localhost:5000")
    print("Press Ctrl+C to stop.\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
