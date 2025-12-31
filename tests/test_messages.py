"""Tests for messages module."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from messages import (
    MessageType,
    MessageHandler,
    ToolException,
    FileNotFoundError,
    InvalidFormatError,
    ProcessingError,
    ValidationError,
    transparency_loss_warning,
    quality_loss_warning,
    jpeg_transparency_warning,
    unsupported_extension_error,
    unsupported_format_error,
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


class TestMessageType:
    """Test MessageType enum."""

    def test_message_type_values(self):
        """Test MessageType enum values."""
        assert MessageType.ERROR.value == "ERROR"
        assert MessageType.SUCCESS.value == "SUCCESS"
        assert MessageType.WARNING.value == "WARNING"
        assert MessageType.INFO.value == "INFO"


class TestMessageHandler:
    """Test MessageHandler class."""

    @pytest.fixture
    def handler(self):
        """Create MessageHandler for testing."""
        return MessageHandler(use_colors=False)

    @pytest.fixture
    def colored_handler(self):
        """Create MessageHandler with colors for testing."""
        return MessageHandler(use_colors=True)

    def test_init_no_colors(self):
        """Test MessageHandler initialization without colors."""
        handler = MessageHandler(use_colors=False)
        assert handler.use_colors is False

    def test_error_message(self, handler, capsys):
        """Test error message output."""
        handler.error("Test error")
        captured = capsys.readouterr()
        assert "ERROR" in captured.err
        assert "Test error" in captured.err

    def test_success_message(self, handler, capsys):
        """Test success message output."""
        handler.success("Test success")
        captured = capsys.readouterr()
        assert "SUCCESS" in captured.out
        assert "Test success" in captured.out

    def test_warning_message(self, handler, capsys):
        """Test warning message output."""
        handler.warning("Test warning")
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "Test warning" in captured.out

    def test_info_message(self, handler, capsys):
        """Test info message output."""
        handler.info("Test info")
        captured = capsys.readouterr()
        assert "INFO" in captured.out
        assert "Test info" in captured.out

    def test_custom_prefix(self, handler, capsys):
        """Test custom message prefix."""
        handler.error("Test", prefix="CUSTOM")
        captured = capsys.readouterr()
        assert "CUSTOM" in captured.err


class TestExceptions:
    """Test custom exception classes."""

    def test_tool_exception(self):
        """Test ToolException base class."""
        exc = ToolException("Test error", exit_code=2)
        assert str(exc) == "Test error"
        assert exc.exit_code == 2

    def test_tool_exception_default_exit_code(self):
        """Test ToolException default exit code."""
        exc = ToolException("Test error")
        assert exc.exit_code == 1

    def test_file_not_found_error(self):
        """Test FileNotFoundError exception."""
        exc = FileNotFoundError("File missing")
        assert isinstance(exc, ToolException)
        assert str(exc) == "File missing"

    def test_invalid_format_error(self):
        """Test InvalidFormatError exception."""
        exc = InvalidFormatError("Bad format")
        assert isinstance(exc, ToolException)

    def test_processing_error(self):
        """Test ProcessingError exception."""
        exc = ProcessingError("Processing failed")
        assert isinstance(exc, ToolException)

    def test_validation_error(self):
        """Test ValidationError exception."""
        exc = ValidationError("Validation failed")
        assert isinstance(exc, ToolException)


class TestFormatConversionMessages:
    """Test format conversion message functions."""

    def test_transparency_loss_warning(self):
        """Test transparency loss warning message."""
        msg = transparency_loss_warning("PNG", "JPEG")
        assert "PNG" in msg
        assert "JPEG" in msg
        assert "transparency" in msg.lower()

    def test_quality_loss_warning(self):
        """Test quality loss warning message."""
        msg = quality_loss_warning("PNG", "JPEG")
        assert "PNG" in msg
        assert "JPEG" in msg
        assert "quality" in msg.lower()

    def test_jpeg_transparency_warning(self):
        """Test JPEG transparency warning."""
        msg = jpeg_transparency_warning()
        assert "JPEG" in msg
        assert "transparency" in msg.lower()

    def test_unsupported_extension_error(self):
        """Test unsupported extension error message."""
        msg = unsupported_extension_error(".xyz")
        assert ".xyz" in msg
        assert "unsupported" in msg.lower()

    def test_unsupported_format_error(self):
        """Test unsupported format error message."""
        msg = unsupported_format_error("XYZ")
        assert "XYZ" in msg
        assert "unsupported" in msg.lower()


class TestVideoProcessingMessages:
    """Test video processing message functions."""

    def test_video_open_error(self):
        """Test video open error message."""
        msg = video_open_error("/path/to/video.mp4")
        assert "video.mp4" in msg
        assert "open" in msg.lower()

    def test_video_no_frames_error(self):
        """Test video no frames error message."""
        msg = video_no_frames_error("/path/to/video.mp4")
        assert "video.mp4" in msg
        assert "frames" in msg.lower()

    def test_video_processing_error(self):
        """Test video processing error message."""
        msg = video_processing_error("/path/to/video.mp4", "codec error")
        assert "video.mp4" in msg
        assert "codec error" in msg

    def test_folder_not_exist_error(self):
        """Test folder not exist error message."""
        msg = folder_not_exist_error("/path/to/folder")
        assert "/path/to/folder" in msg
        assert "exist" in msg.lower()

    def test_invalid_input_warning(self):
        """Test invalid input warning message."""
        msg = invalid_input_warning(3.0)
        assert "3.0" in msg
        assert "default" in msg.lower()

    def test_invalid_choice_error(self):
        """Test invalid choice error message."""
        msg = invalid_choice_error()
        assert "invalid" in msg.lower()
        assert "choice" in msg.lower()

    def test_video_mapped_success(self):
        """Test video mapped success message."""
        msg = video_mapped_success("video.mp4", 5.5, 3.0)
        assert "video.mp4" in msg
        assert "5.50" in msg
        assert "3.00" in msg

    def test_video_mapping_error(self):
        """Test video mapping error message."""
        msg = video_mapping_error("video.mp4")
        assert "video.mp4" in msg
        assert "error" in msg.lower()

    def test_mapping_saved_success(self):
        """Test mapping saved success message."""
        msg = mapping_saved_success("mapping.txt")
        assert "mapping.txt" in msg

    def test_total_processed_info(self):
        """Test total processed info message."""
        msg = total_processed_info(10)
        assert "10" in msg
        assert "processed" in msg.lower()

    def test_video_created_success(self):
        """Test video created success message."""
        msg = video_created_success("output.mp4", 3.0)
        assert "output.mp4" in msg
        assert "3.00" in msg

    def test_processing_videos_info(self):
        """Test processing videos info message."""
        msg = processing_videos_info(3.0)
        assert "3.00" in msg
        assert "processing" in msg.lower()

    def test_batch_complete_success(self):
        """Test batch complete success message."""
        msg = batch_complete_success(5, 3.0)
        assert "5" in msg
        assert "3.00" in msg

    def test_output_saved_info(self):
        """Test output saved info message."""
        msg = output_saved_info("output_folder")
        assert "output_folder" in msg

    def test_folder_created_info(self):
        """Test folder created info message."""
        msg = folder_created_info("new_folder")
        assert "new_folder" in msg

    def test_folder_setup_instructions_with_output(self):
        """Test folder setup instructions with output folder."""
        msg = folder_setup_instructions("input", "output")
        assert "input" in msg
        assert "output" in msg

    def test_folder_setup_instructions_without_output(self):
        """Test folder setup instructions without output folder."""
        msg = folder_setup_instructions("input")
        assert "input" in msg
