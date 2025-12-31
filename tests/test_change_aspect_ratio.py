"""Tests for change_aspect_ratio module."""

from pathlib import Path
import sys
import numpy as np
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from change_aspect_ratio import (
    AspectRatioMode,
    CropAnchor,
    calculate_crop_position,
    resize_with_aspect_ratio,
    get_media_files,
)


class TestAspectRatioMode:
    """Test AspectRatioMode enum."""

    def test_letterbox_mode(self):
        """Test letterbox mode value."""
        assert AspectRatioMode.LETTERBOX.value == "letterbox"

    def test_crop_mode(self):
        """Test crop mode value."""
        assert AspectRatioMode.CROP.value == "crop"


class TestCropAnchor:
    """Test CropAnchor enum."""

    def test_center_anchor(self):
        """Test center anchor value."""
        assert CropAnchor.CENTER.value == "center"

    def test_upper_left_anchor(self):
        """Test upper left anchor value."""
        assert CropAnchor.UPPER_LEFT.value == "upper_left"

    def test_upper_center_anchor(self):
        """Test upper center anchor value."""
        assert CropAnchor.UPPER_CENTER.value == "upper_center"

    def test_upper_right_anchor(self):
        """Test upper right anchor value."""
        assert CropAnchor.UPPER_RIGHT.value == "upper_right"

    def test_center_left_anchor(self):
        """Test center left anchor value."""
        assert CropAnchor.CENTER_LEFT.value == "center_left"

    def test_center_right_anchor(self):
        """Test center right anchor value."""
        assert CropAnchor.CENTER_RIGHT.value == "center_right"

    def test_lower_left_anchor(self):
        """Test lower left anchor value."""
        assert CropAnchor.LOWER_LEFT.value == "lower_left"

    def test_lower_center_anchor(self):
        """Test lower center anchor value."""
        assert CropAnchor.LOWER_CENTER.value == "lower_center"

    def test_lower_right_anchor(self):
        """Test lower right anchor value."""
        assert CropAnchor.LOWER_RIGHT.value == "lower_right"


class TestCalculateCropPosition:
    """Test calculate_crop_position function."""

    def test_center_crop_position(self):
        """Test center crop position calculation."""
        x, y = calculate_crop_position(1920, 1080, 1080, 1080, CropAnchor.CENTER)
        assert x == 420  # (1920 - 1080) / 2
        assert y == 0  # (1080 - 1080) / 2

    def test_upper_left_crop_position(self):
        """Test upper left crop position calculation."""
        x, y = calculate_crop_position(1920, 1080, 1080, 1080, CropAnchor.UPPER_LEFT)
        assert x == 0
        assert y == 0

    def test_upper_center_crop_position(self):
        """Test upper center crop position calculation."""
        x, y = calculate_crop_position(1920, 1080, 1080, 1080, CropAnchor.UPPER_CENTER)
        assert x == 420  # (1920 - 1080) / 2
        assert y == 0

    def test_upper_right_crop_position(self):
        """Test upper right crop position calculation."""
        x, y = calculate_crop_position(1920, 1080, 1080, 1080, CropAnchor.UPPER_RIGHT)
        assert x == 840  # 1920 - 1080
        assert y == 0

    def test_center_left_crop_position(self):
        """Test center left crop position calculation."""
        x, y = calculate_crop_position(1920, 1080, 1080, 1080, CropAnchor.CENTER_LEFT)
        assert x == 0
        assert y == 0  # (1080 - 1080) / 2

    def test_center_right_crop_position(self):
        """Test center right crop position calculation."""
        x, y = calculate_crop_position(1920, 1080, 1080, 1080, CropAnchor.CENTER_RIGHT)
        assert x == 840  # 1920 - 1080
        assert y == 0  # (1080 - 1080) / 2

    def test_lower_left_crop_position(self):
        """Test lower left crop position calculation."""
        x, y = calculate_crop_position(1920, 1080, 1080, 1080, CropAnchor.LOWER_LEFT)
        assert x == 0
        assert y == 0  # 1080 - 1080

    def test_lower_center_crop_position(self):
        """Test lower center crop position calculation."""
        x, y = calculate_crop_position(1920, 1080, 1080, 1080, CropAnchor.LOWER_CENTER)
        assert x == 420  # (1920 - 1080) / 2
        assert y == 0  # 1080 - 1080

    def test_lower_right_crop_position(self):
        """Test lower right crop position calculation."""
        x, y = calculate_crop_position(1920, 1080, 1080, 1080, CropAnchor.LOWER_RIGHT)
        assert x == 840  # 1920 - 1080
        assert y == 0  # 1080 - 1080

    def test_negative_values_clamped_to_zero(self):
        """Test that negative values are clamped to zero."""
        # This shouldn't happen in practice, but test the safety check
        x, y = calculate_crop_position(100, 100, 200, 200, CropAnchor.CENTER)
        assert x >= 0
        assert y >= 0


