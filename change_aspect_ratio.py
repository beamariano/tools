#!/usr/bin/env python3
"""
Change aspect ratio of images and videos with letterboxing or cropping options.
Supports multiple crop anchor positions for precise control and configurable letterbox colors.
"""

import cv2
import os
import numpy as np
from pathlib import Path
from typing import Tuple, List
from enum import Enum

from constants import (
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    DEFAULT_IMAGES_INPUT_DIR,
    DEFAULT_IMAGES_OUTPUT_DIR,
    DEFAULT_VIDEOS_INPUT_DIR,
    DEFAULT_VIDEOS_OUTPUT_DIR,
    ASPECT_RATIO_16_9,
    ASPECT_RATIO_4_3,
    ASPECT_RATIO_1_1,
    ASPECT_RATIO_9_16,
    ASPECT_RATIO_21_9,
    LETTERBOX_COLOR_BLACK,
    LETTERBOX_COLOR_WHITE,
    LETTERBOX_COLOR_GRAY,
    VIDEO_PROGRESS_FRAME_INTERVAL,
    VIDEO_CODEC_MP4V,
    COLOR_MIN_VALUE,
    COLOR_MAX_VALUE,
)
from messages import (
    msg,
    processing_started,
    file_processed,
    batch_started,
    batch_completed,
    folder_not_exist_error,
    folder_created_info,
    folder_setup_instructions,
    image_read_error,
    video_open_failed_error,
    image_processing_error,
    video_processing_failed_error,
    video_frame_progress_info,
    video_processed_success,
    no_media_files_warning,
    output_saved_to_folder_info,
    invalid_input_default_warning,
    invalid_choice_default_warning,
)


class AspectRatioMode(Enum):
    """Aspect ratio adjustment modes."""

    LETTERBOX = "letterbox"  # Add bars
    CROP = "crop"  # Crop to fit


class CropAnchor(Enum):
    """Crop anchor positions."""

    CENTER = "center"
    UPPER_LEFT = "upper_left"
    UPPER_CENTER = "upper_center"
    UPPER_RIGHT = "upper_right"
    CENTER_LEFT = "center_left"
    CENTER_RIGHT = "center_right"
    LOWER_LEFT = "lower_left"
    LOWER_CENTER = "lower_center"
    LOWER_RIGHT = "lower_right"


def calculate_crop_position(
    original_width: int,
    original_height: int,
    target_width: int,
    target_height: int,
    anchor: CropAnchor,
) -> Tuple[int, int]:
    """
    Calculate crop position based on anchor point.

    Args:
        original_width: Original image/video width
        original_height: Original image/video height
        target_width: Target crop width
        target_height: Target crop height
        anchor: Crop anchor position

    Returns:
        Tuple of (x, y) coordinates for top-left corner of crop
    """
    if anchor == CropAnchor.CENTER:
        x = (original_width - target_width) // 2
        y = (original_height - target_height) // 2
    elif anchor == CropAnchor.UPPER_LEFT:
        x, y = 0, 0
    elif anchor == CropAnchor.UPPER_CENTER:
        x = (original_width - target_width) // 2
        y = 0
    elif anchor == CropAnchor.UPPER_RIGHT:
        x = original_width - target_width
        y = 0
    elif anchor == CropAnchor.CENTER_LEFT:
        x = 0
        y = (original_height - target_height) // 2
    elif anchor == CropAnchor.CENTER_RIGHT:
        x = original_width - target_width
        y = (original_height - target_height) // 2
    elif anchor == CropAnchor.LOWER_LEFT:
        x = 0
        y = original_height - target_height
    elif anchor == CropAnchor.LOWER_CENTER:
        x = (original_width - target_width) // 2
        y = original_height - target_height
    elif anchor == CropAnchor.LOWER_RIGHT:
        x = original_width - target_width
        y = original_height - target_height
    else:
        # Default to center
        x = (original_width - target_width) // 2
        y = (original_height - target_height) // 2

    return max(0, x), max(0, y)


