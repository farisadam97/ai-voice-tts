import soundfile as sf
import sounddevice as sd


def play_audio(filepath: str, device: str | None = None) -> None:
    data, samplerate = sf.read(filepath)
    sd.play(data, samplerate, device=device)
    sd.wait()


def list_devices() -> None:
    print("\nAvailable audio devices:\n")
    print(sd.query_devices())
    print()
