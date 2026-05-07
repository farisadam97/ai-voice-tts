# Implementation Plans — All Iterations

---

## Iteration 1 — Voice Clone Pipeline

> Text input → LLM response → Qwen3-TTS voice clone → WAV output + audio playback

### Scope

- Clone a target anime character's voice from game audio lines
- Accept text input from user via CLI REPL
- Generate character-consistent response via local LLM (Qwen3-4B via LM Studio)
- Synthesize response in cloned voice using Qwen3-TTS 0.6B-Base
- Play audio to speakers or virtual audio cable
- MCP web search enabled via LM Studio (optional, no code needed)

### Files to Create

| Order | File | Purpose |
|---|---|---|
| 1 | `requirements.txt` | Python dependencies |
| 2 | `config.py` | All configuration constants |
| 3 | `pipeline/__init__.py` | Package init |
| 4 | `pipeline/llm.py` | LM Studio API wrapper |
| 5 | `pipeline/tts.py` | Qwen3-TTS voice clone wrapper |
| 6 | `pipeline/audio_player.py` | Audio playback to speakers / virtual cable |
| 7 | `main.py` | Entry point, REPL loop |
| 8 | `scripts/prepare_voice.py` | Demucs voice cleaning utility |

### Directory Structure

```
vtuber-tts/
├── PRD.md
├── PLAN.md
├── requirements.txt
├── config.py
├── main.py
├── pipeline/
│   ├── __init__.py
│   ├── llm.py
│   ├── tts.py
│   └── audio_player.py
├── models/
│   ├── tokenizer/
│   └── tts/
├── voice_samples/
│   ├── raw/
│   ├── cleaned/
│   └── reference.wav
├── output/
│   └── response_audio/
└── scripts/
    └── prepare_voice.py
```

### Module Details

#### `config.py`

Configuration constants organized by section:

- **LM Studio** — URL endpoint, model name (`qwen3-4b-instruct-2507`)
- **Character** — name, system prompt (personality + response length rules)
- **Voice Clone** — TTS model path (`./models/tts`), tokenizer path (`./models/tokenizer`), language (`"Auto"`), reference audio path, reference text path
- **Output** — directory for generated WAV files
- **Audio** — output device name (`None` = system default, or virtual cable name)

#### `pipeline/llm.py`

LM Studio API wrapper using the OpenAI Python client:

- `get_response(user_input: str, history: list | None = None) -> str`
- Builds messages array: system prompt + last 10 history entries + new user input
- Calls LM Studio chat completions endpoint (OpenAI-compatible)
- Parameters: `temperature=0.8`, `max_tokens=200`

**Error handling:**
- `ConnectionError` → "LM Studio server not reachable. Make sure it's running on {url}"
- Request timeout → clear timeout message
- Empty response → warning + fallback empty string

#### `pipeline/tts.py`

F5-TTS voice clone wrapper:

- `load_model()` — loads F5-TTS model (`F5TTS_v1_Base`), caches reference audio processing
- `synthesize(text: str, output_path: str) -> str` — generates cloned voice audio, saves WAV

**Performance:**
- Short text (30 chars): ~4s (2.2x realtime)
- Medium text (135 chars): ~2s (0.24x realtime — faster than realtime)
- Flow-matching architecture (non-autoregressive) — significantly faster than Qwen3-TTS

**Error handling:**
- Missing reference audio/text file → warning, falls back to no-clone mode
- CUDA OOM → `RuntimeError` with suggestion to close other GPU processes

#### `pipeline/audio_player.py`

Audio playback module using `soundfile` + `sounddevice`:

- `play_audio(filepath: str, device: str | None = None)` — read WAV, play to output device
- `list_devices()` — print available audio output devices (for finding virtual cable name)
- Device `None` = system default speakers
- Device `"CABLE Input"` (or similar) = route to VB-Audio Virtual Cable

#### `main.py`

Entry point that ties the pipeline together:

- Startup: load TTS model (with progress messages)
- REPL loop:
  1. Read user input
  2. Get LLM response
  3. Print character response
  4. Synthesize audio via TTS
  5. Save WAV to output directory
  6. Play audio
  7. Update session history
- Exit on `quit`/`exit` or `Ctrl+C`
- History: session-only, keeps last 10 messages (5 exchanges)

