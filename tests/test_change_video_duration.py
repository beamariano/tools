"""Tests for change_video_duration module."""

from pathlib import Path
import sys
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from change_video_duration import (
    ensure_folder_exists,
    get_video_files,
    apply_fade,
    get_float_input,
    get_yes_no_input,
)
from constants import VIDEO_EXTENSIONS
import numpy as np


class TestEnsureFolderExists:
    """Test ensure_folder_exists function."""

    def test_existing_folder(self, temp_dir):
        """Test with existing folder."""
        result = ensure_folder_exists(str(temp_dir), create=False)
        assert result is True

    def test_nonexistent_folder_create(self, temp_dir):
        """Test creating non-existent folder."""
        new_folder = temp_dir / "new_folder"
        result = ensure_folder_exists(str(new_folder), create=True)
        assert result is True
        assert new_folder.exists()

    def test_nonexistent_folder_no_create(self, temp_dir, capsys):
        """Test non-existent folder without creation."""
        new_folder = temp_dir / "new_folder"
        result = ensure_folder_exists(str(new_folder), create=False)
        assert result is False
        assert not new_folder.exists()
        captured = capsys.readouterr()
        assert "exist" in captured.err.lower()

    def test_nested_folder_creation(self, temp_dir):
        """Test creating nested folders."""
        nested_folder = temp_dir / "level1" / "level2" / "level3"
        result = ensure_folder_exists(str(nested_folder), create=True)
        assert result is True
        assert nested_folder.exists()


class TestGetVideoFiles:
    """Test get_video_files function."""

    def test_empty_folder(self, temp_dir):
        """Test with empty folder."""
        files = get_video_files(str(temp_dir))
        assert files == []

    def test_nonexistent_folder(self, temp_dir):
        """Test with non-existent folder."""
        non_existent = temp_dir / "missing"
        files = get_video_files(str(non_existent))
        assert files == []

    def test_folder_with_video_files(self, temp_dir):
        """Test folder containing video files."""
        # Create mock video files
        (temp_dir / "video1.mp4").touch()
        (temp_dir / "video2.avi").touch()
        (temp_dir / "image.jpg").touch()  # Non-video file

        files = get_video_files(str(temp_dir))
        assert len(files) == 2
        assert all(f.suffix in VIDEO_EXTENSIONS for f in files)

    def test_sorted_output(self, temp_dir):
        """Test that output is sorted."""
        (temp_dir / "c.mp4").touch()
        (temp_dir / "a.mp4").touch()
        (temp_dir / "b.mp4").touch()

        files = get_video_files(str(temp_dir))
        file_names = [f.name for f in files]
        assert file_names == sorted(file_names)


class TestApplyFade:
    """Test apply_fade function."""

    def test_fade_full_opacity(self):
        """Test fade with alpha=1.0 (full opacity)."""
        frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
        result = apply_fade(frame, 1.0)
        np.testing.assert_array_equal(result, frame)

    def test_fade_zero_opacity(self):
        """Test fade with alpha=0.0 (fully transparent)."""
        frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
        result = apply_fade(frame, 0.0)
        expected = np.zeros((100, 100, 3), dtype=np.uint8)
        np.testing.assert_array_equal(result, expected)

    def test_fade_half_opacity(self):
        """Test fade with alpha=0.5 (half opacity)."""
        frame = np.ones((100, 100, 3), dtype=np.uint8) * 200
        result = apply_fade(frame, 0.5)
        expected = np.ones((100, 100, 3), dtype=np.uint8) * 100
        np.testing.assert_array_equal(result, expected)

    def test_fade_maintains_shape(self):
        """Test that fade maintains frame shape."""
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        result = apply_fade(frame, 0.7)
        assert result.shape == frame.shape

    def test_fade_output_dtype(self):
        """Test that output has correct dtype."""
        frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
        result = apply_fade(frame, 0.5)
        assert result.dtype == np.uint8


class TestGetFloatInput:
    """Test get_float_input function."""

    @patch('builtins.input', return_value='3.5')
    def test_valid_float_input(self, mock_input):
        """Test valid float input."""
        result = get_float_input("Enter value: ", 2.0)
        assert result == 3.5

    @patch('builtins.input', return_value='')
    def test_empty_input_returns_default(self, mock_input):
        """Test empty input returns default."""
        result = get_float_input("Enter value: ", 2.0)
        assert result == 2.0

    @patch('builtins.input', return_value='   ')
    def test_whitespace_input_returns_default(self, mock_input):
        """Test whitespace input returns default."""
        result = get_float_input("Enter value: ", 2.0)
        assert result == 2.0

    @patch('builtins.input', return_value='invalid')
    def test_invalid_input_returns_default(self, mock_input, capsys):
        """Test invalid input returns default with warning."""
        result = get_float_input("Enter value: ", 2.0)
        assert result == 2.0
        captured = capsys.readouterr()
        assert "invalid" in captured.out.lower()


class TestGetYesNoInput:
    """Test get_yes_no_input function."""

    @patch('builtins.input', return_value='y')
    def test_yes_input(self, mock_input):
        """Test 'y' input returns True."""
        result = get_yes_no_input("Continue? ", default=False)
        assert result is True

    @patch('builtins.input', return_value='yes')
    def test_yes_word_input(self, mock_input):
        """Test 'yes' input returns True."""
        result = get_yes_no_input("Continue? ", default=False)
        assert result is True

    @patch('builtins.input', return_value='n')
    def test_no_input(self, mock_input):
        """Test 'n' input returns False."""
        result = get_yes_no_input("Continue? ", default=True)
        assert result is False

    @patch('builtins.input', return_value='')
    def test_empty_input_returns_default_true(self, mock_input):
        """Test empty input returns default True."""
        result = get_yes_no_input("Continue? ", default=True)
        assert result is True

    @patch('builtins.input', return_value='')
    def test_empty_input_returns_default_false(self, mock_input):
        """Test empty input returns default False."""
        result = get_yes_no_input("Continue? ", default=False)
        assert result is False

    @patch('builtins.input', return_value='1')
    def test_one_input(self, mock_input):
        """Test '1' input returns True."""
        result = get_yes_no_input("Continue? ", default=False)
        assert result is True

    @patch('builtins.input', return_value='YES')
    def test_case_insensitive(self, mock_input):
        """Test input is case insensitive."""
        result = get_yes_no_input("Continue? ", default=False)
        assert result is True
