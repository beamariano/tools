#!/usr/bin/env python3
"""
Image optimization tool for web.
Compresses and resizes images while maintaining quality.
"""

import sys
from pathlib import Path
from PIL import Image
import argparse
from constants import (
    IMAGE_EXTENSIONS,
    DEFAULT_MAX_WEB_WIDTH,
    DEFAULT_MAX_WEB_HEIGHT,
    DEFAULT_WEB_QUALITY,
    DEFAULT_PNG_COMPRESSION_LEVEL,
    DEFAULT_WEBP_METHOD,
    RGB_MODE,
    MODES_REQUIRING_RGB_CONVERSION,
)
from messages import (
    msg,
    processing_started,
    size_info,
    dimensions_info,
    batch_started,
    batch_completed,
    Operation,
    handle_exception,
)


def optimize_image(
    input_path,
    output_path=None,
    max_width=DEFAULT_MAX_WEB_WIDTH,
    max_height=DEFAULT_MAX_WEB_HEIGHT,
    quality=DEFAULT_WEB_QUALITY,
    format=None,
):
    """
    Optimize an image for web use.

    Args:
        input_path: Path to input image
        output_path: Path to output image (optional, defaults to input_path with _optimized suffix)
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        quality: JPEG/WebP quality (1-100)
        format: Output format (jpg, png, webp). If None, uses input format

    Returns:
        Path to optimized image
    """
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Image not found: {input_path}")

    # Open and process image
    img = Image.open(input_path)

    # Convert RGBA to RGB if saving as JPEG
    output_format = format.upper() if format else img.format
    if output_format == "JPEG" and img.mode in MODES_REQUIRING_RGB_CONVERSION:
        background = Image.new(RGB_MODE, img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(
            img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None
        )
        img = background

    # Resize if needed
    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        dimensions_info(img.width, img.height, "Resized")

    # Determine output path
    if output_path is None:
        ext = f".{format.lower()}" if format else input_path.suffix
        output_path = input_path.parent / f"{input_path.stem}_optimized{ext}"
    else:
        output_path = Path(output_path)

    # Save optimized image
    save_kwargs: dict = {"optimize": True}

    if output_format in ("JPEG", "JPG"):
        save_kwargs["quality"] = quality
        save_kwargs["progressive"] = True
    elif output_format == "PNG":
        save_kwargs["compress_level"] = DEFAULT_PNG_COMPRESSION_LEVEL
    elif output_format == "WEBP":
        save_kwargs["quality"] = quality
        save_kwargs["method"] = DEFAULT_WEBP_METHOD

    img.save(output_path, **save_kwargs)

    # Print size comparison
    original_size = input_path.stat().st_size
    optimized_size = output_path.stat().st_size

    size_info(original_size / 1024, optimized_size / 1024)

    return output_path


def optimize_directory(input_dir, output_dir=None, **kwargs):
    """
    Optimize all images in a directory.

    Args:
        input_dir: Directory containing images
        output_dir: Output directory (optional)
        **kwargs: Additional arguments passed to optimize_image
    """
    input_dir = Path(input_dir)

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    image_files = [
        f
        for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]

    if not image_files:
        msg.error(f"No images found in {input_dir}")
        return

    batch_started(len(image_files), "images")

    success_count = 0
    fail_count = 0

    for img_file in image_files:
        processing_started("Processing", img_file)
        try:
            out_path = output_dir / img_file.name if output_dir else None
            optimize_image(img_file, out_path, **kwargs)
            success_count += 1
            print()
        except Exception as e:
            msg.error(f"Error processing {img_file.name}: {e}")
            fail_count += 1
            print()

    # Summary
    if fail_count == 0:
        batch_completed(success_count, "images")
    else:
        msg.warning(f"Completed with {success_count} success, {fail_count} failed")


def main():
    parser = argparse.ArgumentParser(
        description="Optimize images for web use",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Optimize single image:
    python optimize_images.py input.jpg

  Optimize with custom settings:
    python optimize_images.py input.jpg -o output.jpg --quality 90 --max-width 1280

  Convert to WebP:
    python optimize_images.py input.jpg --format webp

  Optimize entire directory:
    python optimize_images.py --dir images/ --output-dir optimized/
        """,
    )

    parser.add_argument("input", nargs="?", help="Input image file")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--dir", help="Process all images in directory")
    parser.add_argument("--output-dir", help="Output directory (for --dir mode)")
    parser.add_argument(
        "--max-width",
        type=int,
        default=DEFAULT_MAX_WEB_WIDTH,
        help=f"Maximum width (default: {DEFAULT_MAX_WEB_WIDTH})",
    )
    parser.add_argument(
        "--max-height",
        type=int,
        default=DEFAULT_MAX_WEB_HEIGHT,
        help=f"Maximum height (default: {DEFAULT_MAX_WEB_HEIGHT})",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=DEFAULT_WEB_QUALITY,
        help=f"Quality for JPEG/WebP (1-100, default: {DEFAULT_WEB_QUALITY})",
    )
    parser.add_argument(
        "--format",
        choices=["jpg", "png", "webp"],
        help="Output format (jpg, png, webp)",
    )

    args = parser.parse_args()

    try:
        if args.dir:
            with Operation("Batch optimization"):
                optimize_directory(
                    args.dir,
                    args.output_dir,
                    max_width=args.max_width,
                    max_height=args.max_height,
                    quality=args.quality,
                    format=args.format,
                )
        elif args.input:
            with Operation("Image optimization"):
                result = optimize_image(
                    args.input,
                    args.output,
                    max_width=args.max_width,
                    max_height=args.max_height,
                    quality=args.quality,
                    format=args.format,
                )
                msg.info(f"Optimized image saved to: {result}")
        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        exit_code = handle_exception(e)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
