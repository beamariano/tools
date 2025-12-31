#!/usr/bin/env python3
"""
Convert text lines from a .txt file into centered images.
Each line in the file is converted to a separate image with configurable
font, size, aspect ratio, and dimensions.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Tuple, Optional, Union
import os

from constants import (
    ASPECT_RATIO_16_9,
    ASPECT_RATIO_4_3,
    ASPECT_RATIO_1_1,
    ASPECT_RATIO_9_16,
    ASPECT_RATIO_21_9,
    ImageFormat,
    IMAGE_FORMAT_EXTENSIONS,
)
from messages import (
    msg,
    processing_started,
    file_created,
    batch_started,
    batch_completed,
    folder_not_exist_error,
    folder_created_info,
    folder_setup_instructions,
    invalid_input_default_warning,
    invalid_choice_default_warning,
)


# Defaults
DEFAULT_INPUT_DIR = "text_to_process"
DEFAULT_OUTPUT_DIR = "images_processed"
DEFAULT_FONT_SIZE = 48
DEFAULT_TEXT_COLOR = (255, 255, 255)  # White
DEFAULT_BG_COLOR = (0, 0, 0)  # Black
DEFAULT_FORMAT = ImageFormat.PNG.value
DEFAULT_PADDING = 20  # Padding around text


def get_default_font(size: int) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
    """
    Get a default system font.

    Args:
        size: Font size

    Returns:
        ImageFont object
    """
    # Try to get a decent system font
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "/System/Library/Fonts/SFNSDisplay.ttf",  # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue

    # Fallback to default font
    return ImageFont.load_default()


def create_text_image(
    text: str,
    width: int,
    height: int,
    font: Union[ImageFont.FreeTypeFont, ImageFont.ImageFont],
    text_color: Tuple[int, int, int] = DEFAULT_TEXT_COLOR,
    bg_color: Tuple[int, int, int] = DEFAULT_BG_COLOR,
    padding: int = DEFAULT_PADDING,
) -> Image.Image:
    """
    Create an image with centered text.

    Args:
        text: Text to render
        width: Image width
        height: Image height
        font: Font to use
        text_color: RGB text color
        bg_color: RGB background color
        padding: Padding around text (pixels)

    Returns:
        PIL Image object
    """
    # Create image with background color
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Get text bounding box for proper centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Check if text fits within the image (with padding)
    max_text_width = width - (2 * padding)
    max_text_height = height - (2 * padding)

    # Calculate position for centered text
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Adjust if text doesn't fit (warn user)
    if text_width > max_text_width or text_height > max_text_height:
        msg.warning(f"Text '{text[:30]}...' may not fit properly in {width}x{height} image")

    # Draw text
    draw.text((x, y), text, font=font, fill=text_color)

    return image


def process_text_file(
    input_file: str,
    output_folder: str,
    width: int,
    height: int,
    font: Optional[Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]] = None,
    font_size: int = DEFAULT_FONT_SIZE,
    text_color: Tuple[int, int, int] = DEFAULT_TEXT_COLOR,
    bg_color: Tuple[int, int, int] = DEFAULT_BG_COLOR,
    output_format: str = DEFAULT_FORMAT,
    padding: int = DEFAULT_PADDING,
) -> int:
    """
    Process a text file and create images for each line.

    Args:
        input_file: Path to input text file
        output_folder: Path to output folder
        width: Image width
        height: Image height
        font: Font to use (None for default)
        font_size: Font size (used if font is None)
        text_color: RGB text color
        bg_color: RGB background color
        output_format: Image format (PNG, JPEG, etc.)
        padding: Padding around text (pixels)

    Returns:
        Number of images created
    """
    input_path = Path(input_file)

    # Check if file exists
    if not input_path.exists():
        msg.error(folder_not_exist_error(input_file))
        return 0

    # Ensure output folder exists
    output_path = Path(output_folder)
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
        msg.info(folder_created_info(output_folder))

    # Get font
    if font is None:
        font = get_default_font(font_size)

    # Read lines from file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        msg.error(f"Failed to read file {input_file}: {e}")
        return 0

    if not lines:
        msg.warning(f"No text found in {input_file}")
        return 0

    batch_started(len(lines), "lines")

    # Process each line
    created_count = 0
    extension = IMAGE_FORMAT_EXTENSIONS.get(output_format.upper(), '.png')

    for idx, line in enumerate(lines, 1):
        if not line:
            continue

        processing_started(f"Creating image {idx}/{len(lines)}", None)

        # Create image
        img = create_text_image(
            line, width, height, font, text_color, bg_color, padding
        )

        # Generate output filename
        # Use line number and sanitized text for filename
        safe_text = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in line)

        # Warn if text will be cropped in filename
        max_filename_length = 50
        if len(safe_text) > max_filename_length:
            msg.warning(f"Line {idx} text too long for filename ('{line[:30]}...'), will be cropped to {max_filename_length} characters")

        safe_text = safe_text[:max_filename_length]  # Limit filename length
        output_file = output_path / f"line_{idx:03d}_{safe_text}{extension}"

        # Save image
        try:
            if output_format.upper() == 'JPEG' or output_format.upper() == 'JPG':
                # Convert to RGB for JPEG (no transparency)
                img = img.convert('RGB')
                img.save(output_file, output_format, quality=95)
            else:
                img.save(output_file, output_format)

            file_size = output_file.stat().st_size / 1024  # KB
            file_created(output_file, file_size)
            created_count += 1

        except Exception as e:
            msg.error(f"Failed to save image for line {idx}: {e}")

    batch_completed(created_count, "images")
    msg.info(f"Output saved to '{output_folder}' folder")

    return created_count


def get_aspect_ratio_input() -> Tuple[int, int]:
    """Get aspect ratio from user input."""
    print("\nCommon aspect ratios:")
    print("1. 16:9 (1920x1080) - Widescreen")
    print("2. 4:3 (1024x768) - Standard")
    print("3. 1:1 (1080x1080) - Square")
    print("4. 9:16 (1080x1920) - Vertical/Portrait")
    print("5. 21:9 (2560x1080) - Ultra-wide")
    print("6. Custom")

    choice = input("\nSelect aspect ratio (1-6, default: 3 - Square): ").strip()

    if choice == "1":
        return ASPECT_RATIO_16_9
    elif choice == "2":
        return ASPECT_RATIO_4_3
    elif choice == "3" or choice == "":
        return ASPECT_RATIO_1_1
    elif choice == "4":
        return ASPECT_RATIO_9_16
    elif choice == "5":
        return ASPECT_RATIO_21_9
    elif choice == "6":
        try:
            width = int(input("Enter image width (px): ").strip())
            height = int(input("Enter image height (px): ").strip())
            return width, height
        except ValueError:
            msg.warning(invalid_input_default_warning("1080x1080 (Square)"))
            return ASPECT_RATIO_1_1
    else:
        msg.warning(invalid_choice_default_warning("1:1 (1080x1080 - Square)"))
        return ASPECT_RATIO_1_1


def get_font_size_input() -> int:
    """Get font size from user input."""
    try:
        size_input = input(f"\nEnter font size (default: {DEFAULT_FONT_SIZE}): ").strip()
        if not size_input:
            return DEFAULT_FONT_SIZE
        size = int(size_input)
        if size <= 0:
            msg.warning(invalid_input_default_warning(str(DEFAULT_FONT_SIZE)))
            return DEFAULT_FONT_SIZE
        return size
    except ValueError:
        msg.warning(invalid_input_default_warning(str(DEFAULT_FONT_SIZE)))
        return DEFAULT_FONT_SIZE


def get_font_path_input() -> Optional[str]:
    """Get custom font path from user input."""
    use_custom = input("\nUse custom font? (y/N): ").strip().lower()

    if use_custom == 'y':
        font_path = input("Enter path to .ttf or .otf font file: ").strip()
        if font_path and os.path.exists(font_path):
            return font_path
        else:
            msg.warning("Font file not found. Using system default.")
            return None

    return None


def get_colors_input() -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """Get text and background colors from user input."""
    print("\nColor scheme:")
    print("1. White text on black background (default)")
    print("2. Black text on white background")
    print("3. Custom RGB colors")

    choice = input("\nSelect color scheme (1-3): ").strip()

    if choice == "2":
        return (0, 0, 0), (255, 255, 255)  # Black on white
    elif choice == "3":
        try:
            print("\nText color (RGB):")
            tr = int(input("  Red (0-255): ").strip())
            tg = int(input("  Green (0-255): ").strip())
            tb = int(input("  Blue (0-255): ").strip())

            print("\nBackground color (RGB):")
            br = int(input("  Red (0-255): ").strip())
            bg = int(input("  Green (0-255): ").strip())
            bb = int(input("  Blue (0-255): ").strip())

            # Clamp values
            text_color = (max(0, min(255, tr)), max(0, min(255, tg)), max(0, min(255, tb)))
            bg_color = (max(0, min(255, br)), max(0, min(255, bg)), max(0, min(255, bb)))

            return text_color, bg_color
        except ValueError:
            msg.warning(invalid_input_default_warning("white on black"))
            return DEFAULT_TEXT_COLOR, DEFAULT_BG_COLOR
    else:
        return DEFAULT_TEXT_COLOR, DEFAULT_BG_COLOR


def get_format_input() -> str:
    """Get output format from user input."""
    print("\nOutput format:")
    print("1. PNG (default - lossless)")
    print("2. JPEG (smaller file size)")
    print("3. WEBP")

    choice = input("\nSelect format (1-3): ").strip()

    if choice == "2":
        return ImageFormat.JPEG.value
    elif choice == "3":
        return ImageFormat.WEBP.value
    else:
        return ImageFormat.PNG.value


def main():
    """Main function."""
    print("=" * 60)
    print("Text to Image Converter")
    print("=" * 60)

    # Get input file
    default_input_file = f"{DEFAULT_INPUT_DIR}/text.txt"
    input_file = input(f"\nEnter path to text file (default: '{default_input_file}'): ").strip()
    if not input_file:
        input_file = default_input_file
        # Create default input folder if it doesn't exist
        Path(DEFAULT_INPUT_DIR).mkdir(exist_ok=True)
        msg.info(folder_setup_instructions(DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR))

    # Get output folder
    output_folder = input(f"Enter output folder (default: '{DEFAULT_OUTPUT_DIR}'): ").strip()
    if not output_folder:
        output_folder = DEFAULT_OUTPUT_DIR

    # Get aspect ratio and dimensions
    width, height = get_aspect_ratio_input()

    # Get font settings
    font_size = get_font_size_input()
    font_path = get_font_path_input()

    # Get font
    font = None
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
            msg.success(f"Loaded custom font: {font_path}")
        except Exception as e:
            msg.error(f"Failed to load font: {e}")
            msg.info("Using system default font")
            font = get_default_font(font_size)
    else:
        font = get_default_font(font_size)

    # Get colors
    text_color, bg_color = get_colors_input()

    # Get output format
    output_format = get_format_input()

    # Display settings
    print("\n" + "=" * 60)
    print("Settings:")
    print(f"  Input file: {input_file}")
    print(f"  Output folder: {output_folder}")
    print(f"  Image dimensions: {width}x{height}")
    print(f"  Font size: {font_size}")
    print(f"  Text color (RGB): {text_color}")
    print(f"  Background color (RGB): {bg_color}")
    print(f"  Output format: {output_format}")
    print("=" * 60)

    # Process file
    created_count = process_text_file(
        input_file,
        output_folder,
        width,
        height,
        font,
        font_size,
        text_color,
        bg_color,
        output_format,
    )

    if created_count > 0:
        print(f"\n{created_count} images created successfully!")
    else:
        print("\nNo images were created.")


if __name__ == "__main__":
    main()
