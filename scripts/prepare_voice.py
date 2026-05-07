import argparse
import os
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean raw audio with Demucs to isolate vocals."
    )
    parser.add_argument("input", help="Path to raw audio file (WAV)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"File not found: {args.input}")
        sys.exit(1)

    if not args.input.lower().endswith(".wav"):
        print("Input must be a WAV file.")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cleaned_dir = os.path.join(script_dir, "voice_samples", "cleaned")
    os.makedirs(cleaned_dir, exist_ok=True)

    print(f"Running Demucs on: {args.input}")
    print("This may take a few minutes...\n")

    try:
        subprocess.run(
            ["demucs", "--two-stems=vocals", args.input],
            check=True,
        )
    except FileNotFoundError:
        print("Demucs not found. Install with: pip install demucs")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Demucs failed with exit code {e.returncode}")
        sys.exit(1)

    basename = os.path.splitext(os.path.basename(args.input))[0]
    vocals_path = os.path.join("htdemucs", basename, "vocals.wav")

    if os.path.exists(vocals_path):
        dest = os.path.join(cleaned_dir, f"{basename}_vocals.wav")
        import shutil

        shutil.copy2(vocals_path, dest)
        print(f"\nVocals saved to: {dest}")
        print(f"\nNext steps:")
        print(f"  1. Copy best result to voice_samples/reference.wav")
        print(f"  2. Write exact transcript to voice_samples/reference_text.txt")
    else:
        print(f"\nCould not find output at {vocals_path}")
        print("Check the htdemucs/ directory for results.")


if __name__ == "__main__":
    main()
