import time
import soundfile as sf
import torchaudio as ta
from chatterbox.tts_turbo import ChatterboxTurboTTS

print("Loading Chatterbox-Turbo...")
model = ChatterboxTurboTTS.from_pretrained(device="cuda")
print("Model loaded.\n")

ref_audio = "G:/Coding/Learn/vtuber-tts/voice_samples/reference_audio.wav"

tests = [
    ("Short", "Hello there, nice to meet you!"),
    ("Medium", "I think the best part of my day is when someone visits the library and asks for a book recommendation. Not many people do that anymore."),
    ("Expressive", "Oh! You startled me! [chuckle] I was just... daydreaming again, sorry about that."),
]

for label, text in tests:
    out = f"G:/Coding/Learn/vtuber-tts/output/response_audio/chatterbox_test_{label.lower()}.wav"
    t0 = time.time()
    wav = model.generate(text, audio_prompt_path=ref_audio)
    t1 = time.time()
    ta.save(out, wav, model.sr)

    data, sr = sf.read(out)
    dur = len(data) / sr
    ratio = (t1 - t0) / dur
    print(f"{label} ({len(text)} chars): {t1-t0:.2f}s for {dur:.1f}s audio (ratio: {ratio:.2f}x)")
