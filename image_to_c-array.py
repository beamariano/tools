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
from constants import (
    DEFAULT_IMAGE_WIDTH,
    DEFAULT_IMAGE_HEIGHT,
    DEFAULT_JPEG_QUALITY,
    DEFAULT_HEADER_OUTPUT,
    DEFAULT_BYTES_PER_LINE,
    RGB_MODE,
    JPEG_SUBSAMPLING_420,
)
from messages import (
    msg,
    file_not_found,
    file_created,
    processing_started,
    dimensions_info,
    Operation,
    handle_exception,
)


def image_to_header(
    input_path,
    output_path=DEFAULT_HEADER_OUTPUT,
    target_width=DEFAULT_IMAGE_WIDTH,
    target_height=DEFAULT_IMAGE_HEIGHT,
    quality=DEFAULT_JPEG_QUALITY,
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
    processing_started("Loading image", input_path)
    img = Image.open(input_path)

    # Convert to RGB if necessary
    if img.mode != RGB_MODE:
        msg.info(f"Converting from {img.mode} to {RGB_MODE} mode")
        img = img.convert(RGB_MODE)

    # Resize image to target dimensions
    original_size = img.size
    msg.info(f"Original size: {original_size[0]}x{original_size[1]}")
    dimensions_info(target_width, target_height, "Resizing to")
    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Apply flips if requested
    if flip_horizontal:
        msg.info("Flipping horizontally")
        img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    if flip_vertical:
        msg.info("Flipping vertically")
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

    # Convert to JPEG in memory
    jpeg_buffer = io.BytesIO()
    msg.info(f"Encoding JPEG (quality={quality}, optimize={optimize})")
    img.save(
        jpeg_buffer,
        format="JPEG",
        quality=quality,
        optimize=optimize,
        subsampling=JPEG_SUBSAMPLING_420,
    )
    jpeg_data = jpeg_buffer.getvalue()
    jpeg_size = len(jpeg_data)

    msg.info(f"JPEG size: {jpeg_size} bytes ({jpeg_size / 1024:.2f} KB)")

    # Generate C header file
    msg.info(f"Writing header file: {output_path}")

    with open(output_path, "w") as f:
        # Write header comments
        f.write(f"// Generated from: {os.path.basename(input_path)}\n")
        f.write(f"// Size: {target_width}x{target_height} pixels\n")
        f.write(f"// JPEG size: {jpeg_size} bytes\n")
        f.write("\n")

        # Write array declaration
        f.write("const unsigned char photoData[] PROGMEM = {{\n")

        # Write bytes in groups per line
        for i in range(0, jpeg_size, DEFAULT_BYTES_PER_LINE):
            chunk = jpeg_data[i : i + DEFAULT_BYTES_PER_LINE]
            hex_values = ", ".join(f"0x{b:02X}" for b in chunk)

            if i + DEFAULT_BYTES_PER_LINE < jpeg_size:
                f.write(f"  {hex_values},\n")
            else:
                f.write(f"  {hex_values}\n")

        f.write("};\n")

    file_created(output_path, jpeg_size / 1024)
    msg.info(f'Include this file in your Arduino sketch with: #include "{output_path}"')


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

    output_path = args[1] if len(args) > 1 else DEFAULT_HEADER_OUTPUT
    width = int(args[2]) if len(args) > 2 else DEFAULT_IMAGE_WIDTH
    height = int(args[3]) if len(args) > 3 else DEFAULT_IMAGE_HEIGHT
    quality = int(args[4]) if len(args) > 4 else DEFAULT_JPEG_QUALITY

    if not os.path.exists(input_path):
        file_not_found(input_path)

    try:
        with Operation("Image to C array conversion"):
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
    except Exception as e:
        exit_code = handle_exception(e)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
