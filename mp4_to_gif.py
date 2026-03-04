import subprocess
import os

INPUT = "____.mp4"
OUTPUT = "____.gif"
WIDTH = 160
HEIGHT = 90
NEW_FPS = 5

subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-i",
        INPUT,
        "-vf",
        f"fps={NEW_FPS},scale={WIDTH}:{HEIGHT}:flags=lanczos",
        OUTPUT,
    ],
    check=True,
)

size_kb = os.path.getsize(OUTPUT) / 1024
print(f"\nDone: {OUTPUT} — {size_kb:.1f} KB")
