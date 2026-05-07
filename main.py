import os
import time

import pipeline.llm as llm
import pipeline.tts as tts
import pipeline.audio_player as audio_player
import config


def main() -> None:
    print(f"=== {config.CHARACTER_NAME} VTuber TTS ===\n")

    try:
        tts.load_model()
    except RuntimeError as e:
        if "CUDA" in str(e) or "out of memory" in str(e):
            print(f"[TTS] CUDA OOM: {e}")
            print("[TTS] Try closing other GPU processes and restarting.")
            return
        raise
    print("Model loaded.\n")

    history: list[dict] = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{config.CHARACTER_NAME}: Bye~!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print(f"{config.CHARACTER_NAME}: Bye~!")
            break

        response = llm.get_response(user_input, history)
        if not response:
            continue

        print(f"{config.CHARACTER_NAME}: {response}\n")

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})

        output_path = os.path.join(config.OUTPUT_DIR, "latest.wav")

        try:
            tts.synthesize(response, output_path)
            print("Playing audio...")
            audio_player.play_audio(output_path, device=config.AUDIO_OUTPUT_DEVICE)
        except Exception as e:
            print(f"[Pipeline] Error during synthesis/playback: {e}")
            continue


if __name__ == "__main__":
    main()
