import cv2
import os
import numpy as np
from pathlib import Path
from typing import Optional, List

from constants import (
    VIDEO_EXTENSIONS,
    DEFAULT_INPUT_FOLDER,
    DEFAULT_OUTPUT_FOLDER,
    DEFAULT_MAPPING_FILE,
    DEFAULT_TARGET_DURATION,
    DEFAULT_FADE_DURATION,
)
from messages import (
    msg,
    video_open_error,
    video_no_frames_error,
    video_processing_error,
    folder_not_exist_error,
    invalid_input_warning,
    invalid_choice_error,
    video_mapped_success,
    video_mapping_error,
    mapping_saved_success,
    total_processed_info,
    video_created_success,
    processing_videos_info,
    batch_complete_success,
    output_saved_info,
    folder_created_info,
    folder_setup_instructions,
)


def ensure_folder_exists(folder: str, create: bool = True) -> bool:
    """
    Ensure folder exists, optionally creating it.

    Args:
        folder: Folder path to check/create
        create: Whether to create the folder if it doesn't exist

    Returns:
        True if folder exists or was created, False otherwise
    """
    folder_path = Path(folder)
    if not folder_path.exists():
        if create:
            folder_path.mkdir(parents=True, exist_ok=True)
            msg.info(folder_created_info(folder))
            return True
        else:
            msg.error(folder_not_exist_error(folder))
            msg.info(folder_setup_instructions(folder))
            return False
    return True


def get_video_files(folder: str) -> List[Path]:
    """Get all video files from a folder"""
    folder_path = Path(folder)
    if not folder_path.exists():
        msg.error(folder_not_exist_error(folder))
        msg.info(folder_setup_instructions(folder))
        return []

    video_files = []
    for ext in VIDEO_EXTENSIONS:
        video_files.extend(folder_path.glob(f"*{ext}"))

    return sorted(video_files)


def get_video_duration(video_path: str) -> Optional[float]:
    """Get the duration of a video file in seconds"""
    try:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            msg.error(video_open_error(video_path))
            return None

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        if fps > 0:
            duration = frame_count / fps
        else:
            duration = 0

        cap.release()
        return duration
    except Exception as e:
        msg.error(video_processing_error(video_path, e))
        return None


def apply_fade(frame: np.ndarray, alpha: float) -> np.ndarray:
    """Apply fade effect to a frame using alpha blending"""
    return (frame * alpha).astype(np.uint8)


def create_video_mapping(
    input_folder: str = DEFAULT_INPUT_FOLDER,
    output_file: str = DEFAULT_MAPPING_FILE,
    target_duration: float = DEFAULT_TARGET_DURATION,
) -> None:
    """
    Create a mapping of all video files in a folder with their durations.
    Works with any video filenames, not just numbered files.
    """
    video_files = get_video_files(input_folder)

    if not video_files:
        msg.error(folder_not_exist_error(input_folder))
        return

    # Create mapping
    mapping = []

    for video_path in video_files:
        video_filename = video_path.name
        duration = get_video_duration(str(video_path))

        if duration is not None:
            mapping.append(
                f"{video_filename} - Original: {duration:.2f}s, Target: {target_duration:.2f}s"
            )
            msg.success(video_mapped_success(video_filename, duration, target_duration))
        else:
            mapping.append(f"{video_filename} - ERROR")
            msg.error(video_mapping_error(video_filename))

    # Write mapping to file
    with open(output_file, "w") as f:
        f.write("Video Mapping (Filename - Durations)\n")
        f.write(f"Target Duration: {target_duration:.2f}s\n")
        f.write("=" * 50 + "\n\n")
        for line in mapping:
            f.write(line + "\n")

    msg.success(mapping_saved_success(output_file))
    msg.info(total_processed_info(len([m for m in mapping if "ERROR" not in m])))


def create_video_with_duration(
    input_video: str,
    output_video: str,
    target_duration: float = DEFAULT_TARGET_DURATION,
    fade_duration: float = DEFAULT_FADE_DURATION,
    apply_fades: bool = False,
) -> bool:
    """
    Create a new video from input video with specified duration.
    If input is longer, it will be trimmed. If shorter, it will loop.
    Optionally applies fade in and fade out effects.
    """
    cap = cv2.VideoCapture(input_video)

    if not cap.isOpened():
        msg.error(video_open_error(input_video))
        return False

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Calculate target frame count
    target_frames = int(target_duration * fps)
    fade_frames = int(fade_duration * fps) if apply_fades else 0

    # Define codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore[attr-defined]
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    frames_written = 0
    all_frames = []

    # Read all frames from input video
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        all_frames.append(frame)

    cap.release()

    if len(all_frames) == 0:
        msg.error(video_no_frames_error(input_video))
        return False

    # Write frames until we reach target duration
    while frames_written < target_frames:
        frame_idx = frames_written % len(all_frames)
        frame = all_frames[frame_idx].copy()

        # Apply fade effects if enabled
        if apply_fades:
            # Fade in at the beginning
            if frames_written < fade_frames:
                alpha = frames_written / fade_frames
                frame = apply_fade(frame, alpha)
            # Fade out at the end
            elif frames_written >= target_frames - fade_frames:
                alpha = (target_frames - frames_written) / fade_frames
                frame = apply_fade(frame, alpha)

        out.write(frame)
        frames_written += 1

    out.release()
    msg.success(video_created_success(output_video, target_duration))
    return True


