# Implementation Checklist

---

## Iteration 1 — Voice Clone Pipeline

### Setup & Infrastructure
- [x] Create conda environment (`python=3.12`)
- [x] Install PyTorch with CUDA 12.8 (`pip install --pre torch torchaudio --index-url https://download.pytorch.org/whl/cu128`)
- [x] Use SDPA attention (built into PyTorch, replaces FlashAttention 2)
- [x] Create directory structure (`pipeline/`, `models/`, `voice_samples/`, `output/`, `scripts/`)
- [x] Create `requirements.txt`
- [x] Install all dependencies (`pip install -r requirements.txt`)
- [x] Install and setup LM Studio
- [x] Download Qwen3-4B-Instruct-2507 model in LM Studio
- [x] Start LM Studio local server
- [x] Pre-download Qwen3-TTS model locally:
  ```bash
  conda activate ai-vtuber
  huggingface-cli download Qwen/Qwen3-TTS-Tokenizer-12Hz --local-dir ./models/tokenizer
  huggingface-cli download Qwen/Qwen3-TTS-12Hz-0.6B-Base --local-dir ./models/tts
  ```
- [ ] Install VB-Audio Virtual Cable (optional)

### Voice Sample Preparation
- [x] Collect raw game audio clips → `voice_samples/raw/`
- [x] Run Demucs to clean audio → `voice_samples/cleaned/`
- [x] Select best clip → `voice_samples/reference_audio.wav`
- [x] Write exact transcript → `voice_samples/reference_text.txt`

### Code Implementation
- [x] Create `config.py` — LM Studio, character, TTS, output config
- [x] Create `pipeline/__init__.py` — empty package init
- [x] Create `pipeline/llm.py` — LM Studio API wrapper + error handling
- [x] Create `pipeline/tts.py` — Qwen3-TTS wrapper + error handling + startup validation
- [x] Create `pipeline/audio_player.py` — playback + device listing
- [x] Create `main.py` — REPL loop + graceful shutdown
- [x] Create `scripts/prepare_voice.py` — Demucs CLI utility

### Verification
- [x] `python -c "import pipeline.llm, pipeline.tts, pipeline.audio_player"` — no import errors
- [x] `python -c "import config"` — config loads
- [x] Test LM Studio connection — send a test message, get response
- [x] Test TTS model load — model loads without errors
- [x] Test TTS synthesis — generate audio from a test string
- [x] Test audio playback — hear the generated audio
- [x] Test full pipeline — type text → get response → hear audio
- [x] Test Web UI — browser chat → LLM → TTS → audio playback
- [x] Benchmark F5-TTS vs Qwen3-TTS speed
- [ ] Test error handling — LM Studio off, missing files, etc.
- [ ] Test `scripts/prepare_voice.py` — clean a raw audio clip

---

## Iteration 2 — Voice Input + Virtual Cable

### Setup & Infrastructure
- [ ] Install `faster-whisper` and `numpy`
- [ ] Install and configure VB-Audio Virtual Cable
- [ ] Configure microphone as default input device
- [ ] Test virtual cable routing (play audio → verify VTube Studio / OBS receives it)

### Code Implementation
- [ ] Update `config.py` — add STT model, mic device index, VAD threshold, virtual cable device name
- [ ] Create `pipeline/stt.py` — faster-whisper wrapper
  - [ ] `transcribe(audio_data, sample_rate)` → text
  - [ ] Model loading (choose medium or large-v3)
  - [ ] Error handling (mic not found, STT failure)
- [ ] Create `pipeline/vad.py` — voice activity detection
  - [ ] `listen_for_speech(device, silence_threshold, silence_duration)` → audio data
  - [ ] Record until silence detected
  - [ ] Error handling (no mic, permission denied)
- [ ] Update `main.py` — voice input mode
  - [ ] `/voice` command to switch to voice input
  - [ ] `/text` command to switch back to text input
  - [ ] Show current mode in prompt
  - [ ] Integrate VAD → STT → existing pipeline
- [ ] Update `pipeline/audio_player.py` — default to virtual cable device

### Verification
- [ ] Test mic recording — record audio and play it back
- [ ] Test VAD — speak, stop, verify it detects end of speech
- [ ] Test STT — speak a sentence, verify transcription
- [ ] Test virtual cable routing — audio plays through virtual cable
- [ ] Test full voice pipeline — speak → transcribe → LLM → TTS → hear response
- [ ] Test mode switching — `/voice` and `/text` commands work
- [ ] Verify VRAM usage is within budget

---

## Iteration 3 — Live2D Avatar + Lip Sync

### Setup & Infrastructure
- [ ] Install VTube Studio
- [ ] Obtain/create Live2D model for the character
- [ ] Load Live2D model in VTube Studio
- [ ] Enable VTube Studio API in settings
- [ ] Install `pyvts` and `numpy`

### Code Implementation
- [ ] Update `config.py` — add VTube Studio API port, plugin name, lip sync sensitivity, Live2D model path
- [ ] Create `pipeline/avatar.py` — VTube Studio API client
  - [ ] `connect()` — authenticate with VTube Studio
  - [ ] `set_parameter(name, value)` — set avatar parameter
  - [ ] `trigger_expression(name)` — trigger expression/hotkey
  - [ ] Error handling (VTube Studio not running, API not enabled)
- [ ] Create `pipeline/lipsync.py` — audio energy analysis
  - [ ] `analyze_chunk(audio_data, sample_rate)` → mouth open value (0.0–1.0)
  - [ ] Map amplitude to `ParamMouthOpenY` range
  - [ ] Smooth transitions (avoid jitter)
