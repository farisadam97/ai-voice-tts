import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pipeline.tts as tts
import pipeline.audio_player as audio_player
import config


def main() -> None:
    print("=== TTS Hardcoded Test ===\n")

    try:
        tts.load_model()
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    test_texts = [
        "Hi, umm... nice to meet you. I'm Noa... and what a great day, right? ri-right?",
        "Oh! You startled me! I was just... daydreaming again, sorry about that. So, um, what were you saying?",
        "You know, I think the best part of my day is... well, it's when someone visits the library and actually asks for a recommendation. Not many people do that anymore...",
    ]

    output_dir = os.path.join(config.OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    for i, text in enumerate(test_texts):
        output_path = os.path.join(output_dir, f"test_{i}.wav")
        print(f'\n[{i + 1}/{len(test_texts)}] Synthesizing: "{text}"')

        try:
            tts.synthesize(text, output_path)
            print(f"Saved: {output_path}")
            print("Playing...")
            audio_player.play_audio(output_path, device=config.AUDIO_OUTPUT_DEVICE)
        except Exception as e:
            print(f"Error: {e}")
            continue

    print("\n=== Test complete ===")


if __name__ == "__main__":
    main()
