#!/usr/bin/env python3
"""
Convert an image to a C array file for ESP32 Arduino projects.
Accepts any image format (JPEG, PNG, BMP, GIF, TIFF, WebP, etc.) as input.
Resizes the image to 240x320 and outputs as JPEG format in a C array.
"""

import sys
from PIL import Image
import io
import os


def image_to_header(
    input_path,
    output_path="photoData.h",
    target_width=240,
    target_height=320,
    quality=75,
    flip_horizontal=False,
    flip_vertical=False,
    optimize=True,
):
    """
    Convert an image to a C header file with JPEG data.

    Supports any image format readable by PIL (JPEG, PNG, BMP, GIF, TIFF, WebP, etc.).
    The output is always encoded as JPEG regardless of input format.

    Args:
        input_path: Path to input image file (any PIL-supported format)
        output_path: Path to output .h file (default: photoData.h)
        target_width: Target width in pixels (default: 240)
        target_height: Target height in pixels (default: 320)
        quality: JPEG quality 1-95 (default: 75)
        flip_horizontal: Flip image horizontally (default: False)
        flip_vertical: Flip image vertically (default: False)
        optimize: Optimize JPEG encoding (default: True)
    """

    # Open and convert image
    print(f"Loading image: {input_path}")
    img = Image.open(input_path)

    # Convert to RGB if necessary
    if img.mode != "RGB":
        print(f"Converting from {img.mode} to RGB mode")
        img = img.convert("RGB")

    # Resize image to target dimensions
    original_size = img.size
    print(f"Original size: {original_size[0]}x{original_size[1]}")
    print(f"Resizing to: {target_width}x{target_height}")
    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Apply flips if requested
    if flip_horizontal:
        print("Flipping horizontally")
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    if flip_vertical:
        print("Flipping vertically")
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

    # Convert to JPEG in memory
    jpeg_buffer = io.BytesIO()
    print(f"Encoding JPEG (quality={quality}, optimize={optimize})")
    img.save(
        jpeg_buffer, format="JPEG", quality=quality, optimize=optimize, subsampling=2
    )
    jpeg_data = jpeg_buffer.getvalue()
    jpeg_size = len(jpeg_data)

    print(f"JPEG size: {jpeg_size} bytes ({jpeg_size / 1024:.2f} KB)")

    # Generate C header file
    print(f"Writing header file: {output_path}")

    with open(output_path, "w") as f:
        # Write header comments
        f.write(f"// Generated from: {os.path.basename(input_path)}\n")
        f.write(f"// Size: {target_width}x{target_height} pixels\n")
        f.write(f"// JPEG size: {jpeg_size} bytes\n")
        f.write(f"\n")

        # Write array declaration
        f.write(f"const unsigned char photoData[] PROGMEM = {{\n")

        # Write bytes in groups of 12 per line
        bytes_per_line = 12
        for i in range(0, jpeg_size, bytes_per_line):
            chunk = jpeg_data[i : i + bytes_per_line]
            hex_values = ", ".join(f"0x{b:02X}" for b in chunk)

            if i + bytes_per_line < jpeg_size:
                f.write(f"  {hex_values},\n")
            else:
                f.write(f"  {hex_values}\n")

        f.write("};\n")

    print(f"Done! Generated {output_path}")
    print(f'Include this file in your Arduino sketch with: #include "{output_path}"')


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 image_to_header.py <input_image> [options]")
        print("\nExamples:")
        print("  python3 image_to_header.py photo.jpg")
        print("  python3 image_to_header.py photo.png photoData.h")
        print("  python3 image_to_header.py photo.jpg photoData.h 240 320 80")
        print(
            "  python3 image_to_header.py photo.jpg photoData.h 240 320 75 --flip-h --flip-v"
        )
        print(
            "  python3 image_to_header.py photo.jpg photoData.h 240 320 75 --no-optimize"
        )
        print("\nPositional Arguments:")
        print(
            "  input_image   - Path to input image (JPEG, PNG, BMP, GIF, TIFF, WebP, etc.)"
        )
        print("  output_header - Output .h file (default: photoData.h)")
        print("  width         - Target width in pixels (default: 240)")
        print("  height        - Target height in pixels (default: 320)")
        print("  quality       - JPEG quality 1-95 (default: 75)")
        print("\nOptional Flags:")
        print("  --flip-h      - Flip image horizontally (mirror)")
        print("  --flip-v      - Flip image vertically (upside down)")
        print("  --no-optimize - Disable JPEG optimization (smaller but slower)")
        sys.exit(1)

    input_path = sys.argv[1]

    # Parse optional flags
    flip_h = "--flip-h" in sys.argv
    flip_v = "--flip-v" in sys.argv
    no_optimize = "--no-optimize" in sys.argv

    # Remove flags from argv for positional parsing
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    output_path = args[1] if len(args) > 1 else "photoData.h"
    width = int(args[2]) if len(args) > 2 else 240
    height = int(args[3]) if len(args) > 3 else 320
    quality = int(args[4]) if len(args) > 4 else 75

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found!")
        sys.exit(1)

    image_to_header(
        input_path,
        output_path,
        width,
        height,
        quality,
        flip_horizontal=flip_h,
        flip_vertical=flip_v,
        optimize=not no_optimize,
    )


if __name__ == "__main__":
    main()