class TestResizeWithAspectRatio:
    """Test resize_with_aspect_ratio function."""

    def test_letterbox_wider_image(self):
        """Test letterbox mode with wider image (adds top/bottom bars)."""
        # Create a 1920x1080 image
        image = np.ones((1080, 1920, 3), dtype=np.uint8) * 255

        # Resize to 1080x1080 (square) with default black bars
        result = resize_with_aspect_ratio(
            image, 1080, 1080, AspectRatioMode.LETTERBOX
        )

        assert result.shape == (1080, 1080, 3)
        # Top and bottom should have black bars
        assert np.all(result[0, :] == 0)  # Top row is black
        assert np.all(result[-1, :] == 0)  # Bottom row is black

    def test_letterbox_with_white_bars(self):
        """Test letterbox mode with white bars."""
        # Create a 1920x1080 image
        image = np.ones((1080, 1920, 3), dtype=np.uint8) * 128

        # Resize to 1080x1080 with white bars
        result = resize_with_aspect_ratio(
            image, 1080, 1080, AspectRatioMode.LETTERBOX,
            letterbox_color=(255, 255, 255)
        )

        assert result.shape == (1080, 1080, 3)
        # Top and bottom should have white bars
        assert np.all(result[0, :] == 255)  # Top row is white
        assert np.all(result[-1, :] == 255)  # Bottom row is white

    def test_letterbox_with_custom_color(self):
        """Test letterbox mode with custom color bars."""
        # Create a 1920x1080 image
        image = np.ones((1080, 1920, 3), dtype=np.uint8) * 100

        # Resize with custom gray bars (128, 128, 128) in BGR
        result = resize_with_aspect_ratio(
            image, 1080, 1080, AspectRatioMode.LETTERBOX,
            letterbox_color=(128, 128, 128)
        )

        assert result.shape == (1080, 1080, 3)
        # Top row should have the custom color
        assert np.all(result[0, :] == 128)

    def test_letterbox_taller_image(self):
        """Test letterbox mode with taller image (adds left/right bars)."""
        # Create a 1080x1920 image (portrait)
        image = np.ones((1920, 1080, 3), dtype=np.uint8) * 255

        # Resize to 1920x1080 (landscape)
        result = resize_with_aspect_ratio(
            image, 1920, 1080, AspectRatioMode.LETTERBOX
        )

        assert result.shape == (1080, 1920, 3)
        # Left and right should have black bars
        assert np.all(result[:, 0] == 0)  # Left column is black
        assert np.all(result[:, -1] == 0)  # Right column is black

    def test_crop_center(self):
        """Test crop mode with center anchor."""
        # Create a 1920x1080 image
        image = np.ones((1080, 1920, 3), dtype=np.uint8) * 255

        # Resize to 1080x1080 (square) with center crop
        result = resize_with_aspect_ratio(
            image, 1080, 1080, AspectRatioMode.CROP, CropAnchor.CENTER
        )

        assert result.shape == (1080, 1080, 3)

    def test_crop_upper_left(self):
        """Test crop mode with upper left anchor."""
        # Create a test image with distinct colors in corners
        image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        image[:540, :960] = [255, 0, 0]  # Upper left = red
        image[:540, 960:] = [0, 255, 0]  # Upper right = green
        image[540:, :960] = [0, 0, 255]  # Lower left = blue
        image[540:, 960:] = [255, 255, 0]  # Lower right = yellow

        # Crop to square with upper left anchor
        result = resize_with_aspect_ratio(
            image, 1080, 1080, AspectRatioMode.CROP, CropAnchor.UPPER_LEFT
        )

        assert result.shape == (1080, 1080, 3)
        # The upper left corner should be predominantly red
        assert result[0, 0, 0] > 200  # High red value

    def test_crop_lower_right(self):
        """Test crop mode with lower right anchor."""
        # Create a test image with distinct colors
        image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        image[:540, :960] = [255, 0, 0]  # Upper left = red
        image[:540, 960:] = [0, 255, 0]  # Upper right = green
        image[540:, :960] = [0, 0, 255]  # Lower left = blue
        image[540:, 960:] = [255, 255, 0]  # Lower right = yellow

        # Crop to square with lower right anchor
        result = resize_with_aspect_ratio(
            image, 1080, 1080, AspectRatioMode.CROP, CropAnchor.LOWER_RIGHT
        )

        assert result.shape == (1080, 1080, 3)

    def test_maintains_image_dtype(self):
        """Test that output maintains input dtype."""
        image = np.ones((1080, 1920, 3), dtype=np.uint8) * 128

        result = resize_with_aspect_ratio(
            image, 1080, 1080, AspectRatioMode.LETTERBOX
        )

        assert result.dtype == np.uint8


