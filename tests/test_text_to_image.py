"""Tests for text_to_image module."""

import pytest
from pathlib import Path
from PIL import Image, ImageFont
import tempfile
import shutil

from text_to_image import (
    get_default_font,
    create_text_image,
    process_text_file,
    DEFAULT_FONT_SIZE,
    DEFAULT_TEXT_COLOR,
    DEFAULT_BG_COLOR,
    DEFAULT_FORMAT,
    DEFAULT_PADDING,
)
from constants import (
    ASPECT_RATIO_16_9,
    ASPECT_RATIO_1_1,
    ImageFormat,
)


class TestGetDefaultFont:
    """Test get_default_font function."""

    def test_returns_font_object(self):
        """Test that get_default_font returns a valid font object."""
        font = get_default_font(DEFAULT_FONT_SIZE)
        assert isinstance(font, (ImageFont.FreeTypeFont, ImageFont.ImageFont))

    def test_different_font_sizes(self):
        """Test creating fonts with different sizes."""
        small_font = get_default_font(12)
        large_font = get_default_font(72)

        assert isinstance(small_font, (ImageFont.FreeTypeFont, ImageFont.ImageFont))
        assert isinstance(large_font, (ImageFont.FreeTypeFont, ImageFont.ImageFont))

    def test_zero_font_size(self):
        """Test that font size of 0 doesn't crash."""
        # Should not raise an exception
        font = get_default_font(0)
        assert font is not None


class TestCreateTextImage:
    """Test create_text_image function."""

    def test_creates_image_with_correct_dimensions(self):
        """Test that created image has correct dimensions."""
        width, height = 800, 600
        font = get_default_font(DEFAULT_FONT_SIZE)

        img = create_text_image("Test", width, height, font)

        assert isinstance(img, Image.Image)
        assert img.size == (width, height)

    def test_creates_image_with_default_colors(self):
        """Test image creation with default colors."""
        width, height = 800, 600
        font = get_default_font(DEFAULT_FONT_SIZE)

        img = create_text_image(
            "Test", width, height, font, DEFAULT_TEXT_COLOR, DEFAULT_BG_COLOR
        )

        # Check background color (sample from corner)
        pixel = img.getpixel((0, 0))
        assert pixel == DEFAULT_BG_COLOR

    def test_creates_image_with_custom_colors(self):
        """Test image creation with custom colors."""
        width, height = 800, 600
        font = get_default_font(DEFAULT_FONT_SIZE)
        custom_bg = (100, 150, 200)

        img = create_text_image("Test", width, height, font, bg_color=custom_bg)

        # Check custom background color
        pixel = img.getpixel((0, 0))
        assert pixel == custom_bg

    def test_empty_text(self):
        """Test creating image with empty text."""
        width, height = 800, 600
        font = get_default_font(DEFAULT_FONT_SIZE)

        img = create_text_image("", width, height, font)

        assert img.size == (width, height)

    def test_long_text(self):
        """Test creating image with very long text."""
        width, height = 800, 600
        font = get_default_font(DEFAULT_FONT_SIZE)
        long_text = "This is a very long text that might not fit in the image"

        img = create_text_image(long_text, width, height, font)

        assert img.size == (width, height)

    def test_unicode_text(self):
        """Test creating image with Unicode characters."""
        width, height = 800, 600
        font = get_default_font(DEFAULT_FONT_SIZE)
        unicode_text = "Hello 世界 🌍"

        img = create_text_image(unicode_text, width, height, font)

        assert img.size == (width, height)

    def test_custom_padding(self):
        """Test image creation with custom padding."""
        width, height = 800, 600
        font = get_default_font(DEFAULT_FONT_SIZE)
        custom_padding = 50

        img = create_text_image("Test", width, height, font, padding=custom_padding)

        assert img.size == (width, height)

    def test_different_aspect_ratios(self):
        """Test creating images with different aspect ratios."""
        font = get_default_font(DEFAULT_FONT_SIZE)

        # 16:9
        img_16_9 = create_text_image("Test", *ASPECT_RATIO_16_9, font)
        assert img_16_9.size == ASPECT_RATIO_16_9

        # 1:1 (Square)
        img_1_1 = create_text_image("Test", *ASPECT_RATIO_1_1, font)
        assert img_1_1.size == ASPECT_RATIO_1_1


