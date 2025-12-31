"""Tests for format_utils module."""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from format_utils import (
    get_format_from_filename,
    get_extension_for_format,
    get_recommended_quality,
    should_convert_format,
    get_optimal_output_format,
    format_info,
)
from constants import (
    LOSSLESS_QUALITY,
    FORMAT_JPEG,
    FORMAT_PNG,
    FORMAT_WEBP,
)


class TestGetFormatFromFilename:
    """Test get_format_from_filename function."""

    def test_jpeg_extension(self):
        """Test JPEG extension detection."""
        assert get_format_from_filename("photo.jpg") == "JPEG"
        assert get_format_from_filename("photo.jpeg") == "JPEG"

    def test_png_extension(self):
        """Test PNG extension detection."""
        assert get_format_from_filename("image.png") == "PNG"

    def test_webp_extension(self):
        """Test WEBP extension detection."""
        assert get_format_from_filename("graphic.webp") == "WEBP"

    def test_gif_extension(self):
        """Test GIF extension detection."""
        assert get_format_from_filename("animation.gif") == "GIF"

    def test_case_insensitive(self):
        """Test case insensitive extension detection."""
        assert get_format_from_filename("PHOTO.JPG") == "JPEG"
        assert get_format_from_filename("Image.PNG") == "PNG"

    def test_with_path(self):
        """Test with full file path."""
        assert get_format_from_filename("/path/to/photo.jpg") == "JPEG"

    def test_unsupported_extension(self):
        """Test unsupported extension raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_format_from_filename("file.xyz")
        assert "unsupported" in str(exc_info.value).lower()


class TestGetExtensionForFormat:
    """Test get_extension_for_format function."""

    def test_jpeg_format(self):
        """Test JPEG format extension."""
        assert get_extension_for_format("JPEG") == ".jpg"

    def test_png_format(self):
        """Test PNG format extension."""
        assert get_extension_for_format("PNG") == ".png"

    def test_webp_format(self):
        """Test WEBP format extension."""
        assert get_extension_for_format("WEBP") == ".webp"

    def test_case_insensitive(self):
        """Test case insensitive format names."""
        assert get_extension_for_format("jpeg") == ".jpg"
        assert get_extension_for_format("png") == ".png"

    def test_unsupported_format(self):
        """Test unsupported format raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_extension_for_format("XYZ")
        assert "unsupported" in str(exc_info.value).lower()


class TestGetRecommendedQuality:
    """Test get_recommended_quality function."""

    def test_jpeg_web_quality(self):
        """Test JPEG web quality recommendation."""
        quality = get_recommended_quality("JPEG", "web")
        assert quality == 85

    def test_jpeg_thumbnail_quality(self):
        """Test JPEG thumbnail quality recommendation."""
        quality = get_recommended_quality("JPEG", "thumbnail")
        assert quality == 60

    def test_jpeg_archive_quality(self):
        """Test JPEG archive quality recommendation."""
        quality = get_recommended_quality("JPEG", "archive")
        assert quality == 95

    def test_lossless_format_quality(self):
        """Test lossless format always returns 100."""
        assert get_recommended_quality("PNG", "web") == LOSSLESS_QUALITY
        assert get_recommended_quality("BMP", "thumbnail") == LOSSLESS_QUALITY

    def test_default_use_case(self):
        """Test default use case is web."""
        quality_default = get_recommended_quality("JPEG")
        quality_web = get_recommended_quality("JPEG", "web")
        assert quality_default == quality_web

    def test_unknown_format_fallback(self):
        """Test unknown format returns fallback quality."""
        quality = get_recommended_quality("UNKNOWN", "web")
        assert 0 <= quality <= 100