class TestGetMediaFiles:
    """Test get_media_files function."""

    def test_empty_folder_images(self, temp_dir):
        """Test with empty folder for images."""
        files = get_media_files(str(temp_dir), "images")
        assert files == []

    def test_nonexistent_folder(self, temp_dir):
        """Test with non-existent folder."""
        non_existent = temp_dir / "missing"
        files = get_media_files(str(non_existent), "both")
        assert files == []

    def test_folder_with_images_only(self, temp_dir):
        """Test folder containing only images."""
        (temp_dir / "image1.jpg").touch()
        (temp_dir / "image2.png").touch()
        (temp_dir / "video.mp4").touch()

        files = get_media_files(str(temp_dir), "images")
        assert len(files) == 2
        assert all(f.suffix.lower() in {'.jpg', '.png'} for f in files)

    def test_folder_with_videos_only(self, temp_dir):
        """Test folder containing only videos."""
        (temp_dir / "image.jpg").touch()
        (temp_dir / "video1.mp4").touch()
        (temp_dir / "video2.avi").touch()

        files = get_media_files(str(temp_dir), "videos")
        assert len(files) == 2
        assert all(f.suffix.lower() in {'.mp4', '.avi'} for f in files)

    def test_folder_with_both_media_types(self, temp_dir):
        """Test folder with both images and videos."""
        (temp_dir / "image1.jpg").touch()
        (temp_dir / "image2.png").touch()
        (temp_dir / "video1.mp4").touch()
        (temp_dir / "video2.avi").touch()
        (temp_dir / "document.txt").touch()  # Non-media file

        files = get_media_files(str(temp_dir), "both")
        assert len(files) == 4
        # Should not include .txt file
        assert all(f.suffix.lower() != '.txt' for f in files)

    def test_sorted_output(self, temp_dir):
        """Test that output is sorted."""
        (temp_dir / "c.jpg").touch()
        (temp_dir / "a.jpg").touch()
        (temp_dir / "b.mp4").touch()

        files = get_media_files(str(temp_dir), "both")
        file_names = [f.name for f in files]
        assert file_names == sorted(file_names)


