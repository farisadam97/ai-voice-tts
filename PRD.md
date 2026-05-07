# AI VTuber — Project PRD & README

> **Iteration 1 Scope:** Voice clone pipeline — text input → LLM response → cloned voice audio output

---

## Overview

A local AI VTuber system inspired by Neuro-sama, running entirely on consumer hardware. The character responds to user input (text or voice) using a cloned anime character voice, powered by a local LLM with a defined personality.

This document covers **Iteration 1** only: getting a working text-in → cloned-voice-out pipeline before adding avatar, STT, memory, and streaming features.

---

## Goals

- Clone a target anime character's voice from official game audio lines
- Accept text input from the user
- Generate a character-consistent response via a local LLM
- Synthesize the response in the cloned voice using Qwen3-TTS
- Output audio to speakers or virtual audio cable

---

## Non-Goals (Iteration 1)

The following are explicitly out of scope for this iteration:

- Live2D avatar / VTube Studio integration
- Voice (STT) input
- Long-term memory / vector DB
- Streaming to Twitch/OBS
- Real-time low-latency optimization

---

## System Architecture

```
[User Text Input]
       │
       ▼
[LM Studio API]  ──  Character system prompt
       │
       ▼
[LLM Response Text]
       │
       ▼
[Qwen3-TTS Voice Clone]  ──  Reference audio + transcript
       │
       ▼
[WAV Audio Output]  →  Speakers / Virtual Audio Cable
```

---

## Hardware Requirements

| Component | Minimum | Recommended |
|---|---|---|
| GPU | 6GB VRAM | 16GB VRAM (RTX 5070 Ti) |
| RAM | 16GB | 32GB |
| Storage | 10GB free | 20GB free |
| OS | Windows 10/11 | Windows 11 |

---

## Tech Stack

| Component | Tool | Version |
|---|---|---|
| TTS / Voice Clone | Qwen3-TTS | `12Hz-0.6B-Base` |
| LLM Backend | LM Studio | Latest |
| LLM Model | Qwen3-4B-Instruct-2507 | via LM Studio |
| Web Search | LM Studio MCP (Web Search) | via LM Studio |
| Audio Playback | soundfile, sounddevice | Latest |
| Virtual Audio | VB-Audio Virtual Cable | Free |
| Language | Python | 3.12 |

---

## Project Structure

```
ai-vtuber/
├── README.md
├── requirements.txt
├── config.py                  # Model paths, API endpoints, character config
├── main.py                    # Entry point
├── pipeline/
│   ├── __init__.py
│   ├── llm.py                 # LM Studio API wrapper
│   ├── tts.py                 # Qwen3-TTS voice clone wrapper
│   └── audio_player.py        # Audio playback to speakers / virtual cable
├── models/
│   ├── tokenizer/             # Qwen3-TTS-Tokenizer-12Hz (local cache)
│   └── tts/                   # Qwen3-TTS-12Hz-0.6B-Base (local cache)
├── voice_samples/
│   ├── raw/                   # Original game audio clips
│   ├── cleaned/               # Demucs-processed vocals
│   └── reference.wav          # Final reference clip used for cloning
├── output/
│   └── response_audio/        # Generated WAV files
└── scripts/
    └── prepare_voice.py       # Voice sample cleaning utility
```

---

## Setup

### 1. Environment

```bash
conda create -n ai-vtuber python=3.12 -y
conda activate ai-vtuber
pip install -U qwen-tts soundfile openai demucs
```

### 2. LM Studio

