import os

import soundfile as sf
from chatterbox.tts_turbo import ChatterboxTurboTTS

import config

_model = None


def load_model() -> None:
    global _model

    print("[TTS] Loading Chatterbox-Turbo model...")
    _model = ChatterboxTurboTTS.from_pretrained(device="cuda")
    print("[TTS] Chatterbox-Turbo model ready.")


def synthesize(text: str, output_path: str) -> str:
    if _model is None:
        raise RuntimeError("TTS model not loaded. Call load_model() first.")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    ref_audio = config.REF_AUDIO_PATH if os.path.exists(config.REF_AUDIO_PATH) else None

    if ref_audio:
        wav = _model.generate(
            text,
            audio_prompt_path=ref_audio,
            temperature=config.TTS_TEMPERATURE,
            top_p=config.TTS_TOP_P,
            top_k=config.TTS_TOP_K,
            repetition_penalty=config.TTS_REPETITION_PENALTY,
            min_p=config.TTS_MIN_P,
            norm_loudness=config.TTS_NORM_LOUDNESS,
        )
    else:
        wav = _model.generate(
            text,
            temperature=config.TTS_TEMPERATURE,
            top_p=config.TTS_TOP_P,
            top_k=config.TTS_TOP_K,
            repetition_penalty=config.TTS_REPETITION_PENALTY,
            min_p=config.TTS_MIN_P,
            norm_loudness=config.TTS_NORM_LOUDNESS,
        )

    sf.write(output_path, wav.squeeze().cpu().numpy(), _model.sr)
    return output_path
