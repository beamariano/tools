#!/usr/bin/env python3
"""
Format utility functions and examples for working with image and video formats.
Demonstrates usage of the structured format system from constants.py.
"""

from pathlib import Path
from constants import (
    # Format enums
    ImageFormat,
    VideoFormat,
    VideoCodec,
    # File extensions
    IMAGE_FORMAT_EXTENSIONS,
    EXTENSION_TO_FORMAT,
    # Format categories
    LOSSY_FORMATS,
    LOSSLESS_FORMATS,
    TRANSPARENCY_FORMATS,
    ANIMATION_FORMATS,
    # Quality settings
    QUALITY_WEB,
    QUALITY_RECOMMENDATIONS,
    DEFAULT_QUALITY_FALLBACK,
    LOSSLESS_QUALITY,
    # Format name constants
    FORMAT_JPEG,
    FORMAT_PNG,
    FORMAT_WEBP,
    # Helpers
    is_image_file,
    is_video_file,
    is_lossy_format,
)
from messages import (
    transparency_loss_warning,
    quality_loss_warning,
    jpeg_transparency_warning,
    unsupported_extension_error,
    unsupported_format_error,
)


def get_format_from_filename(filename: str) -> str:
    """
    Get the format name from a filename.

    Args:
        filename: File path or name

    Returns:
        Format name (e.g., 'JPEG', 'PNG')

    Raises:
        ValueError: If format is not supported
    """
    ext = Path(filename).suffix.lower()
    if ext in EXTENSION_TO_FORMAT:
        return EXTENSION_TO_FORMAT[ext]
    raise ValueError(unsupported_extension_error(ext))


def get_extension_for_format(format_name: str) -> str:
    """
    Get the file extension for a format name.

    Args:
        format_name: Format name (e.g., 'JPEG', 'PNG')

    Returns:
        File extension (e.g., '.jpg', '.png')

    Raises:
        ValueError: If format is not supported
    """
    format_upper = format_name.upper()
    if format_upper in IMAGE_FORMAT_EXTENSIONS:
        return IMAGE_FORMAT_EXTENSIONS[format_upper]
    raise ValueError(unsupported_format_error(format_name))


def get_recommended_quality(format_name: str, use_case: str = QUALITY_WEB) -> int:
    """
    Get recommended quality setting for a format.

    Args:
        format_name: Format name (e.g., 'JPEG', 'PNG', 'WEBP')
        use_case: Use case ('web', 'archive', 'thumbnail')

    Returns:
        Recommended quality value (1-100)
    """
    format_upper = format_name.upper()

    if not is_lossy_format(format_upper):
        return LOSSLESS_QUALITY

    return QUALITY_RECOMMENDATIONS.get(use_case, QUALITY_RECOMMENDATIONS[QUALITY_WEB]).get(
        format_upper, DEFAULT_QUALITY_FALLBACK
    )


def should_convert_format(
    source_format: str, target_format: str, has_transparency: bool = False
) -> dict:
    """
    Determine if and how to convert between formats.

    Args:
        source_format: Source format name
        target_format: Target format name
        has_transparency: Whether source image has transparency

    Returns:
        Dictionary with conversion information
    """
    source = source_format.upper()
    target = target_format.upper()

    result = {
        "should_convert": source != target,
        "will_lose_transparency": False,
        "will_lose_quality": False,
        "recommended": True,
        "warnings": [],
    }

    if source == target:
        return result

    # Check transparency loss
    if has_transparency:
        if source in TRANSPARENCY_FORMATS and target not in TRANSPARENCY_FORMATS:
            result["will_lose_transparency"] = True
            result["warnings"].append(transparency_loss_warning(source, target))

    # Check quality loss
    if source in LOSSLESS_FORMATS and target in LOSSY_FORMATS:
        result["will_lose_quality"] = True
        result["warnings"].append(quality_loss_warning(source, target))

    # Check if conversion is recommended
    if target == FORMAT_JPEG and has_transparency:
        result["recommended"] = False
        result["warnings"].append(jpeg_transparency_warning())

    return result


def get_optimal_output_format(
    input_format: str, has_transparency: bool = False, prefer_modern: bool = True
) -> str:
    """
    Get optimal output format for web optimization.

    Args:
        input_format: Input format name
        has_transparency: Whether image has transparency
        prefer_modern: Prefer modern formats (WEBP) over legacy (JPEG/PNG)

    Returns:
        Recommended output format name
    """
    if has_transparency:
        return FORMAT_WEBP if prefer_modern else FORMAT_PNG

    if input_format.upper() in ANIMATION_FORMATS:
        return FORMAT_WEBP if prefer_modern else input_format.upper()

    # For photos/regular images
    return FORMAT_WEBP if prefer_modern else FORMAT_JPEG


