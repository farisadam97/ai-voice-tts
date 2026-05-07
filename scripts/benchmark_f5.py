import time
import soundfile as sf
from f5_tts.api import F5TTS

print("Loading F5-TTS...")
model = F5TTS(model="F5TTS_v1_Base", device="cuda")
print("Model loaded.\n")

ref_audio = "G:/Coding/Learn/vtuber-tts/voice_samples/reference_audio.wav"
ref_text = open("G:/Coding/Learn/vtuber-tts/voice_samples/reference_text.txt", encoding="utf-8").read().strip()

tests = [
    ("Short", "Hello there, nice to meet you!"),
    ("Medium", "I think the best part of my day is when someone visits the library and asks for a book recommendation. Not many people do that anymore."),
]

for label, text in tests:
    out = f"G:/Coding/Learn/vtuber-tts/output/response_audio/f5test_{label.lower()}.wav"
    t0 = time.time()
    model.infer(ref_file=ref_audio, ref_text=ref_text, gen_text=text, file_wave=out)
    t1 = time.time()

    data, sr = sf.read(out)
    dur = len(data) / sr
    ratio = (t1 - t0) / dur
    print(f"{label} ({len(text)} chars): {t1-t0:.2f}s for {dur:.1f}s audio (ratio: {ratio:.2f}x)")
