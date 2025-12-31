"""Tests for constants module."""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from constants import (
    ImageFormat,
    VideoFormat,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    LOSSY_FORMATS,
    LOSSLESS_FORMATS,
    TRANSPARENCY_FORMATS,
    ANIMATION_FORMATS,
    QUALITY_RECOMMENDATIONS,
    DEFAULT_QUALITY_FALLBACK,
    LOSSLESS_QUALITY,
    is_image_file,
    is_video_file,
    supports_transparency,
    is_lossy_format,
)


class TestImageFormat:
    """Test ImageFormat enum."""

    def test_image_format_values(self):
        """Test that ImageFormat enum has expected values."""
        assert ImageFormat.JPEG.value == "JPEG"
        assert ImageFormat.PNG.value == "PNG"
        assert ImageFormat.WEBP.value == "WEBP"
        assert ImageFormat.GIF.value == "GIF"

    def test_all_formats_present(self):
        """Test that all expected formats are in enum."""
        format_values = {f.value for f in ImageFormat}
        assert "JPEG" in format_values
        assert "PNG" in format_values
        assert "WEBP" in format_values
        assert "GIF" in format_values
        assert "BMP" in format_values
        assert "TIFF" in format_values


class TestVideoFormat:
    """Test VideoFormat enum."""

    def test_video_format_values(self):
        """Test that VideoFormat enum has expected values."""
        assert VideoFormat.MP4.value == "mp4"
        assert VideoFormat.AVI.value == "avi"
        assert VideoFormat.MOV.value == "mov"


class TestFileExtensions:
    """Test file extension constants."""

    def test_image_extensions(self):
        """Test that IMAGE_EXTENSIONS contains expected extensions."""
        assert '.jpg' in IMAGE_EXTENSIONS
        assert '.jpeg' in IMAGE_EXTENSIONS
        assert '.png' in IMAGE_EXTENSIONS
        assert '.gif' in IMAGE_EXTENSIONS
        assert '.webp' in IMAGE_EXTENSIONS

    def test_video_extensions(self):
        """Test that VIDEO_EXTENSIONS contains expected extensions."""
        assert '.mp4' in VIDEO_EXTENSIONS
        assert '.avi' in VIDEO_EXTENSIONS
        assert '.mov' in VIDEO_EXTENSIONS
        assert '.mkv' in VIDEO_EXTENSIONS


class TestFormatCategories:
    """Test format category sets."""

    def test_lossy_formats(self):
        """Test lossy format identification."""
        assert 'JPEG' in LOSSY_FORMATS
        assert 'WEBP' in LOSSY_FORMATS
        assert 'PNG' not in LOSSY_FORMATS

    def test_lossless_formats(self):
        """Test lossless format identification."""
        assert 'PNG' in LOSSLESS_FORMATS
        assert 'BMP' in LOSSLESS_FORMATS
        assert 'TIFF' in LOSSLESS_FORMATS
        assert 'JPEG' not in LOSSLESS_FORMATS

    def test_transparency_formats(self):
        """Test transparency support identification."""
        assert 'PNG' in TRANSPARENCY_FORMATS
        assert 'WEBP' in TRANSPARENCY_FORMATS
        assert 'GIF' in TRANSPARENCY_FORMATS
        assert 'JPEG' not in TRANSPARENCY_FORMATS

    def test_animation_formats(self):
        """Test animation support identification."""
        assert 'GIF' in ANIMATION_FORMATS
        assert 'WEBP' in ANIMATION_FORMATS
        assert 'PNG' not in ANIMATION_FORMATS


class TestQualitySettings:
    """Test quality setting constants."""

    def test_quality_recommendations_structure(self):
        """Test that quality recommendations have correct structure."""
        assert "thumbnail" in QUALITY_RECOMMENDATIONS
        assert "web" in QUALITY_RECOMMENDATIONS
        assert "archive" in QUALITY_RECOMMENDATIONS

    def test_quality_recommendations_values(self):
        """Test quality recommendation values are in valid range."""
        for use_case, formats in QUALITY_RECOMMENDATIONS.items():
            for format_name, quality in formats.items():
                assert 0 <= quality <= 100, f"Quality {quality} out of range for {format_name} in {use_case}"

    def test_default_quality_fallback(self):
        """Test default quality fallback is valid."""
        assert 0 <= DEFAULT_QUALITY_FALLBACK <= 100

    def test_lossless_quality(self):
        """Test lossless quality is 100."""
        assert LOSSLESS_QUALITY == 100