def resize_with_aspect_ratio(
    image: np.ndarray,
    target_width: int,
    target_height: int,
    mode: AspectRatioMode = AspectRatioMode.LETTERBOX,
    anchor: CropAnchor = CropAnchor.CENTER,
    letterbox_color: Tuple[int, int, int] = LETTERBOX_COLOR_BLACK,
) -> np.ndarray:
    """
    Resize image to target dimensions with aspect ratio handling.

    Args:
        image: Input image (numpy array)
        target_width: Target width
        target_height: Target height
        mode: AspectRatioMode (LETTERBOX or CROP)
        anchor: CropAnchor position (for CROP mode)
        letterbox_color: BGR color for letterbox bars (default: black)

    Returns:
        Resized image
    """
    original_height, original_width = image.shape[:2]
    target_aspect = target_width / target_height
    original_aspect = original_width / original_height

    if mode == AspectRatioMode.LETTERBOX:
        # Add bars to fit aspect ratio
        if original_aspect > target_aspect:
            # Image is wider - fit to width, add bars top/bottom
            new_width = target_width
            new_height = int(target_width / original_aspect)
        else:
            # Image is taller - fit to height, add bars left/right
            new_height = target_height
            new_width = int(target_height * original_aspect)

        # Resize image
        resized = cv2.resize(
            image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4
        )

        # Create canvas with specified color (BGR format for OpenCV)
        canvas = np.full(
            (target_height, target_width, image.shape[2]),
            letterbox_color,
            dtype=image.dtype,
        )

        # Center the resized image on canvas
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        canvas[y_offset : y_offset + new_height, x_offset : x_offset + new_width] = (
            resized
        )

        return canvas

    else:  # CROP mode
        # Crop to fit aspect ratio
        if original_aspect > target_aspect:
            # Image is wider - crop width
            crop_height = original_height
            crop_width = int(original_height * target_aspect)
        else:
            # Image is taller - crop height
            crop_width = original_width
            crop_height = int(original_width / target_aspect)

        # Calculate crop position based on anchor
        x, y = calculate_crop_position(
            original_width, original_height, crop_width, crop_height, anchor
        )

        # Crop image
        cropped = image[y : y + crop_height, x : x + crop_width]

        # Resize to target dimensions
        resized = cv2.resize(
            cropped, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4
        )

        return resized


def process_image(
    input_path: str,
    output_path: str,
    target_width: int,
    target_height: int,
    mode: AspectRatioMode = AspectRatioMode.LETTERBOX,
    anchor: CropAnchor = CropAnchor.CENTER,
    letterbox_color: Tuple[int, int, int] = LETTERBOX_COLOR_BLACK,
) -> bool:
    """
    Process a single image to change aspect ratio.

    Args:
        input_path: Path to input image
        output_path: Path to output image
        target_width: Target width
        target_height: Target height
        mode: AspectRatioMode (LETTERBOX or CROP)
        anchor: CropAnchor position (for CROP mode)
        letterbox_color: BGR color for letterbox bars (default: black)

    Returns:
        True if successful, False otherwise
    """
    try:
        processing_started("Processing image", input_path)

        # Read image
        image = cv2.imread(input_path)
        if image is None:
            msg.error(image_read_error(input_path))
            return False

        # Process image
        result = resize_with_aspect_ratio(
            image, target_width, target_height, mode, anchor, letterbox_color
        )

        # Save result
        cv2.imwrite(output_path, result)

        # Get file sizes for reporting
        original_size = Path(input_path).stat().st_size / 1024  # KB
        new_size = Path(output_path).stat().st_size / 1024  # KB

        file_processed(output_path, original_size, new_size)
        return True

    except Exception as e:
        msg.error(image_processing_error(input_path, e))
        return False


def process_video(
    input_path: str,
    output_path: str,
    target_width: int,
    target_height: int,
    mode: AspectRatioMode = AspectRatioMode.LETTERBOX,
    anchor: CropAnchor = CropAnchor.CENTER,
    letterbox_color: Tuple[int, int, int] = LETTERBOX_COLOR_BLACK,
) -> bool:
    """
    Process a single video to change aspect ratio.

    Args:
        input_path: Path to input video
        output_path: Path to output video
        target_width: Target width
        target_height: Target height
        mode: AspectRatioMode (LETTERBOX or CROP)
        anchor: CropAnchor position (for CROP mode)
        letterbox_color: BGR color for letterbox bars (default: black)

    Returns:
        True if successful, False otherwise
    """
    try:
        processing_started("Processing video", input_path)

        # Open video
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            msg.error(video_open_failed_error(input_path))
            return False

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*VIDEO_CODEC_MP4V)  # type: ignore[attr-defined]
        out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))

        # Process each frame
        frame_num = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame
            processed_frame = resize_with_aspect_ratio(
                frame, target_width, target_height, mode, anchor, letterbox_color
            )  # pyright: ignore[reportArgumentType]
            out.write(processed_frame)

            frame_num += 1
            if frame_num % VIDEO_PROGRESS_FRAME_INTERVAL == 0:
                progress = (frame_num / frame_count) * 100
                msg.info(video_frame_progress_info(frame_num, frame_count, progress))

        # Release resources
        cap.release()
        out.release()

        msg.success(video_processed_success(Path(output_path).name))
        return True

    except Exception as e:
        msg.error(video_processing_failed_error(input_path, e))
        return False


