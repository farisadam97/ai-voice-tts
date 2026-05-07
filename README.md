# AI Voice TTS

A local AI VTuber voice pipeline — text input to LLM response to cloned voice audio output, running entirely on consumer hardware.

Powered by **Chatterbox-Turbo TTS** for voice cloning and **LM Studio** for local LLM inference. Inspired by Neuro-sama.

## Architecture

```
[User Text Input]
       │
       ▼
[LM Studio API] ── Character system prompt
       │
       ▼
[LLM Response Text]
       │
       ▼
[Chatterbox-Turbo TTS] ── Reference audio (voice clone)
       │
       ▼
[WAV Audio Output] → Speakers / Virtual Audio Cable
```

## Features

- **Voice cloning** from a short reference audio clip
- **Local LLM** via LM Studio with configurable character personality
- **Web UI** with real-time chat and audio playback
- **Remote TTS mode** — offload TTS to a Kaggle/Colab GPU via ngrok tunnel
- **CLI mode** for terminal-based interaction
- **Configurable TTS parameters** — temperature, top-p, top-k, repetition penalty

## Hardware Requirements

| Component | Minimum | Recommended |
|---|---|---|
| GPU | 6GB VRAM | 8GB+ VRAM |
| RAM | 16GB | 32GB |
| Storage | 5GB free | 10GB free |
| OS | Windows 10/11 | Windows 11 |

## Tech Stack

| Component | Tool |
|---|---|
| TTS / Voice Clone | Chatterbox-Turbo TTS |
| LLM Backend | LM Studio |
| Web Server | Flask |
| Audio Playback | soundfile + sounddevice |
| Language | Python 3.12 |

## Project Structure

```
ai-voice-tts/
├── main.py                    # CLI entry point
├── server.py                  # Web UI server (local TTS)
├── server_remote.py           # Web UI server (remote TTS)
├── config.py                  # Local mode config
├── config_remote.py           # Remote mode config
├── requirements.txt
├── pipeline/
│   ├── llm.py                 # LM Studio API wrapper
│   ├── tts.py                 # Chatterbox-Turbo TTS wrapper
│   ├── remote_tts.py          # Remote TTS via HTTP
│   └── audio_player.py        # Audio playback
├── static/
│   └── index.html             # Web UI
├── scripts/
│   ├── kaggle_tts_server.py   # Kaggle notebook for remote TTS
│   ├── prepare_voice.py       # Voice sample cleaning utility
│   ├── benchmark_chatterbox.py
│   └── test_tts.py
├── models/                    # (gitignored) TTS model files
├── voice_samples/             # (gitignored) Reference audio
└── output/                    # (gitignored) Generated audio
```

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/farisadam97/ai-voice-tts.git
cd ai-voice-tts
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

For CUDA support (RTX 50-series / Blackwell):

```bash
pip install --pre torch torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### 2. LM Studio

1. Download and install [LM Studio](https://lmstudio.ai)
2. Download a model — recommended: `Qwen3-4B-Instruct-2507` (GGUF, Q4_K_M)
3. Start the local server: **Local Server tab → Start Server**
4. Default endpoint: `http://localhost:1234/v1`

### 3. Prepare voice samples

Place a reference audio clip (3–10 seconds, clean speech, WAV format) at:

```
voice_samples/reference_audio.wav
```

Write the exact transcript to:

```
voice_samples/reference_text.txt
```

If the source has background music, use Demucs to isolate vocals:

```bash
pip install demucs
demucs --two-stems=vocals voice_samples/raw/your_clip.wav
```

## Usage

### CLI Mode

```bash
python main.py
```

Type messages in the terminal. The character responds with text and plays cloned voice audio.

### Web UI Mode (Local TTS)

```bash
python server.py
```

Open `http://localhost:5000` in your browser.

### Web UI Mode (Remote TTS)

Run the TTS server on a remote GPU (e.g., Kaggle notebook):

```bash
# In Kaggle notebook — see scripts/kaggle_tts_server.py
```

Then locally:

```bash
python server_remote.py
```

Set your ngrok URL in `config_remote.py`:

```python
REMOTE_TTS_URL = "https://your-ngrok-url.ngrok-free.app"
```

## Configuration

Edit `config.py` to customize:

```python
# LLM
LM_STUDIO_URL = "http://localhost:1234/v1"
LM_STUDIO_MODEL = "qwen3-4b-instruct-2507"

# Character
CHARACTER_NAME = "Noa"
CHARACTER_SYSTEM_PROMPT = "..."

# TTS parameters
TTS_TEMPERATURE = 1.05
TTS_TOP_P = 0.81
TTS_TOP_K = 1000
TTS_REPETITION_PENALTY = 1.25

# Audio output device (None = default)
AUDIO_OUTPUT_DEVICE = None
```

Copy `.env.example` to `.env` for environment-based configuration.

## API Endpoints (Web UI Server)

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Web UI |
| `/api/chat` | POST | Send message, get response + audio |
| `/api/status` | GET | Server status |
| `/audio/<filename>` | GET | Serve generated audio file |

### Example request

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

Response:

```json
{
  "text": "Oh, hi there! It's so nice to see you.",
  "audio": "/audio/abc123.wav",
  "character": "Noa"
}
```

## License

This project is for educational and personal use. Voice cloning carries ethical responsibilities — only clone voices you have permission to use.