class TestShouldConvertFormat:
    """Test should_convert_format function."""

    def test_same_format_no_conversion(self):
        """Test same format doesn't need conversion."""
        result = should_convert_format("JPEG", "JPEG")
        assert result["should_convert"] is False

    def test_different_format_needs_conversion(self):
        """Test different formats need conversion."""
        result = should_convert_format("PNG", "JPEG")
        assert result["should_convert"] is True

    def test_transparency_loss_warning(self):
        """Test transparency loss is detected."""
        result = should_convert_format("PNG", "JPEG", has_transparency=True)
        assert result["will_lose_transparency"] is True
        assert len(result["warnings"]) > 0

    def test_no_transparency_loss_if_supported(self):
        """Test no transparency loss for supporting formats."""
        result = should_convert_format("PNG", "WEBP", has_transparency=True)
        assert result["will_lose_transparency"] is False

    def test_quality_loss_warning(self):
        """Test quality loss from lossless to lossy."""
        result = should_convert_format("PNG", "JPEG")
        assert result["will_lose_quality"] is True
        assert len(result["warnings"]) > 0

    def test_no_quality_loss_lossless_to_lossless(self):
        """Test no quality loss between lossless formats."""
        result = should_convert_format("PNG", "BMP")
        assert result["will_lose_quality"] is False

    def test_jpeg_with_transparency_not_recommended(self):
        """Test JPEG not recommended for transparent images."""
        result = should_convert_format("PNG", "JPEG", has_transparency=True)
        assert result["recommended"] is False

    def test_case_insensitive_formats(self):
        """Test format comparison is case insensitive."""
        result1 = should_convert_format("png", "JPEG")
        result2 = should_convert_format("PNG", "jpeg")
        assert result1["should_convert"] == result2["should_convert"]


class TestGetOptimalOutputFormat:
    """Test get_optimal_output_format function."""

    def test_transparent_image_modern(self):
        """Test transparent image prefers WEBP when modern."""
        format_name = get_optimal_output_format("PNG", has_transparency=True, prefer_modern=True)
        assert format_name == FORMAT_WEBP

    def test_transparent_image_legacy(self):
        """Test transparent image uses PNG when legacy."""
        format_name = get_optimal_output_format("PNG", has_transparency=True, prefer_modern=False)
        assert format_name == FORMAT_PNG

    def test_animation_modern(self):
        """Test animated image prefers WEBP when modern."""
        format_name = get_optimal_output_format("GIF", has_transparency=False, prefer_modern=True)
        assert format_name == FORMAT_WEBP

    def test_photo_modern(self):
        """Test photo prefers WEBP when modern."""
        format_name = get_optimal_output_format("JPEG", has_transparency=False, prefer_modern=True)
        assert format_name == FORMAT_WEBP

    def test_photo_legacy(self):
        """Test photo uses JPEG when legacy."""
        format_name = get_optimal_output_format("JPEG", has_transparency=False, prefer_modern=False)
        assert format_name == FORMAT_JPEG


class TestFormatInfo:
    """Test format_info function."""

    def test_jpeg_info(self):
        """Test JPEG format information."""
        info = format_info("JPEG")
        assert info["name"] == "JPEG"
        assert info["extension"] == ".jpg"
        assert info["is_lossy"] is True
        assert info["is_lossless"] is False
        assert info["supports_transparency"] is False
        assert info["supports_animation"] is False

    def test_png_info(self):
        """Test PNG format information."""
        info = format_info("PNG")
        assert info["name"] == "PNG"
        assert info["extension"] == ".png"
        assert info["is_lossy"] is False
        assert info["is_lossless"] is True
        assert info["supports_transparency"] is True
        assert info["supports_animation"] is False

    def test_webp_info(self):
        """Test WEBP format information."""
        info = format_info("WEBP")
        assert info["name"] == "WEBP"
        assert info["extension"] == ".webp"
        assert info["is_lossy"] is True
        assert info["supports_transparency"] is True
        assert info["supports_animation"] is True

    def test_gif_info(self):
        """Test GIF format information."""
        info = format_info("GIF")
        assert info["name"] == "GIF"
        assert info["is_lossless"] is True
        assert info["supports_transparency"] is True
        assert info["supports_animation"] is True

    def test_quality_recommendations_present(self):
        """Test quality recommendations are included."""
        info = format_info("JPEG")
        assert "recommended_quality" in info
        assert "thumbnail" in info["recommended_quality"]
        assert "web" in info["recommended_quality"]
        assert "archive" in info["recommended_quality"]

    def test_case_insensitive_format(self):
        """Test format info is case insensitive."""
        info_upper = format_info("JPEG")
        info_lower = format_info("jpeg")
        assert info_upper["name"] == info_lower["name"]