def format_info(format_name: str) -> dict:
    """
    Get comprehensive information about a format.

    Args:
        format_name: Format name

    Returns:
        Dictionary with format information
    """
    format_upper = format_name.upper()

    return {
        "name": format_upper,
        "extension": IMAGE_FORMAT_EXTENSIONS.get(format_upper, "unknown"),
        "is_lossy": format_upper in LOSSY_FORMATS,
        "is_lossless": format_upper in LOSSLESS_FORMATS,
        "supports_transparency": format_upper in TRANSPARENCY_FORMATS,
        "supports_animation": format_upper in ANIMATION_FORMATS,
        "recommended_quality": {
            "thumbnail": get_recommended_quality(format_upper, "thumbnail"),
            "web": get_recommended_quality(format_upper, "web"),
            "archive": get_recommended_quality(format_upper, "archive"),
        },
    }


def main():
    """Demonstrate format utilities."""
    print("=" * 60)
    print("Format Utilities - Usage Examples")
    print("=" * 60)

    # Example 1: Check file types
    print("\n1. File Type Detection:")
    test_files = ["photo.jpg", "animation.gif", "video.mp4", "graphic.png"]
    for filename in test_files:
        is_img = is_image_file(filename)
        is_vid = is_video_file(filename)
        file_type = "Image" if is_img else ("Video" if is_vid else "Unknown")
        print(f"   {filename:20} -> {file_type}")

    # Example 2: Format information
    print("\n2. Format Information:")
    for fmt in [ImageFormat.JPEG, ImageFormat.PNG, ImageFormat.WEBP]:
        info = format_info(fmt.value)
        print(f"\n   {info['name']}:")
        print(f"      Extension: {info['extension']}")
        print(f"      Lossy: {info['is_lossy']}")
        print(f"      Transparency: {info['supports_transparency']}")
        print(f"      Recommended quality (web): {info['recommended_quality']['web']}")

    # Example 3: Format conversions
    print("\n3. Format Conversion Analysis:")
    conversions = [
        (ImageFormat.PNG.value, ImageFormat.JPEG.value, True),
        (ImageFormat.PNG.value, ImageFormat.WEBP.value, True),
        (ImageFormat.JPEG.value, ImageFormat.PNG.value, False),
    ]

    for source, target, has_alpha in conversions:
        result = should_convert_format(source, target, has_alpha)
        print(f"\n   {source} -> {target} (transparency: {has_alpha}):")
        print(f"      Should convert: {result['should_convert']}")
        print(f"      Will lose transparency: {result['will_lose_transparency']}")
        print(f"      Will lose quality: {result['will_lose_quality']}")
        if result["warnings"]:
            for warning in result["warnings"]:
                print(f"      ⚠ {warning}")

    # Example 4: Optimal format selection
    print("\n4. Optimal Format Selection:")
    scenarios = [
        (ImageFormat.PNG.value, True, True, "Transparent logo"),
        (ImageFormat.JPEG.value, False, True, "Photo for web"),
        (ImageFormat.GIF.value, False, True, "Animation"),
    ]

    for input_fmt, has_trans, prefer_mod, desc in scenarios:
        optimal = get_optimal_output_format(input_fmt, has_trans, prefer_mod)
        print(f"   {desc:25} ({input_fmt}) -> {optimal}")

    # Example 5: Available formats
    print("\n5. All Supported Formats:")
    print(f"   Image formats: {', '.join(f.value for f in ImageFormat)}")
    print(f"   Video formats: {', '.join(f.value for f in VideoFormat)}")
    print(f"   Video codecs:  {', '.join(c.value for c in VideoCodec)}")

    # Example 6: Format categories
    print("\n6. Format Categories:")
    print(f"   Lossy:        {', '.join(sorted(LOSSY_FORMATS))}")
    print(f"   Lossless:     {', '.join(sorted(LOSSLESS_FORMATS))}")
    print(f"   Transparency: {', '.join(sorted(TRANSPARENCY_FORMATS))}")
    print(f"   Animation:    {', '.join(sorted(ANIMATION_FORMATS))}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