class TestAspectRatioInputFunctions:
    """Test input helper functions."""

    @patch('builtins.input', side_effect=['1'])
    def test_get_aspect_ratio_16_9(self, mock_input):
        """Test selecting 16:9 aspect ratio."""
        from change_aspect_ratio import get_aspect_ratio_input
        width, height = get_aspect_ratio_input()
        assert width == 1920
        assert height == 1080

    @patch('builtins.input', side_effect=['2'])
    def test_get_aspect_ratio_4_3(self, mock_input):
        """Test selecting 4:3 aspect ratio."""
        from change_aspect_ratio import get_aspect_ratio_input
        width, height = get_aspect_ratio_input()
        assert width == 1024
        assert height == 768

    @patch('builtins.input', side_effect=['3'])
    def test_get_aspect_ratio_1_1(self, mock_input):
        """Test selecting 1:1 (square) aspect ratio."""
        from change_aspect_ratio import get_aspect_ratio_input
        width, height = get_aspect_ratio_input()
        assert width == 1080
        assert height == 1080

    @patch('builtins.input', side_effect=['4'])
    def test_get_aspect_ratio_9_16(self, mock_input):
        """Test selecting 9:16 (vertical) aspect ratio."""
        from change_aspect_ratio import get_aspect_ratio_input
        width, height = get_aspect_ratio_input()
        assert width == 1080
        assert height == 1920

    @patch('builtins.input', side_effect=['6', '1280', '720'])
    def test_get_aspect_ratio_custom(self, mock_input):
        """Test custom aspect ratio input."""
        from change_aspect_ratio import get_aspect_ratio_input
        width, height = get_aspect_ratio_input()
        assert width == 1280
        assert height == 720

    @patch('builtins.input', side_effect=['6', 'invalid', 'also_invalid'])
    def test_get_aspect_ratio_invalid_custom(self, mock_input, capsys):
        """Test invalid custom aspect ratio falls back to default."""
        from change_aspect_ratio import get_aspect_ratio_input
        width, height = get_aspect_ratio_input()
        assert width == 1920
        assert height == 1080
        captured = capsys.readouterr()
        assert "invalid" in captured.out.lower()

    @patch('builtins.input', return_value='invalid')
    def test_get_aspect_ratio_invalid_choice(self, mock_input, capsys):
        """Test invalid choice falls back to default."""
        from change_aspect_ratio import get_aspect_ratio_input
        width, height = get_aspect_ratio_input()
        assert width == 1920
        assert height == 1080
        captured = capsys.readouterr()
        assert "invalid" in captured.out.lower()

    @patch('builtins.input', return_value='1')
    def test_get_mode_letterbox(self, mock_input):
        """Test selecting letterbox mode."""
        from change_aspect_ratio import get_mode_input
        mode = get_mode_input()
        assert mode == AspectRatioMode.LETTERBOX

    @patch('builtins.input', return_value='2')
    def test_get_mode_crop(self, mock_input):
        """Test selecting crop mode."""
        from change_aspect_ratio import get_mode_input
        mode = get_mode_input()
        assert mode == AspectRatioMode.CROP

    @patch('builtins.input', return_value='1')
    def test_get_anchor_center(self, mock_input):
        """Test selecting center anchor."""
        from change_aspect_ratio import get_anchor_input
        anchor = get_anchor_input()
        assert anchor == CropAnchor.CENTER

    @patch('builtins.input', return_value='2')
    def test_get_anchor_upper_left(self, mock_input):
        """Test selecting upper left anchor."""
        from change_aspect_ratio import get_anchor_input
        anchor = get_anchor_input()
        assert anchor == CropAnchor.UPPER_LEFT

    @patch('builtins.input', return_value='3')
    def test_get_anchor_upper_center(self, mock_input):
        """Test selecting upper center anchor."""
        from change_aspect_ratio import get_anchor_input
        anchor = get_anchor_input()
        assert anchor == CropAnchor.UPPER_CENTER

    @patch('builtins.input', return_value='4')
    def test_get_anchor_upper_right(self, mock_input):
        """Test selecting upper right anchor."""
        from change_aspect_ratio import get_anchor_input
        anchor = get_anchor_input()
        assert anchor == CropAnchor.UPPER_RIGHT

    @patch('builtins.input', return_value='5')
    def test_get_anchor_center_left(self, mock_input):
        """Test selecting center left anchor."""
        from change_aspect_ratio import get_anchor_input
        anchor = get_anchor_input()
        assert anchor == CropAnchor.CENTER_LEFT

    @patch('builtins.input', return_value='6')
    def test_get_anchor_center_right(self, mock_input):
        """Test selecting center right anchor."""
        from change_aspect_ratio import get_anchor_input
        anchor = get_anchor_input()
        assert anchor == CropAnchor.CENTER_RIGHT

    @patch('builtins.input', return_value='7')
    def test_get_anchor_lower_left(self, mock_input):
        """Test selecting lower left anchor."""
        from change_aspect_ratio import get_anchor_input
        anchor = get_anchor_input()
        assert anchor == CropAnchor.LOWER_LEFT

    @patch('builtins.input', return_value='8')
    def test_get_anchor_lower_center(self, mock_input):
        """Test selecting lower center anchor."""
        from change_aspect_ratio import get_anchor_input
        anchor = get_anchor_input()
        assert anchor == CropAnchor.LOWER_CENTER

    @patch('builtins.input', return_value='9')
    def test_get_anchor_lower_right(self, mock_input):
        """Test selecting lower right anchor."""
        from change_aspect_ratio import get_anchor_input
        anchor = get_anchor_input()
        assert anchor == CropAnchor.LOWER_RIGHT

    @patch('builtins.input', return_value='')
    def test_get_anchor_default(self, mock_input):
        """Test default anchor is center."""
        from change_aspect_ratio import get_anchor_input
        anchor = get_anchor_input()
        assert anchor == CropAnchor.CENTER

    @patch('builtins.input', return_value='1')
    def test_get_letterbox_color_black(self, mock_input):
        """Test selecting black letterbox color."""
        from change_aspect_ratio import get_letterbox_color_input
        color = get_letterbox_color_input()
        assert color == (0, 0, 0)

    @patch('builtins.input', return_value='2')
    def test_get_letterbox_color_white(self, mock_input):
        """Test selecting white letterbox color."""
        from change_aspect_ratio import get_letterbox_color_input
        color = get_letterbox_color_input()
        assert color == (255, 255, 255)

    @patch('builtins.input', return_value='3')
    def test_get_letterbox_color_gray(self, mock_input):
        """Test selecting gray letterbox color."""
        from change_aspect_ratio import get_letterbox_color_input
        color = get_letterbox_color_input()
        assert color == (128, 128, 128)

    @patch('builtins.input', side_effect=['4', '255', '128', '64'])
    def test_get_letterbox_color_custom(self, mock_input):
        """Test custom RGB letterbox color."""
        from change_aspect_ratio import get_letterbox_color_input
        color = get_letterbox_color_input()
        # Should return BGR format (64, 128, 255)
        assert color == (64, 128, 255)

    @patch('builtins.input', side_effect=['4', '300', '128', '64'])
    def test_get_letterbox_color_clamped(self, mock_input):
        """Test that custom color values are clamped to 0-255."""
        from change_aspect_ratio import get_letterbox_color_input
        color = get_letterbox_color_input()
        # Red value 300 should be clamped to 255, result in BGR: (64, 128, 255)
        assert color == (64, 128, 255)

    @patch('builtins.input', side_effect=['4', 'invalid', 'also_invalid', '0'])
    def test_get_letterbox_color_invalid_custom(self, mock_input, capsys):
        """Test invalid custom color falls back to black."""
        from change_aspect_ratio import get_letterbox_color_input
        color = get_letterbox_color_input()
        assert color == (0, 0, 0)
        captured = capsys.readouterr()
        assert "invalid" in captured.out.lower()

    @patch('builtins.input', return_value='')
    def test_get_letterbox_color_default(self, mock_input):
        """Test default letterbox color is black."""
        from change_aspect_ratio import get_letterbox_color_input
        color = get_letterbox_color_input()
        assert color == (0, 0, 0)
