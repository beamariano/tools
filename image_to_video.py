#!/usr/bin/env python3
"""Convert images to videos with configurable duration, format, and dimensions."""

import argparse
from pathlib import Path
from moviepy import ImageClip
from moviepy.video.fx.FadeIn import FadeIn
from moviepy.video.fx.FadeOut import FadeOut

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}

def image_to_video(image_path, output_path, duration=4, size=None, fps=24, codec='libx264',
                   fade_in=0, fade_out=0):
    """Convert image to video with optional resizing and fades."""
    clip = ImageClip(str(image_path), duration=duration)
    if size:
        clip = clip.resized(size)
    if fade_in > 0 or fade_out > 0:
        effects = []
        if fade_in > 0:
            effects.append(FadeIn(fade_in))
        if fade_out > 0:
            effects.append(FadeOut(fade_out))
        clip = clip.with_effects(effects)
    clip.write_videofile(str(output_path), fps=fps, codec=codec, audio=False)
    print(f"✓ {output_path.name}")

def main():
    parser = argparse.ArgumentParser(description='Convert images to videos')
    parser.add_argument('input', help='Input image file or folder')
    parser.add_argument('-o', '--output', help='Output folder (default: ./videos)')
    parser.add_argument('-d', '--duration', type=float, default=4, help='Duration in seconds (default: 4)')
    parser.add_argument('-f', '--format', default='mp4', help='Output format (default: mp4)')
    parser.add_argument('-s', '--size', help='Output size as WIDTHxHEIGHT (e.g., 1920x1080)')
    parser.add_argument('--fps', type=int, default=24, help='Frames per second (default: 24)')
    parser.add_argument('--codec', default='libx264', help='Video codec (default: libx264)')
    parser.add_argument('--fade-in', type=float, default=0, help='Fade in duration in seconds (default: 0)')
    parser.add_argument('--fade-out', type=float, default=0, help='Fade out duration in seconds (default: 0)')

    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output or 'videos')
    output_dir.mkdir(parents=True, exist_ok=True)

    size = tuple(map(int, args.size.split('x'))) if args.size else None

    # Get image files
    images = [input_path] if input_path.is_file() else [
        f for f in sorted(input_path.iterdir())
        if f.suffix.lower() in IMAGE_EXTENSIONS
    ]

    if not images:
        print(f"No images found. Supported: {', '.join(sorted(IMAGE_EXTENSIONS))}")
        return

    print(f"Converting {len(images)} image(s) to video...")
    for img in images:
        output = output_dir / f"{img.stem}.{args.format}"
        try:
            image_to_video(img, output, args.duration, size, args.fps, args.codec,
                         args.fade_in, args.fade_out)
        except Exception as e:
            print(f"✗ {img.name}: {e}")

if __name__ == "__main__":
    main()
