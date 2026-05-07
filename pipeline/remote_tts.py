import os
import time

import requests

import config_remote as config

_session = requests.Session()


def load_model() -> None:
    url = f"{config.REMOTE_TTS_URL}/health"
    print(f"[Remote TTS] Checking connection to {url}...")
    try:
        resp = _session.get(url, timeout=10)
        data = resp.json()
        print(f"[Remote TTS] Connected. Model: {data.get('model', 'unknown')}, Voice clone: {data.get('voice_clone', False)}")
    except requests.ConnectionError:
        print(f"[Remote TTS] ERROR: Cannot reach {config.REMOTE_TTS_URL}")
        print("[Remote TTS] Make sure the Kaggle notebook is running and ngrok tunnel is active.")
    except Exception as e:
        print(f"[Remote TTS] ERROR: {e}")


def synthesize(text: str, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    url = f"{config.REMOTE_TTS_URL}/tts"
    payload = {
        "text": text,
        "language": config.REMOTE_TTS_LANGUAGE,
    }

    t0 = time.time()
    resp = _session.post(url, json=payload, timeout=config.REMOTE_TTS_TIMEOUT)
    t1 = time.time()

    if resp.status_code != 200:
        try:
            err = resp.json().get("error", resp.text)
        except Exception:
            err = resp.text
        raise RuntimeError(f"Remote TTS error ({resp.status_code}): {err}")

    with open(output_path, "wb") as f:
        f.write(resp.content)

    print(f"[Remote TTS] {t1 - t0:.2f}s — {len(resp.content)} bytes received")
    return output_path
