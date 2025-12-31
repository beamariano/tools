"""
Centralized message handling library for consistent error, success, warning,
and info messages across all tools.
"""

import sys
from enum import Enum
from pathlib import Path


class MessageType(Enum):
    """Message type enumeration."""
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    INFO = "INFO"


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class MessageHandler:
    """Handles formatted messages with colors and prefixes."""

    def __init__(self, use_colors=True):
        """
        Initialize message handler.

        Args:
            use_colors: Enable colored output (default: True)
        """
        self.use_colors = use_colors and sys.stdout.isatty()

    def _format(self, msg_type, message, prefix=None):
        """
        Format a message with color and prefix.

        Args:
            msg_type: MessageType enum value
            message: Message text
            prefix: Optional prefix (defaults to msg_type name)

        Returns:
            Formatted message string
        """
        if prefix is None:
            prefix = msg_type.value

        if not self.use_colors:
            return f"[{prefix}] {message}"

        color_map = {
            MessageType.ERROR: Colors.RED,
            MessageType.SUCCESS: Colors.GREEN,
            MessageType.WARNING: Colors.YELLOW,
            MessageType.INFO: Colors.CYAN,
        }

        color = color_map.get(msg_type, Colors.WHITE)
        return f"{color}{Colors.BOLD}[{prefix}]{Colors.RESET} {message}"

    def error(self, message, prefix="ERROR"):
        """Print error message to stderr."""
        print(self._format(MessageType.ERROR, message, prefix), file=sys.stderr)

    def success(self, message, prefix="SUCCESS"):
        """Print success message."""
        print(self._format(MessageType.SUCCESS, message, prefix))

    def warning(self, message, prefix="WARNING"):
        """Print warning message."""
        print(self._format(MessageType.WARNING, message, prefix))

    def info(self, message, prefix="INFO"):
        """Print info message."""
        print(self._format(MessageType.INFO, message, prefix))


class ToolException(Exception):
    """Base exception class for tool errors."""

    def __init__(self, message, exit_code=1):
        """
        Initialize exception.

        Args:
            message: Error message
            exit_code: Exit code to use when terminating (default: 1)
        """
        super().__init__(message)
        self.exit_code = exit_code


class FileNotFoundError(ToolException):
    """Raised when a required file is not found."""
    pass


class InvalidFormatError(ToolException):
    """Raised when file format is invalid or unsupported."""
    pass


class ProcessingError(ToolException):
    """Raised when image/video processing fails."""
    pass


class ValidationError(ToolException):
    """Raised when input validation fails."""
    pass


# Global message handler instance
msg = MessageHandler()


# Convenience functions for common messages
def file_not_found(file_path):
    """Standard file not found error message."""
    msg.error(f"File not found: {file_path}")
    raise FileNotFoundError(f"File not found: {file_path}")


def invalid_format(file_path, expected_formats):
    """Standard invalid format error message."""
    formats_str = ", ".join(expected_formats)
    msg.error(f"Invalid format: {file_path}. Expected: {formats_str}")
    raise InvalidFormatError(f"Invalid format: {file_path}")


def processing_failed(operation, reason):
    """Standard processing failure error message."""
    msg.error(f"{operation} failed: {reason}")
    raise ProcessingError(f"{operation} failed: {reason}")


def validation_failed(field, reason):
    """Standard validation error message."""
    msg.error(f"Validation failed for {field}: {reason}")
    raise ValidationError(f"Validation failed for {field}: {reason}")


def file_created(file_path, size_kb=None):
    """Standard file creation success message."""
    path = Path(file_path)
    size_str = f" ({size_kb:.2f} KB)" if size_kb else ""
    msg.success(f"Created: {path.name}{size_str}")


def file_processed(file_path, original_size_kb=None, new_size_kb=None):
    """Standard file processing success message."""
    path = Path(file_path)

    if original_size_kb and new_size_kb:
        reduction = ((original_size_kb - new_size_kb) / original_size_kb) * 100
        msg.success(f"Processed: {path.name} ({original_size_kb:.2f} KB → {new_size_kb:.2f} KB, {reduction:.1f}% reduction)")
    else:
        msg.success(f"Processed: {path.name}")


def processing_started(operation, file_path=None):
    """Standard processing started info message."""
    if file_path:
        path = Path(file_path)
        msg.info(f"{operation}: {path.name}")
    else:
        msg.info(operation)


def batch_started(count, item_type="items"):
    """Standard batch processing started message."""
    msg.info(f"Found {count} {item_type} to process")


def batch_completed(count, item_type="items"):
    """Standard batch processing completed message."""
    msg.success(f"Completed processing {count} {item_type}")


def size_info(original_kb, optimized_kb):
    """
    Display file size comparison.

    Args:
        original_kb: Original file size in KB
        optimized_kb: Optimized file size in KB
    """
    reduction = ((original_kb - optimized_kb) / original_kb) * 100
    print(f"  Original:  {original_kb:.2f} KB")
    print(f"  Optimized: {optimized_kb:.2f} KB")

    if reduction > 0:
        print(f"  {Colors.GREEN}Reduction: {reduction:.1f}%{Colors.RESET}")
    else:
        print(f"  {Colors.YELLOW}Size increased by {abs(reduction):.1f}%{Colors.RESET}")


def dimensions_info(width, height, operation="Resized"):
    """Display dimension information."""
    print(f"  {operation} to: {width}x{height}")


