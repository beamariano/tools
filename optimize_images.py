#!/usr/bin/env python3
"""
Image optimization tool for web.
Compresses and resizes images while maintaining quality.
"""

import os
import sys
from pathlib import Path
from PIL import Image
import argparse


def optimize_image(input_path, output_path=None, max_width=1920, max_height=1080,
                   quality=85, format=None):
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
    if output_format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = background

    # Resize if needed
    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        print(f"Resized to {img.width}x{img.height}")

    # Determine output path
    if output_path is None:
        ext = f".{format.lower()}" if format else input_path.suffix
        output_path = input_path.parent / f"{input_path.stem}_optimized{ext}"
    else:
        output_path = Path(output_path)

    # Save optimized image
    save_kwargs = {'optimize': True}

    if output_format in ('JPEG', 'JPG'):
        save_kwargs['quality'] = quality
        save_kwargs['progressive'] = True
    elif output_format == 'PNG':
        save_kwargs['compress_level'] = 9
    elif output_format == 'WEBP':
        save_kwargs['quality'] = quality
        save_kwargs['method'] = 6

    img.save(output_path, **save_kwargs)

    # Print size comparison
    original_size = input_path.stat().st_size
    optimized_size = output_path.stat().st_size
    reduction = ((original_size - optimized_size) / original_size) * 100

    print(f"Original: {original_size / 1024:.2f} KB")
    print(f"Optimized: {optimized_size / 1024:.2f} KB")
    print(f"Reduction: {reduction:.1f}%")

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

    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
    image_files = [f for f in input_dir.iterdir()
                   if f.is_file() and f.suffix.lower() in image_extensions]

    if not image_files:
        print(f"No images found in {input_dir}")
        return

    print(f"Found {len(image_files)} images to optimize\n")

    for img_file in image_files:
        print(f"Processing {img_file.name}...")
        try:
            out_path = output_dir / img_file.name if output_dir else None
            optimize_image(img_file, out_path, **kwargs)
            print()
        except Exception as e:
            print(f"Error processing {img_file.name}: {e}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Optimize images for web use',
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
        """
    )

    parser.add_argument('input', nargs='?', help='Input image file')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--dir', help='Process all images in directory')
    parser.add_argument('--output-dir', help='Output directory (for --dir mode)')
    parser.add_argument('--max-width', type=int, default=1920,
                       help='Maximum width (default: 1920)')
    parser.add_argument('--max-height', type=int, default=1080,
                       help='Maximum height (default: 1080)')
    parser.add_argument('--quality', type=int, default=85,
                       help='Quality for JPEG/WebP (1-100, default: 85)')
    parser.add_argument('--format', choices=['jpg', 'png', 'webp'],
                       help='Output format (jpg, png, webp)')

    args = parser.parse_args()

    try:
        if args.dir:
            optimize_directory(
                args.dir,
                args.output_dir,
                max_width=args.max_width,
                max_height=args.max_height,
                quality=args.quality,
                format=args.format
            )
        elif args.input:
            result = optimize_image(
                args.input,
                args.output,
                max_width=args.max_width,
                max_height=args.max_height,
                quality=args.quality,
                format=args.format
            )
            print(f"\nOptimized image saved to: {result}")
        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