def get_media_files(folder: str, media_type: str = "both") -> List[Path]:
    """
    Get all media files from a folder.

    Args:
        folder: Folder path
        media_type: "images", "videos", or "both"

    Returns:
        List of media file paths
    """
    folder_path = Path(folder)
    if not folder_path.exists():
        msg.error(folder_not_exist_error(folder))
        msg.info(folder_setup_instructions(folder))
        return []

    files = []

    if media_type in ["images", "both"]:
        for ext in IMAGE_EXTENSIONS:
            files.extend(folder_path.glob(f"*{ext}"))

    if media_type in ["videos", "both"]:
        for ext in VIDEO_EXTENSIONS:
            files.extend(folder_path.glob(f"*{ext}"))

    return sorted(files)


def batch_process(
    input_folder: str,
    output_folder: str,
    target_width: int,
    target_height: int,
    mode: AspectRatioMode = AspectRatioMode.LETTERBOX,
    anchor: CropAnchor = CropAnchor.CENTER,
    letterbox_color: Tuple[int, int, int] = LETTERBOX_COLOR_BLACK,
    media_type: str = "both",
) -> None:
    """
    Batch process all media files in a folder.

    Args:
        input_folder: Input folder path
        output_folder: Output folder path
        target_width: Target width
        target_height: Target height
        mode: AspectRatioMode (LETTERBOX or CROP)
        anchor: CropAnchor position (for CROP mode)
        letterbox_color: BGR color for letterbox bars (default: black)
        media_type: "images", "videos", or "both"
    """
    # Ensure output folder exists
    output_path = Path(output_folder)
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
        msg.info(folder_created_info(output_folder))

    # Get media files
    media_files = get_media_files(input_folder, media_type)

    if not media_files:
        msg.warning(no_media_files_warning(input_folder))
        msg.info(folder_setup_instructions(input_folder, output_folder))
        return

    batch_started(len(media_files), "files")

    success_count = 0
    for media_file in media_files:
        input_file = str(media_file)
        output_file = os.path.join(output_folder, media_file.name)

        # Determine if image or video
        ext = media_file.suffix.lower()
        is_image = ext in IMAGE_EXTENSIONS

        if is_image:
            success = process_image(
                input_file,
                output_file,
                target_width,
                target_height,
                mode,
                anchor,
                letterbox_color,
            )
        else:
            success = process_video(
                input_file,
                output_file,
                target_width,
                target_height,
                mode,
                anchor,
                letterbox_color,
            )

        if success:
            success_count += 1

    batch_completed(success_count, "files")
    msg.info(output_saved_to_folder_info(output_folder))


def get_aspect_ratio_input() -> Tuple[int, int]:
    """Get aspect ratio from user input."""
    print("\nCommon aspect ratios:")
    print("1. 16:9 (1920x1080) - Widescreen")
    print("2. 4:3 (1024x768) - Standard")
    print("3. 1:1 (1080x1080) - Square")
    print("4. 9:16 (1080x1920) - Vertical/Portrait")
    print("5. 21:9 (2560x1080) - Ultra-wide")
    print("6. Custom")

    choice = input("\nSelect aspect ratio (1-6): ").strip()

    if choice == "1":
        return ASPECT_RATIO_16_9
    elif choice == "2":
        return ASPECT_RATIO_4_3
    elif choice == "3":
        return ASPECT_RATIO_1_1
    elif choice == "4":
        return ASPECT_RATIO_9_16
    elif choice == "5":
        return ASPECT_RATIO_21_9
    elif choice == "6":
        try:
            width = int(input("Enter target width: ").strip())
            height = int(input("Enter target height: ").strip())
            return width, height
        except ValueError:
            msg.warning(invalid_input_default_warning("1920x1080"))
            return ASPECT_RATIO_16_9
    else:
        msg.warning(invalid_choice_default_warning("16:9 (1920x1080)"))
        return ASPECT_RATIO_16_9


def get_mode_input() -> AspectRatioMode:
    """Get processing mode from user input."""
    print("\nAspect ratio adjustment mode:")
    print("1. Letterbox - Add bars to preserve full image")
    print("2. Crop - Crop image to fit aspect ratio")

    choice = input("\nSelect mode (1-2): ").strip()

    if choice == "2":
        return AspectRatioMode.CROP
    else:
        return AspectRatioMode.LETTERBOX