1. Download and install [LM Studio](https://lmstudio.ai)
2. Download a model — recommended: `Qwen3-4B-Instruct-2507` (GGUF, Q4_K_M)
3. Start the local server: **Local Server tab → Start Server**
4. Default endpoint: `http://localhost:1234/v1`

#### MCP Web Search (optional)

To enable web search for the LLM responses:

1. In LM Studio, go to **Developer tab → MCP Servers**
2. Enable the **Web Search** MCP server
3. The LLM will automatically use it when it needs to look up information
4. No code changes needed — LM Studio handles tool calls transparently

### 3. Qwen3-TTS Model

Models download automatically on first run. To pre-download manually:

```bash
pip install -U huggingface_hub
huggingface-cli download Qwen/Qwen3-TTS-Tokenizer-12Hz --local-dir ./models/tokenizer
huggingface-cli download Qwen/Qwen3-TTS-12Hz-0.6B-Base --local-dir ./models/tts
```

---

## Voice Sample Preparation

### Requirements for a good reference clip

- Duration: **3–10 seconds**
- Clean speech — no background music or SFX
- Neutral to mildly expressive tone (avoid whispering or shouting)
- Format: **WAV, mono, 16kHz or 24kHz**

### Cleaning game audio with Demucs

Game voice lines often have background music mixed in. Use Demucs to isolate vocals:

```bash
pip install demucs
demucs --two-stems=vocals voice_samples/raw/your_clip.wav
# Output: htdemucs/your_clip/vocals.wav
```

Copy the best cleaned clip to `voice_samples/reference.wav` and write its exact transcript to `voice_samples/reference_text.txt`.

### Tips

- Pick a clip where the character speaks a full sentence clearly
- The transcript must be **exact** — Qwen3-TTS cloning quality degrades with transcript mismatch
- Test multiple clips and keep the one that produces the most accurate clone

---

## Configuration

Edit `config.py` before running:

```python
# LM Studio
LM_STUDIO_URL = "http://localhost:1234/v1"
LM_STUDIO_MODEL = "qwen3-4b-instruct-2507"  # match what's loaded in LM Studio

# Character
CHARACTER_NAME = "Your Character Name"
CHARACTER_SYSTEM_PROMPT = """
You are [character name]. [Brief personality description].
Keep responses short, 1-3 sentences. Stay in character at all times.
"""

# Voice Clone
TTS_MODEL = "./models/tts"
TTS_TOKENIZER = "./models/tokenizer"
TTS_LANGUAGE = "Auto"  # "Auto", "Japanese", "English", etc.
REF_AUDIO_PATH = "voice_samples/reference.wav"
REF_TEXT_PATH  = "voice_samples/reference_text.txt"

# Output
OUTPUT_DIR = "output/response_audio"
```

---

## Core Modules

### `pipeline/llm.py`

```python
from openai import OpenAI
import config

client = OpenAI(base_url=config.LM_STUDIO_URL, api_key="lm-studio")

def get_response(user_input: str, history: list | None = None) -> str:
    history = history or []
    messages = [{"role": "system", "content": config.CHARACTER_SYSTEM_PROMPT}]
    messages += history[-10:]  # last 5 exchanges
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=config.LM_STUDIO_MODEL,
        messages=messages,
        temperature=0.8,
        max_tokens=200,
    )
    return response.choices[0].message.content
```

### `pipeline/tts.py`

```python
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel
import config
import os

model = None
voice_clone_prompt = None

def load_model():
    global model, voice_clone_prompt
    model = Qwen3TTSModel.from_pretrained(
        config.TTS_MODEL,
        device_map="cuda:0",
        dtype=torch.bfloat16,
        attn_implementation="sdpa",
    )
    with open(config.REF_TEXT_PATH, "r", encoding="utf-8") as f:
        ref_text = f.read().strip()

    voice_clone_prompt = model.create_voice_clone_prompt(
        ref_audio=config.REF_AUDIO_PATH,
        ref_text=ref_text,
    )

def synthesize(text: str, output_path: str) -> str:
    wavs, sr = model.generate_voice_clone(
        text=text,
        language=config.TTS_LANGUAGE,
        voice_clone_prompt=voice_clone_prompt,
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, wavs[0], sr)
    return output_path
```

### `main.py`

```python
import os
import time
import soundfile as sf
import sounddevice as sd
import pipeline.llm as llm
import pipeline.tts as tts

def play_audio(filepath: str):
    data, samplerate = sf.read(filepath)
    sd.play(data, samplerate)
    sd.wait()

def main():
    print("Loading TTS model...")
    tts.load_model()
    print("Ready.\n")

    history = []

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit"]:
            break

        response = llm.get_response(user_input, history)
        print(f"Character: {response}\n")

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})

        output_path = f"output/response_audio/{int(time.time())}.wav"
        tts.synthesize(response, output_path)
        print(f"Audio saved: {output_path}")

        print("Playing audio...")
        play_audio(output_path)

if __name__ == "__main__":
    main()
```

---

## Running

```bash
# Make sure LM Studio server is running first
conda activate ai-vtuber
python main.py
```

---

## VRAM Usage (Iteration 1)

| Model | Estimated VRAM |
|---|---|
| Qwen3-TTS 0.6B-Base | ~2–3 GB |
| Qwen3-4B (LM Studio) | ~2 GB |
| **Total** | **~4–5 GB** |

Runs comfortably on 8GB. Leaves ample headroom for running a game alongside.

---

## Known Limitations (Iteration 1)

- Text input only — no microphone/STT support yet
- No conversation memory beyond session history buffer
- No avatar or lip sync
- Audio plays after full synthesis — no streaming

---

## Roadmap

| Iteration | Features |
|---|---|
| **1 (current)** | Text input → LLM (Qwen3-4B + MCP web search) → F5-TTS voice clone → WAV output + audio playback + Web UI |
| 2 | STT voice input (faster-whisper), audio playback via virtual cable |
| 3 | VTube Studio avatar + lip sync via VB-Audio Virtual Cable |
| 4 | Long-term memory with ChromaDB + embedding model |
| 5 | OBS streaming integration, real-time optimization |

---

## Dependencies (`requirements.txt`)

```
qwen-tts
openai
soundfile
sounddevice
demucs
torch
```

---

## Notes

- Qwen3-TTS cloning quality is highly sensitive to `ref_text` accuracy. Always transcribe the reference audio precisely.
- LM Studio must have its local server running before `main.py` is started.
- Language is configured in `config.py` via `TTS_LANGUAGE`. Use `"Auto"` for automatic detection, or set explicitly (e.g. `"Japanese"`, `"English"`).
- The `create_voice_clone_prompt` call in `load_model()` runs once at startup — this is intentional to avoid per-call overhead.
- SDPA (Scaled Dot Product Attention) is used via `attn_implementation="sdpa"` for reduced VRAM and faster inference. Built into PyTorch 2.x — no extra install needed.
- MCP web search is configured entirely within LM Studio — no code changes needed. The LLM will use it automatically when needed.
- For Windows + RTX 50-series (Blackwell), install PyTorch with CUDA 12.8: `pip install --pre torch torchaudio --index-url https://download.pytorch.org/whl/cu128  