class TestProcessTextFile:
    """Test process_text_file function."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def sample_text_file(self, temp_dir):
        """Create a sample text file."""
        text_file = temp_dir / "test.txt"
        text_file.write_text("Line 1\nLine 2\nLine 3\n")
        return text_file

    def test_process_nonexistent_file(self, temp_dir):
        """Test processing a file that doesn't exist."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        count = process_text_file(
            str(temp_dir / "nonexistent.txt"),
            str(output_dir),
            800,
            600,
        )

        assert count == 0

    def test_process_empty_file(self, temp_dir):
        """Test processing an empty file."""
        text_file = temp_dir / "empty.txt"
        text_file.write_text("")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        count = process_text_file(
            str(text_file),
            str(output_dir),
            800,
            600,
        )

        assert count == 0

    def test_process_file_with_only_whitespace(self, temp_dir):
        """Test processing a file with only whitespace."""
        text_file = temp_dir / "whitespace.txt"
        text_file.write_text("   \n\n  \n")
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        count = process_text_file(
            str(text_file),
            str(output_dir),
            800,
            600,
        )

        assert count == 0

    def test_process_valid_text_file(self, sample_text_file, temp_dir):
        """Test processing a valid text file."""
        output_dir = temp_dir / "output"

        count = process_text_file(
            str(sample_text_file),
            str(output_dir),
            800,
            600,
        )

        assert count == 3
        assert output_dir.exists()

        # Check that output files were created
        output_files = list(output_dir.glob("*.png"))
        assert len(output_files) == 3

    def test_process_file_creates_output_folder(self, sample_text_file, temp_dir):
        """Test that process_text_file creates output folder if it doesn't exist."""
        output_dir = temp_dir / "new_output"
        assert not output_dir.exists()

        count = process_text_file(
            str(sample_text_file),
            str(output_dir),
            800,
            600,
        )

        assert count == 3
        assert output_dir.exists()

    def test_output_filenames(self, sample_text_file, temp_dir):
        """Test that output filenames are correctly formatted."""
        output_dir = temp_dir / "output"

        process_text_file(
            str(sample_text_file),
            str(output_dir),
            800,
            600,
        )

        output_files = sorted(output_dir.glob("*.png"))
        assert len(output_files) == 3

        # Check filename pattern
        assert "line_001" in output_files[0].name
        assert "line_002" in output_files[1].name
        assert "line_003" in output_files[2].name

    def test_different_output_formats(self, sample_text_file, temp_dir):
        """Test creating images in different formats."""
        output_dir = temp_dir / "output"

        # Test JPEG
        count_jpeg = process_text_file(
            str(sample_text_file),
            str(output_dir / "jpeg"),
            800,
            600,
            output_format=ImageFormat.JPEG.value,
        )
        assert count_jpeg == 3
        jpeg_files = list((output_dir / "jpeg").glob("*.jpg"))
        assert len(jpeg_files) == 3

        # Test WEBP
        count_webp = process_text_file(
            str(sample_text_file),
            str(output_dir / "webp"),
            800,
            600,
            output_format=ImageFormat.WEBP.value,
        )
        assert count_webp == 3
        webp_files = list((output_dir / "webp").glob("*.webp"))
        assert len(webp_files) == 3

    def test_custom_colors(self, sample_text_file, temp_dir):
        """Test processing with custom colors."""
        output_dir = temp_dir / "output"
        custom_text_color = (255, 0, 0)  # Red
        custom_bg_color = (0, 0, 255)  # Blue

        count = process_text_file(
            str(sample_text_file),
            str(output_dir),
            800,
            600,
            text_color=custom_text_color,
            bg_color=custom_bg_color,
        )

        assert count == 3

        # Verify image has custom background color
        img = Image.open(list(output_dir.glob("*.png"))[0])
        pixel = img.getpixel((0, 0))
        assert pixel == custom_bg_color

    def test_custom_font_size(self, sample_text_file, temp_dir):
        """Test processing with custom font size."""
        output_dir = temp_dir / "output"
        custom_font_size = 72

        count = process_text_file(
            str(sample_text_file),
            str(output_dir),
            800,
            600,
            font_size=custom_font_size,
        )

        assert count == 3

    def test_custom_dimensions(self, sample_text_file, temp_dir):
        """Test processing with custom dimensions."""
        output_dir = temp_dir / "output"
        width, height = 1920, 1080

        process_text_file(
            str(sample_text_file),
            str(output_dir),
            width,
            height,
        )

        # Verify image dimensions
        img = Image.open(list(output_dir.glob("*.png"))[0])
        assert img.size == (width, height)

    def test_special_characters_in_text(self, temp_dir):
        """Test processing text with special characters."""
        text_file = temp_dir / "special.txt"
        text_file.write_text("Hello/World\nTest*File\nSpecial#Characters\n")
        output_dir = temp_dir / "output"

        count = process_text_file(
            str(text_file),
            str(output_dir),
            800,
            600,
        )

        assert count == 3

        # Verify filenames are sanitized
        output_files = list(output_dir.glob("*.png"))
        for file in output_files:
            # Ensure no special characters in filename
            assert "/" not in file.name
            assert "*" not in file.name

    def test_very_long_text_line(self, temp_dir, capfd):
        """Test processing a very long text line."""
        text_file = temp_dir / "long.txt"
        long_line = "A" * 200  # Very long line
        text_file.write_text(long_line)
        output_dir = temp_dir / "output"

        count = process_text_file(
            str(text_file),
            str(output_dir),
            800,
            600,
        )

        assert count == 1

        # Verify filename is truncated
        output_file = list(output_dir.glob("*.png"))[0]
        assert len(output_file.stem) < 200  # Filename should be truncated

        # Verify warning was issued
        captured = capfd.readouterr()
        assert "too long for filename" in captured.out or "too long for filename" in captured.err

    def test_unicode_text_in_file(self, temp_dir):
        """Test processing text file with Unicode characters."""
        text_file = temp_dir / "unicode.txt"
        text_file.write_text("Hello 世界\nBonjour 🌍\nПривет\n", encoding="utf-8")
        output_dir = temp_dir / "output"

        count = process_text_file(
            str(text_file),
            str(output_dir),
            800,
            600,
        )

        assert count == 3

    def test_mixed_empty_and_valid_lines(self, temp_dir):
        """Test processing file with mix of empty and valid lines."""
        text_file = temp_dir / "mixed.txt"
        text_file.write_text("Line 1\n\nLine 2\n   \nLine 3\n")
        output_dir = temp_dir / "output"

        count = process_text_file(
            str(text_file),
            str(output_dir),
            800,
            600,
        )

        # Should only process non-empty lines
        assert count == 3

    def test_custom_padding(self, sample_text_file, temp_dir):
        """Test processing with custom padding."""
        output_dir = temp_dir / "output"
        custom_padding = 50

        count = process_text_file(
            str(sample_text_file),
            str(output_dir),
            800,
            600,
            padding=custom_padding,
        )

        assert count == 3