def progress_indicator(current, total, prefix="Processing"):
    """
    Display progress indicator.

    Args:
        current: Current item number (1-indexed)
        total: Total number of items
        prefix: Prefix text (default: "Processing")
    """
    percentage = (current / total) * 100
    msg.info(f"{prefix} {current}/{total} ({percentage:.0f}%)")


def handle_exception(exception, verbose=False):
    """
    Handle exceptions consistently.

    Args:
        exception: Exception to handle
        verbose: Show full traceback (default: False)

    Returns:
        Exit code
    """
    if isinstance(exception, ToolException):
        msg.error(str(exception))
        if verbose:
            import traceback
            traceback.print_exc()
        return exception.exit_code
    else:
        msg.error(f"Unexpected error: {exception}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


# Emoji support (optional, can be disabled)
class Emoji:
    """Common emoji for messages (only if terminal supports it)."""
    CHECK = "✓"
    CROSS = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    ARROW = "→"
    SPARKLES = "✨"
    GEAR = "⚙"
    PACKAGE = "📦"
    IMAGE = "🖼"
    VIDEO = "🎥"
    ROCKET = "🚀"


def use_emoji():
    """Check if emoji should be used based on terminal support."""
    return sys.stdout.isatty() and sys.stdout.encoding.lower() in ['utf-8', 'utf8']


# Format conversion messages
def transparency_loss_warning(source_format, target_format):
    """Warning for losing transparency during conversion."""
    return f"Converting from {source_format} to {target_format} will lose transparency"


def quality_loss_warning(source_format, target_format):
    """Warning for losing quality during conversion."""
    return f"Converting from lossless {source_format} to lossy {target_format} will degrade quality"


def jpeg_transparency_warning():
    """Warning for JPEG not supporting transparency."""
    return "JPEG does not support transparency. Consider using PNG or WEBP instead."


def unsupported_extension_error(extension):
    """Error message for unsupported file extensions."""
    return f"Unsupported file extension: {extension}"


def unsupported_format_error(format_name):
    """Error message for unsupported formats."""
    return f"Unsupported format: {format_name}"


# Video processing messages
def video_open_error(video_path):
    """Error message for video opening failure."""
    return f"Could not open video {video_path}"


def video_no_frames_error(video_path):
    """Error message for video with no frames."""
    return f"No frames in {video_path}"


def video_processing_error(video_path, reason):
    """Error message for video processing failure."""
    return f"Error processing {video_path}: {reason}"


def folder_not_exist_error(folder_path):
    """Error message for non-existent folder."""
    return f"Folder '{folder_path}' does not exist"


def invalid_input_warning(default_value):
    """Warning for invalid input."""
    return f"Invalid input. Using default: {default_value}"


def invalid_choice_error():
    """Error message for invalid choice."""
    return "Invalid choice!"


def video_mapped_success(filename, original_duration, target_duration):
    """Success message for video mapping."""
    return f"Mapped {filename}: {filename} (original: {original_duration:.2f}s, set to: {target_duration:.2f}s)"


def video_mapping_error(filename):
    """Error message for video mapping failure."""
    return f"Error processing {filename}"


def mapping_saved_success(output_file):
    """Success message for mapping file saved."""
    return f"Mapping saved to '{output_file}'"


def total_processed_info(count):
    """Info message for total videos processed."""
    return f"Total videos processed: {count}"


def video_created_success(output_video, duration):
    """Success message for video creation."""
    return f"Created {output_video} with {duration:.2f}s duration"


def processing_videos_info(duration):
    """Info message for processing videos."""
    return f"Processing videos to {duration:.2f}s duration..."


def batch_complete_success(count, duration):
    """Success message for batch processing completion."""
    return f"Processed {count} videos to {duration:.2f}s"


def output_saved_info(folder):
    """Info message for output saved."""
    return f"Output saved to '{folder}' folder"


def folder_created_info(folder):
    """Info message for folder creation."""
    return f"Created folder: '{folder}'"


def folder_setup_instructions(input_folder, output_folder=None):
    """Instructions for setting up required folders."""
    if output_folder:
        return f"Place your files in '{input_folder}/' folder. Output will be saved to '{output_folder}/'"
    return f"Place your files in '{input_folder}/' folder"


def checking_folder_info(folder):
    """Info message for checking folder existence."""
    return f"Checking for '{folder}' folder..."


# Helper context manager for operation tracking
class Operation:
    """Context manager for tracking operations with start/end messages."""

    def __init__(self, name, show_duration=True):
        """
        Initialize operation tracker.

        Args:
            name: Operation name
            show_duration: Show elapsed time on completion (default: True)
        """
        self.name = name
        self.show_duration = show_duration
        self.start_time: float = 0.0

    def __enter__(self):
        """Start operation."""
        import time
        self.start_time = time.time()
        msg.info(f"Starting: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End operation."""
        import time

        if exc_type is not None:
            # An exception occurred
            msg.error(f"Failed: {self.name}")
            return False

        elapsed = time.time() - self.start_time

        if self.show_duration:
            if elapsed < 1:
                duration_str = f" ({elapsed*1000:.0f}ms)"
            else:
                duration_str = f" ({elapsed:.2f}s)"
        else:
            duration_str = ""

        msg.success(f"Completed: {self.name}{duration_str}")
        return True