def get_anchor_input() -> CropAnchor:
    """Get crop anchor from user input."""
    print("\nCrop focus position:")
    print("1. Center")
    print("2. Upper Left")
    print("3. Upper Center")
    print("4. Upper Right")
    print("5. Center Left")
    print("6. Center Right")
    print("7. Lower Left")
    print("8. Lower Center")
    print("9. Lower Right")

    choice = input("\nSelect crop focus (1-9, default: 1): ").strip()

    if choice == "2":
        return CropAnchor.UPPER_LEFT
    elif choice == "3":
        return CropAnchor.UPPER_CENTER
    elif choice == "4":
        return CropAnchor.UPPER_RIGHT
    elif choice == "5":
        return CropAnchor.CENTER_LEFT
    elif choice == "6":
        return CropAnchor.CENTER_RIGHT
    elif choice == "7":
        return CropAnchor.LOWER_LEFT
    elif choice == "8":
        return CropAnchor.LOWER_CENTER
    elif choice == "9":
        return CropAnchor.LOWER_RIGHT
    else:
        return CropAnchor.CENTER


def get_letterbox_color_input() -> Tuple[int, int, int]:
    """Get letterbox color from user input."""
    print("\nLetterbox bar color:")
    print("1. Black (0, 0, 0)")
    print("2. White (255, 255, 255)")
    print("3. Gray (128, 128, 128)")
    print("4. Custom RGB")

    choice = input("\nSelect color (1-4, default: 1): ").strip()

    if choice == "2":
        return LETTERBOX_COLOR_WHITE
    elif choice == "3":
        return LETTERBOX_COLOR_GRAY
    elif choice == "4":
        try:
            r = int(input(f"Enter Red value ({COLOR_MIN_VALUE}-{COLOR_MAX_VALUE}): ").strip())
            g = int(input(f"Enter Green value ({COLOR_MIN_VALUE}-{COLOR_MAX_VALUE}): ").strip())
            b = int(input(f"Enter Blue value ({COLOR_MIN_VALUE}-{COLOR_MAX_VALUE}): ").strip())
            # Clamp values to valid range
            r = max(COLOR_MIN_VALUE, min(COLOR_MAX_VALUE, r))
            g = max(COLOR_MIN_VALUE, min(COLOR_MAX_VALUE, g))
            b = max(COLOR_MIN_VALUE, min(COLOR_MAX_VALUE, b))
            return (b, g, r)  # OpenCV uses BGR format
        except ValueError:
            msg.warning(invalid_input_default_warning("black (0, 0, 0)"))
            return LETTERBOX_COLOR_BLACK
    else:
        return LETTERBOX_COLOR_BLACK


def main():
    """Main function."""
    print("=" * 60)
    print("Aspect Ratio Changer - Images & Videos")
    print("=" * 60)

    # Get media type
    print("\nProcess:")
    print("1. Images only")
    print("2. Videos only")
    print("3. Both images and videos")

    type_choice = input("\nSelect option (1-3, default: 1): ").strip()

    if type_choice == "2":
        media_type = "videos"
        default_input = DEFAULT_VIDEOS_INPUT_DIR
        default_output = DEFAULT_VIDEOS_OUTPUT_DIR
    elif type_choice == "3":
        media_type = "both"
        default_input = DEFAULT_IMAGES_INPUT_DIR  # Use images as default
        default_output = DEFAULT_IMAGES_OUTPUT_DIR
    else:
        media_type = "images"
        default_input = DEFAULT_IMAGES_INPUT_DIR
        default_output = DEFAULT_IMAGES_OUTPUT_DIR

    # Get folders
    input_folder = (
        input(f"\nEnter input folder (default: '{default_input}'): ").strip()
        or default_input
    )
    output_folder = (
        input(f"Enter output folder (default: '{default_output}'): ").strip()
        or default_output
    )

    # Get aspect ratio
    target_width, target_height = get_aspect_ratio_input()

    # Get mode
    mode = get_mode_input()

    # Get crop anchor if cropping, or letterbox color if letterboxing
    if mode == AspectRatioMode.CROP:
        anchor = get_anchor_input()
        letterbox_color = LETTERBOX_COLOR_BLACK  # Not used for crop mode
    else:
        anchor = CropAnchor.CENTER
        letterbox_color = get_letterbox_color_input()

    # Process
    print(f"\nProcessing {media_type} from '{input_folder}' to '{output_folder}'")
    print(f"Target dimensions: {target_width}x{target_height}")
    print(f"Mode: {mode.value}")
    if mode == AspectRatioMode.CROP:
        print(f"Crop anchor: {anchor.value}")
    else:
        print(f"Letterbox color: BGR{letterbox_color}")
    print()

    batch_process(
        input_folder,
        output_folder,
        target_width,
        target_height,
        mode,
        anchor,
        letterbox_color,
        media_type,
    )


if __name__ == "__main__":
    main()