**Error handling:**
- `KeyboardInterrupt` → clean shutdown, print goodbye
- Pipeline errors → print error message, continue loop (don't crash)

#### `scripts/prepare_voice.py`

CLI utility for cleaning game audio with Demucs:

- Input: path to raw audio file (positional argument)
- Output: cleaned vocals saved to `voice_samples/cleaned/`
- Validates input is a WAV file
- Runs `demucs --two-stems=vocals` under the hood
- Prints instructions: copy best result to `voice_samples/reference.wav` and write transcript

### Dependencies

```
qwen-tts
openai
soundfile
sounddevice
demucs
torch
```

**Note:** F5-TTS model is cached by HuggingFace in `~/.cache/huggingface/hub/`. The original Qwen3-TTS models in `./models/` are no longer used by the active pipeline but are kept as fallback.
**Note:** On Windows + RTX 50-series (Blackwell), install PyTorch with CUDA 12.8 first:
```bash
pip install --pre torch torchaudio --index-url https://download.pytorch.org/whl/cu128
```

**Models are stored locally** in `./models/` (not global HuggingFace cache). Pre-download:
```bash
huggingface-cli download Qwen/Qwen3-TTS-Tokenizer-12Hz --local-dir ./models/tokenizer
huggingface-cli download Qwen/Qwen3-TTS-12Hz-0.6B-Base --local-dir ./models/tts
```

### Prerequisites Before Running

1. **Conda environment** created and activated (`python=3.12`)
2. **LM Studio** installed, Qwen3-4B model downloaded, local server running
3. **Reference audio** placed at `voice_samples/reference.wav`
4. **Reference transcript** written to `voice_samples/reference_text.txt`
5. **PyTorch + CUDA 12.8** installed (for GPU inference on RTX 50-series)
6. **Qwen3-TTS models** pre-downloaded to `./models/tts` and `./models/tokenizer` (local, not global cache)

### Verification Steps

1. All imports work (`python -c "import pipeline.llm, pipeline.tts, pipeline.audio_player"`)
2. Config loads without errors
3. `pipeline/audio_player.py list_devices` shows available audio devices
4. LM Studio connection works (start server, send a test message)
5. TTS model loads and generates audio from a test string
6. Full pipeline: type text → get response → hear audio

### Out of Scope

- Live2D avatar / VTube Studio
- Voice (STT) input
- Long-term memory / vector DB
- Streaming to Twitch/OBS
- Real-time low-latency optimization
- Automated tests

---

## Iteration 2 — Voice Input + Virtual Cable

> Microphone → STT → LLM → TTS → Virtual Audio Cable → VTube Studio / OBS

### Scope

- Accept voice input from microphone using `faster-whisper` (local STT)
- Route synthesized audio output to VB-Audio Virtual Cable
- Toggle between text and voice input mode
- Auto-detect silence / end of speech (voice activity detection)

### New Files

| File | Purpose |
|---|---|
| `pipeline/stt.py` | Speech-to-text via faster-whisper |
| `pipeline/vad.py` | Voice activity detection (silence threshold to detect end of speech) |

### Modified Files

| File | Changes |
|---|---|
| `config.py` | Add STT model config, mic device index, VAD silence threshold, virtual cable device name |
| `main.py` | Add voice input mode toggle (`/voice`, `/text` commands), integrate STT + VAD |
| `pipeline/audio_player.py` | Default output to virtual cable device name from config |
| `requirements.txt` | Add `faster-whisper`, `numpy` |

### Key Decisions

- **STT model:** `faster-whisper` with `large-v3` for best accuracy, or `medium` to save VRAM (~1-2GB vs ~3GB)
- **VAD:** Simple energy-based silence detection via `sounddevice` input stream, or use Silero VAD (lightweight, ~10MB)
- **Audio routing:** TTS output goes to VB-Audio Virtual Cable by default. VTube Studio picks it up as mic input.

### Architecture Addition

```
[Microphone Input]
       │
       ▼
[VAD (Silence Detection)]  ──  Wait for speech to end
       │
       ▼
[faster-whisper STT]  ──  Transcribe speech to text
       │
       ▼
[Existing pipeline: LLM → TTS → Virtual Cable]
```

### Estimated VRAM Impact

| Model | Estimated VRAM |
|---|---|
| faster-whisper medium | ~1.5 GB |
| faster-whisper large-v3 | ~3 GB |

### Dependencies to Add

```
faster-whisper
numpy
```

### Prerequisites

- VB-Audio Virtual Cable installed and configured
- Microphone configured as default input device

---

## Iteration 3 — Live2D Avatar + Lip Sync

> Audio output drives Live2D avatar mouth movement via virtual audio routing

### Scope

- Display a Live2D avatar on screen
- Drive lip sync from the TTS audio output
- Avatar reacts to audio amplitude / energy in real-time
- VTube Studio integration (receive audio from virtual cable)

### New Files

| File | Purpose |
|---|---|
| `pipeline/lipsync.py` | Audio energy analysis for lip sync parameter generation |
| `pipeline/avatar.py` | VTube Studio API client (start/stop lip sync, set parameters) |

### Modified Files

| File | Changes |
|---|---|
| `config.py` | Add VTube Studio API config, lip sync sensitivity, Live2D model path |
| `main.py` | Start avatar alongside TTS, send lip sync data during playback |
| `requirements.txt` | Add `pyvts`, `numpy` |

### Key Decisions

- **VTube Studio integration:** Use `pyvts` library (VTube Studio API plugin) to control avatar parameters
- **Lip sync approach:** Analyze audio amplitude in real-time chunks → map to mouth open parameter (`ParamMouthOpenY`)
- **Audio routing:** VB-Audio Virtual Cable carries TTS audio → VTube Studio listens to virtual cable as mic input → built-in lip sync
- **Alternative:** Send lip sync parameters directly via VTube Studio API for more control (expressions, eye movement)

### Architecture Addition

```
[TTS Audio Output]
       │
       ├──→ [Virtual Audio Cable] ──→ VTube Studio mic input (auto lip sync)
       │
       └──→ [pipeline/lipsync.py] ──→ Audio energy → mouth params → VTube Studio API
```

Two lip sync strategies (use one or both):
1. **Passive:** Route audio to virtual cable → VTube Studio's built-in audio reactive lip sync
2. **Active:** Analyze audio energy in Python → send precise mouth parameters via VTube Studio API

### Estimated VRAM Impact

Negligible — Live2D rendering is handled by VTube Studio (separate process, typically CPU/GPU-light).

### Dependencies to Add

```
pyvts
numpy
```

### Prerequisites

- VTube Studio installed and running
- Live2D model loaded in VTube Studio
- VTube Studio API enabled in settings
- VB-Audio Virtual Cable installed

---

## Iteration 4 — Long-Term Memory

> Character remembers past conversations across sessions using vector similarity search

### Scope

- Store conversation summaries in ChromaDB (local, persistent vector database)
- Embed messages using a local embedding model
- Retrieve relevant past conversations as additional context for LLM
- Summarize long conversations to keep token usage manageable
- Memory search happens before LLM call — injects relevant context into system prompt

### New Files

| File | Purpose |
|---|---|
| `pipeline/memory.py` | ChromaDB wrapper — store, search, summarize conversations |
| `scripts/init_db.py` | Initialize ChromaDB collection |

### Modified Files

| File | Changes |
|---|---|
| `config.py` | Add ChromaDB path, embedding model name, max memory results, auto-summarize threshold |
| `pipeline/llm.py` | Inject memory context into system prompt before LLM call |
| `main.py` | Save conversations to memory, load relevant context on startup |
| `requirements.txt` | Add `chromadb`, `sentence-transformers` |

### Key Decisions

- **Vector DB:** ChromaDB (local, file-based, no server needed, Python-native)
- **Embedding model:** `nomic-embed-text` via Ollama, or `all-MiniLM-L6-v2` via sentence-transformers (local, ~80MB, no extra VRAM needed if run on CPU)
- **Storage strategy:**
  - Each conversation exchange stored as: `{timestamp, user_input, character_response, summary}`
  - Auto-summarize when conversation exceeds N exchanges
  - Search returns top-K relevant past exchanges by cosine similarity
- **Context injection:** Retrieved memories appended to system prompt as "Relevant past conversations:"
- **Persistence:** ChromaDB stores data in `./data/chroma/` directory

### Architecture Addition

```
[User Input]
      │
      ▼
[pipeline/memory.py]  ──  Search for relevant past conversations
      │
      ▼
[pipeline/llm.py]  ──  System prompt + memory context + history + user input
      │
      ▼
[LLM Response]
      │
      ├──→ [Existing pipeline: TTS → Audio]
      │
      └──→ [pipeline/memory.py]  ──  Store exchange for future recall
```

### Estimated VRAM Impact

| Model | Estimated VRAM |
|---|---|
| all-MiniLM-L6-v2 (CPU) | ~0 GB (runs on CPU) |
| nomic-embed-text via Ollama (GPU) | ~0.5 GB |

Recommendation: Run embedding model on CPU to save VRAM. It's fast enough for this use case.

### Dependencies to Add

```
chromadb
sentence-transformers
```

### Prerequisites

- None additional — ChromaDB and embedding model are self-contained

---

## Iteration 5 — OBS Streaming + Real-Time Optimization

> Stream to Twitch/YouTube via OBS, minimize end-to-end latency

### Scope

- Integrate with OBS Studio via obs-websocket for scene management
- Optimize pipeline for real-time interaction:
  - Streaming TTS generation (start playing audio before full synthesis completes)
  - Sentence-level chunking (start TTS on first sentence while LLM is still generating)
  - Reduce first-audio latency below 2 seconds
- Auto-start/stop streaming
- Scene switching (idle vs. active vs. overlay)

### New Files

| File | Purpose |
|---|---|
| `pipeline/obs.py` | OBS WebSocket client — scene management, streaming control |
| `pipeline/streaming.py` | Streaming audio chunker — sentence splitting, partial TTS synthesis |

### Modified Files

| File | Changes |
|---|---|
| `config.py` | Add OBS WebSocket config (host, port, password), streaming settings, latency targets |
| `main.py` | Integrate streaming audio pipeline, OBS scene triggers |
| `pipeline/tts.py` | Add streaming synthesis mode (generate chunks as they arrive) |
| `pipeline/llm.py` | Add streaming response mode (yield sentences as they generate) |
| `requirements.txt` | Add `obs-websocket-py` |

### Key Decisions

- **OBS integration:** `obs-websocket-py` for remote control of OBS Studio
- **Streaming TTS:** F5-TTS supports chunk inference for streaming generation. Split text into sentences, synthesize each independently, play sequentially.
- **Sentence chunking:** Split LLM streaming response by sentence boundaries (`.` `!` `?` `。` `！` `？`). Start TTS on each sentence as it completes.
- **Pipeline parallelism:**
  ```
  LLM generates: "Sentence 1. | Sentence 2. | Sentence 3."
                        │                │               │
                        ▼                ▼               ▼
                   TTS sent 1       TTS sent 2      TTS sent 3
                        │                │               │
                        ▼                ▼               ▼
                   Play audio 1     Play audio 2    Play audio 3
  ```
- **Latency target:** < 2 seconds from user input end to first audio output

### Architecture Addition

```
[User Input / STT]
        │
        ▼
[LLM (streaming)]  ──  Yield sentences one at a time
        │
        ▼
[pipeline/streaming.py]
   ├── Sentence splitter
   ├── TTS queue (process sentences in order)
   └── Audio player queue (play chunks sequentially)
        │
        ▼
[pipeline/obs.py]  ──  Scene management, stream control
```

### Estimated VRAM Impact

No additional VRAM — uses existing models. Streaming is a software optimization, not a new model.

### Dependencies to Add

```
obs-websocket-py
```

### Prerequisites

- OBS Studio installed and configured
- obs-websocket plugin enabled (built into OBS 28+)
- Streaming accounts configured in OBS (Twitch, YouTube, etc.)
- VB-Audio Virtual Cable for audio routing to OBS

---

## Full Roadmap Summary

| Iteration | Key Feature | New Dependencies | New VRAM | Cumulative VRAM |
|---|---|---|---|---|
| **1** | Text → LLM → TTS → Audio | qwen-tts, openai, sounddevice, demucs, flash-attn | ~4-5 GB | ~4-5 GB |
| **2** | Voice input (STT), virtual cable | faster-whisper, numpy | ~1.5-3 GB | ~6-8 GB |
| **3** | Live2D avatar, lip sync | pyvts, numpy | ~0 GB | ~6-8 GB |
| **4** | Long-term memory (ChromaDB) | chromadb, sentence-transforme