class TestImageVerification:
    """Test that created images are valid and readable."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)

    def test_created_images_are_valid(self, temp_dir):
        """Test that created images can be opened and read."""
        text_file = temp_dir / "test.txt"
        text_file.write_text("Test Image")
        output_dir = temp_dir / "output"

        process_text_file(
            str(text_file),
            str(output_dir),
            800,
            600,
        )

        # Try to open and verify each created image
        for img_file in output_dir.glob("*.png"):
            img = Image.open(img_file)
            assert img.size == (800, 600)
            assert img.mode == "RGB"
            img.verify()  # Verify image integrity

    def test_jpeg_images_have_no_alpha(self, temp_dir):
        """Test that JPEG images don't have alpha channel."""
        text_file = temp_dir / "test.txt"
        text_file.write_text("Test JPEG")
        output_dir = temp_dir / "output"

        process_text_file(
            str(text_file),
            str(output_dir),
            800,
            600,
            output_format=ImageFormat.JPEG.value,
        )

        img_file = list(output_dir.glob("*.jpg"))[0]
        img = Image.open(img_file)
        assert img.mode == "RGB"  # JPEG should be RGB, not RGBA


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)

    def test_very_small_dimensions(self, temp_dir):
        """Test creating images with very small dimensions."""
        text_file = temp_dir / "test.txt"
        text_file.write_text("Test")
        output_dir = temp_dir / "output"

        count = process_text_file(
            str(text_file),
            str(output_dir),
            10,  # Very small
            10,
        )

        assert count == 1
        img = Image.open(list(output_dir.glob("*.png"))[0])
        assert img.size == (10, 10)

    def test_very_large_dimensions(self, temp_dir):
        """Test creating images with large dimensions."""
        text_file = temp_dir / "test.txt"
        text_file.write_text("Test")
        output_dir = temp_dir / "output"

        count = process_text_file(
            str(text_file),
            str(output_dir),
            3840,  # 4K width
            2160,  # 4K height
        )

        assert count == 1
        img = Image.open(list(output_dir.glob("*.png"))[0])
        assert img.size == (3840, 2160)

    def test_single_line_file(self, temp_dir):
        """Test processing file with single line."""
        text_file = temp_dir / "single.txt"
        text_file.write_text("Single Line")
        output_dir = temp_dir / "output"

        count = process_text_file(
            str(text_file),
            str(output_dir),
            800,
            600,
        )

        assert count == 1
        assert len(list(output_dir.glob("*.png"))) == 1

    def test_many_lines_file(self, temp_dir):
        """Test processing file with many lines."""
        text_file = temp_dir / "many.txt"
        lines = [f"Line {i}" for i in range(1, 101)]  # 100 lines
        text_file.write_text("\n".join(lines))
        output_dir = temp_dir / "output"

        count = process_text_file(
            str(text_file),
            str(output_dir),
            800,
            600,
        )

        assert count == 100
        assert len(list(output_dir.glob("*.png"))) == 100