- [ ] Update `main.py` — avatar integration
  - [ ] Connect to VTube Studio on startup
  - [ ] Send lip sync params during audio playback
  - [ ] Set idle expression when not speaking
  - [ ] Graceful disconnect on exit
- [ ] Update `pipeline/audio_player.py` — return audio data for lip sync analysis

### Verification
- [ ] Test VTube Studio API connection — `pipeline/avatar.py connect()` succeeds
- [ ] Test parameter control — manually set mouth open, verify avatar moves
- [ ] Test lip sync — play audio, verify mouth movement matches
- [ ] Test expression triggers — trigger happy/surprised/angry expressions
- [ ] Test idle state — avatar returns to neutral when not speaking
- [ ] Test full pipeline — speak → LLM → TTS → avatar lip sync + audio

---

## Iteration 4 — Long-Term Memory

### Setup & Infrastructure
- [ ] Install `chromadb` and `sentence-transformers`
- [ ] Choose embedding model (`all-MiniLM-L6-v2` for CPU, or `nomic-embed-text` via Ollama)
- [ ] Test embedding model — embed a sentence, verify output shape
- [ ] Initialize ChromaDB collection

### Code Implementation
- [ ] Update `config.py` — add ChromaDB path, embedding model name, max memory results, auto-summarize threshold
- [ ] Create `scripts/init_db.py` — initialize ChromaDB collection
- [ ] Create `pipeline/memory.py` — ChromaDB wrapper
  - [ ] `init()` — load ChromaDB client and collection
  - [ ] `store(user_input, character_response, metadata)` — embed and store exchange
  - [ ] `search(query, top_k)` → list of relevant past exchanges
  - [ ] `summarize_old(exchanges)` — compress old exchanges into summaries
  - [ ] Error handling (DB locked, embedding failure)
- [ ] Update `pipeline/llm.py` — inject memory context
  - [ ] Before LLM call, search memory for relevant context
  - [ ] Append retrieved memories to system prompt
  - [ ] Keep total context within token limits
- [ ] Update `main.py` — memory integration
  - [ ] Initialize memory on startup
  - [ ] Store each exchange after response
  - [ ] Auto-summarize when history exceeds threshold
  - [ ] Print memory status on startup

### Verification
- [ ] Test ChromaDB init — collection created, no errors
- [ ] Test store — embed and store a test exchange
- [ ] Test search — query for stored exchange, verify relevance
- [ ] Test summarization — store many exchanges, verify auto-summarize works
- [ ] Test LLM memory injection — ask about something from a previous session
- [ ] Test persistence — close and reopen, verify memories persist
- [ ] Verify embedding model runs on CPU (no VRAM impact)
- [ ] Verify memory search doesn't add noticeable latency

---

## Iteration 5 — OBS Streaming + Real-Time Optimization

### Setup & Infrastructure
- [ ] Install OBS Studio
- [ ] Enable obs-websocket in OBS settings (port, password)
- [ ] Configure streaming accounts (Twitch, YouTube, etc.)
- [ ] Set up OBS scenes (idle, active, overlay)
- [ ] Route virtual cable audio to OBS audio source
- [ ] Install `obs-websocket-py`
- [ ] Test OBS WebSocket connection — connect and list scenes

### Code Implementation
- [ ] Update `config.py` — add OBS WebSocket host/port/password, scene names, latency target
- [ ] Create `pipeline/obs.py` — OBS WebSocket client
  - [ ] `connect()` — authenticate with OBS
  - [ ] `switch_scene(name)` — switch between scenes
  - [ ] `start_streaming()` / `stop_streaming()` — control stream
  - [ ] Error handling (OBS not running, WebSocket auth failure)
- [ ] Create `pipeline/streaming.py` — streaming audio chunker
  - [ ] `split_sentences(text)` — split text into sentences (support JP/EN punctuation)
  - [ ] `process_sentence_queue(sentences)` — queue TTS per sentence
  - [ ] `play_audio_queue()` — play audio chunks sequentially with no gaps
  - [ ] Smooth transition between chunks
- [ ] Update `pipeline/llm.py` — streaming response mode
  - [ ] `get_response_stream(user_input, history)` → yield sentences as generated
  - [ ] Parse sentence boundaries from stream
- [ ] Update `pipeline/tts.py` — streaming synthesis mode
  - [ ] `synthesize_stream(text)` → yield audio chunks as generated
  - [ ] Use F5-TTS chunk inference for sentence-level streaming
- [ ] Update `main.py` — integrate streaming pipeline + OBS
  - [ ] Connect to OBS on startup
  - [ ] Switch to active scene when conversation starts
  - [ ] Switch to idle scene after inactivity timeout
  - [ ] Use streaming pipeline instead of full synthesis
  - [ ] Measure and display latency

### Verification
- [ ] Test OBS WebSocket connection — connect, list scenes
- [ ] Test scene switching — switch between idle/active scenes
- [ ] Test streaming control — start/stop stream
- [ ] Test sentence splitting — verify JP and EN sentences split correctly
- [ ] Test streaming TTS — verify audio chunks arrive with low latency
- [ ] Test streaming LLM — verify sentences yield incrementally
- [ ] Test full streaming pipeline — input → streaming LLM → streaming TTS → play chunks
- [ ] Measure latency — verify first audio output < 2 seconds
- [ ] Test OBS integration — full pipeline with OBS scene management
- [ ] Test stability — run for 30+ minutes without issues
- [ ] Verify VRAM usage stays within budget during streaming