def batch_adjust_durations(
    input_folder: str = DEFAULT_INPUT_FOLDER,
    output_folder: str = DEFAULT_OUTPUT_FOLDER,
    target_duration: float = DEFAULT_TARGET_DURATION,
    fade_duration: float = DEFAULT_FADE_DURATION,
    apply_fades: bool = False,
) -> None:
    """
    Batch process all video files in a folder to have the specified duration.
    Works with any video filenames, not just numbered files.
    """
    # Ensure output folder exists (create it)
    ensure_folder_exists(output_folder, create=True)

    # Check input folder exists
    if not ensure_folder_exists(input_folder, create=False):
        return

    video_files = get_video_files(input_folder)

    if not video_files:
        msg.warning(f"No video files found in '{input_folder}'")
        msg.info(folder_setup_instructions(input_folder, output_folder))
        return

    msg.info(processing_videos_info(target_duration))

    success_count = 0
    for video_path in video_files:
        input_file = str(video_path)
        output_file = os.path.join(output_folder, video_path.name)

        if create_video_with_duration(
            input_file, output_file, target_duration, fade_duration, apply_fades
        ):
            success_count += 1

    msg.success(batch_complete_success(success_count, target_duration))
    msg.info(output_saved_info(output_folder))


def get_float_input(prompt: str, default: float) -> float:
    """Helper function to get float input with default value"""
    user_input = input(prompt).strip()
    if not user_input:
        return default
    try:
        return float(user_input)
    except ValueError:
        msg.warning(invalid_input_warning(default))
        return default


def get_yes_no_input(prompt: str, default: bool = False) -> bool:
    """Helper function to get yes/no input"""
    user_input = input(prompt).strip().lower()
    if not user_input:
        return default
    return user_input in ["y", "yes", "true", "1"]


def main():
    """
    Main function - choose what you want to do:
    1. Create mapping of existing videos
    2. Adjust all videos to a specified duration with optional fade effects
    """

    print("Video Mapping & Duration Adjuster")
    print("=" * 50)
    print("\nDefault folders:")
    print(f"  Input:  {DEFAULT_INPUT_FOLDER}/")
    print(f"  Output: {DEFAULT_OUTPUT_FOLDER}/")
    print("\nOptions:")
    print("1. Create mapping of all videos in folder")
    print("2. Adjust all videos to specified duration")
    print("3. Both (mapping + adjustment)")

    choice = input("\nEnter choice (1/2/3): ").strip()

    input_folder = (
        input(f"Enter input folder name (default: '{DEFAULT_INPUT_FOLDER}'): ").strip()
        or DEFAULT_INPUT_FOLDER
    )

    # Get target duration for all operations
    target_duration = get_float_input(
        f"Enter target duration in seconds (default: {DEFAULT_TARGET_DURATION}): ",
        DEFAULT_TARGET_DURATION,
    )

    if choice == "1":
        mapping_file = (
            input(
                f"Enter mapping file name (default: '{DEFAULT_MAPPING_FILE}'): "
            ).strip()
            or DEFAULT_MAPPING_FILE
        )
        create_video_mapping(input_folder, mapping_file, target_duration)

    elif choice == "2":
        output_folder = (
            input(
                f"Enter output folder name (default: '{DEFAULT_OUTPUT_FOLDER}'): "
            ).strip()
            or DEFAULT_OUTPUT_FOLDER
        )

        apply_fades = get_yes_no_input(
            "Apply fade in/out effects? (y/n, default: n): ", default=False
        )

        fade_duration = DEFAULT_FADE_DURATION
        if apply_fades:
            fade_duration = get_float_input(
                f"Enter fade duration in seconds (default: {DEFAULT_FADE_DURATION}): ",
                DEFAULT_FADE_DURATION,
            )

        batch_adjust_durations(
            input_folder, output_folder, target_duration, fade_duration, apply_fades
        )

    elif choice == "3":
        mapping_file = (
            input(
                f"Enter mapping file name (default: '{DEFAULT_MAPPING_FILE}'): "
            ).strip()
            or DEFAULT_MAPPING_FILE
        )
        create_video_mapping(input_folder, mapping_file, target_duration)

        output_folder = (
            input(
                f"Enter output folder name (default: '{DEFAULT_OUTPUT_FOLDER}'): "
            ).strip()
            or DEFAULT_OUTPUT_FOLDER
        )

        apply_fades = get_yes_no_input(
            "Apply fade in/out effects? (y/n, default: n): ", default=False
        )

        fade_duration = DEFAULT_FADE_DURATION
        if apply_fades:
            fade_duration = get_float_input(
                f"Enter fade duration in seconds (default: {DEFAULT_FADE_DURATION}): ",
                DEFAULT_FADE_DURATION,
            )

        batch_adjust_durations(
            input_folder, output_folder, target_duration, fade_duration, apply_fades
        )

    else:
        msg.error(invalid_choice_error())


if __name__ == "__main__":
    main()
