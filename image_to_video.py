#!/usr/bin/env python3
"""Convert images to videos with configurable duration, format, and dimensions."""

import argparse
from pathlib import Path
from moviepy import ImageClip
from moviepy.video.fx.FadeIn import FadeIn
from moviepy.video.fx.FadeOut import FadeOut
from constants import (
    IMAGE_EXTENSIONS,
    DEFAULT_VIDEO_DURATION,
    DEFAULT_VIDEO_FPS,
    DEFAULT_VIDEO_CODEC,
    DEFAULT_VIDEO_FORMAT,
    DEFAULT_VIDEO_OUTPUT_DIR,
    DEFAULT_IMAGES_INPUT_DIR,
)
from messages import (
    msg,
    batch_started,
    batch_completed,
    processing_started,
    folder_created_info,
    folder_setup_instructions,
    Emoji,
    use_emoji,
)


def image_to_video(
    image_path,
    output_path,
    duration=DEFAULT_VIDEO_DURATION,
    size=None,
    fps=DEFAULT_VIDEO_FPS,
    codec=DEFAULT_VIDEO_CODEC,
    fade_in=0,
    fade_out=0,
):
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
    clip.write_videofile(str(output_path), fps=fps, codec=codec, audio=False)  # type: ignore[attr-defined]

    # Display success with emoji if supported
    check = Emoji.CHECK if use_emoji() else "✓"
    print(f"{check} {output_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert images to videos",
        epilog=f"Default: Input from '{DEFAULT_IMAGES_INPUT_DIR}/', output to '{DEFAULT_VIDEO_OUTPUT_DIR}/'",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=DEFAULT_IMAGES_INPUT_DIR,
        help=f"Input image file or folder (default: {DEFAULT_IMAGES_INPUT_DIR})",
    )
    parser.add_argument(
        "-o", "--output", help=f"Output folder (default: {DEFAULT_VIDEO_OUTPUT_DIR})"
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=float,
        default=DEFAULT_VIDEO_DURATION,
        help=f"Duration in seconds (default: {DEFAULT_VIDEO_DURATION})",
    )
    parser.add_argument(
        "-f",
        "--format",
        default=DEFAULT_VIDEO_FORMAT,
        help=f"Output format (default: {DEFAULT_VIDEO_FORMAT})",
    )
    parser.add_argument(
        "-s", "--size", help="Output size as WIDTHxHEIGHT (e.g., 1920x1080)"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=DEFAULT_VIDEO_FPS,
        help=f"Frames per second (default: {DEFAULT_VIDEO_FPS})",
    )
    parser.add_argument(
        "--codec",
        default=DEFAULT_VIDEO_CODEC,
        help=f"Video codec (default: {DEFAULT_VIDEO_CODEC})",
    )
    parser.add_argument(
        "--fade-in",
        type=float,
        default=0,
        help="Fade in duration in seconds (default: 0)",
    )
    parser.add_argument(
        "--fade-out",
        type=float,
        default=0,
        help="Fade out duration in seconds (default: 0)",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output or DEFAULT_VIDEO_OUTPUT_DIR)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    if not output_dir.exists() or len(list(output_dir.iterdir())) == 0:
        msg.info(folder_created_info(str(output_dir)))

    # Check if input exists
    if not input_path.exists():
        msg.error(f"Input path '{input_path}' does not exist")
        msg.info(folder_setup_instructions(str(input_path), str(output_dir)))
        return

    size = tuple(map(int, args.size.split("x"))) if args.size else None

    # Get image files
    images = (
        [input_path]
        if input_path.is_file()
        else [
            f
            for f in sorted(input_path.iterdir())
            if f.suffix.lower() in IMAGE_EXTENSIONS
        ]
    )

    if not images:
        msg.error(f"No images found in '{input_path}'. Supported: {', '.join(sorted(IMAGE_EXTENSIONS))}")
        msg.info(folder_setup_instructions(str(input_path), str(output_dir)))
        return

    batch_started(len(images), "image(s)")

    success_count = 0
    fail_count = 0

    for idx, img in enumerate(images, 1):
        output = output_dir / f"{img.stem}.{args.format}"
        try:
            processing_started(f"Converting [{idx}/{len(images)}]", img)
            image_to_video(
                img,
                output,
                args.duration,
                size,
                args.fps,
                args.codec,
                args.fade_in,
                args.fade_out,
            )
            success_count += 1
        except Exception as e:
            cross = Emoji.CROSS if use_emoji() else "✗"
            print(f"{cross} {img.name}: {e}")
            fail_count += 1

    # Summary
    if fail_count == 0:
        batch_completed(success_count, "video(s)")
    else:
        msg.warning(f"Completed with {success_count} success, {fail_count} failed")


if __name__ == "__main__":
    main()