class TestHelperFunctions:
    """Test helper functions."""

    def test_is_image_file_valid(self):
        """Test is_image_file with valid image files."""
        assert is_image_file("photo.jpg") is True
        assert is_image_file("image.png") is True
        assert is_image_file("graphic.webp") is True
        assert is_image_file("animation.gif") is True

    def test_is_image_file_invalid(self):
        """Test is_image_file with non-image files."""
        assert is_image_file("video.mp4") is False
        assert is_image_file("document.pdf") is False
        assert is_image_file("script.py") is False

    def test_is_image_file_case_insensitive(self):
        """Test is_image_file is case insensitive."""
        assert is_image_file("PHOTO.JPG") is True
        assert is_image_file("Image.PNG") is True

    def test_is_video_file_valid(self):
        """Test is_video_file with valid video files."""
        assert is_video_file("clip.mp4") is True
        assert is_video_file("movie.avi") is True
        assert is_video_file("video.mov") is True

    def test_is_video_file_invalid(self):
        """Test is_video_file with non-video files."""
        assert is_video_file("photo.jpg") is False
        assert is_video_file("document.pdf") is False

    def test_supports_transparency_true(self):
        """Test supports_transparency with formats that support it."""
        assert supports_transparency("PNG") is True
        assert supports_transparency("WEBP") is True
        assert supports_transparency("GIF") is True
        assert supports_transparency("png") is True  # Case insensitive

    def test_supports_transparency_false(self):
        """Test supports_transparency with formats that don't support it."""
        assert supports_transparency("JPEG") is False
        assert supports_transparency("BMP") is False

    def test_is_lossy_format_true(self):
        """Test is_lossy_format with lossy formats."""
        assert is_lossy_format("JPEG") is True
        assert is_lossy_format("WEBP") is True
        assert is_lossy_format("jpeg") is True  # Case insensitive

    def test_is_lossy_format_false(self):
        """Test is_lossy_format with lossless formats."""
        assert is_lossy_format("PNG") is False
        assert is_lossy_format("BMP") is False


class TestDefaultValues:
    """Test default value constants."""

    def test_folder_defaults_exist(self):
        """Test that all default folder constants are defined."""
        from constants import (
            DEFAULT_IMAGES_INPUT_DIR,
            DEFAULT_IMAGES_OUTPUT_DIR,
            DEFAULT_VIDEOS_INPUT_DIR,
            DEFAULT_VIDEOS_OUTPUT_DIR,
        )
        assert DEFAULT_IMAGES_INPUT_DIR == "images_to_process"
        assert DEFAULT_IMAGES_OUTPUT_DIR == "images_processed"
        assert DEFAULT_VIDEOS_INPUT_DIR == "videos_to_process"
        assert DEFAULT_VIDEOS_OUTPUT_DIR == "videos_processed"

    def test_legacy_aliases(self):
        """Test that legacy aliases point to correct values."""
        from constants import (
            DEFAULT_INPUT_FOLDER,
            DEFAULT_OUTPUT_FOLDER,
            DEFAULT_VIDEOS_INPUT_DIR,
            DEFAULT_VIDEOS_OUTPUT_DIR,
        )
        assert DEFAULT_INPUT_FOLDER == DEFAULT_VIDEOS_INPUT_DIR
        assert DEFAULT_OUTPUT_FOLDER == DEFAULT_VIDEOS_OUTPUT_DIR

    def test_video_defaults(self):
        """Test video processing defaults."""
        from constants import (
            DEFAULT_MAPPING_FILE,
            DEFAULT_TARGET_DURATION,
            DEFAULT_FADE_DURATION,
        )
        assert DEFAULT_MAPPING_FILE == "video_mapping.txt"
        assert DEFAULT_TARGET_DURATION == 3.0
        assert DEFAULT_FADE_DURATION == 0.5
