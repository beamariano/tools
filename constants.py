"""
Shared constants for image and video processing tools.
"""

from enum import Enum
from typing import Set, Dict


# Image Format Enumerations
class ImageFormat(Enum):
    """Supported image formats."""
    JPEG = "JPEG"
    JPG = "JPG"
    PNG = "PNG"
    WEBP = "WEBP"
    GIF = "GIF"
    BMP = "BMP"
    TIFF = "TIFF"


class VideoFormat(Enum):
    """Supported video formats."""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"


# File Extensions
IMAGE_EXTENSIONS: Set[str] = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
VIDEO_EXTENSIONS: Set[str] = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}

# Format to extension mapping
IMAGE_FORMAT_EXTENSIONS: Dict[str, str] = {
    'JPEG': '.jpg',
    'JPG': '.jpg',
    'PNG': '.png',
    'WEBP': '.webp',
    'GIF': '.gif',
    'BMP': '.bmp',
    'TIFF': '.tiff',
}

# Extension to format mapping
EXTENSION_TO_FORMAT: Dict[str, str] = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.png': 'PNG',
    '.webp': 'WEBP',
    '.gif': 'GIF',
    '.bmp': 'BMP',
    '.tiff': 'TIFF',
}

# Lossy vs Lossless formats
LOSSY_FORMATS: Set[str] = {'JPEG', 'JPG', 'WEBP'}
LOSSLESS_FORMATS: Set[str] = {'PNG', 'BMP', 'TIFF', 'GIF'}

# Formats supporting transparency
TRANSPARENCY_FORMATS: Set[str] = {'PNG', 'WEBP', 'GIF', 'TIFF'}

# Formats supporting animation
ANIMATION_FORMATS: Set[str] = {'GIF', 'WEBP'}

# Backward compatibility
SUPPORTED_IMAGE_FORMATS = {fmt.value for fmt in ImageFormat}

# Image processing defaults
DEFAULT_IMAGE_WIDTH = 240
DEFAULT_IMAGE_HEIGHT = 320
DEFAULT_JPEG_QUALITY = 75
DEFAULT_WEB_QUALITY = 85
DEFAULT_MAX_WEB_WIDTH = 1920
DEFAULT_MAX_WEB_HEIGHT = 1080

# Image optimization settings
DEFAULT_PNG_COMPRESSION_LEVEL = 9
DEFAULT_WEBP_METHOD = 6
DEFAULT_BYTES_PER_LINE = 12

# Video processing defaults
DEFAULT_VIDEO_DURATION = 4
DEFAULT_VIDEO_FPS = 24
DEFAULT_VIDEO_CODEC = 'libx264'
DEFAULT_VIDEO_FORMAT = 'mp4'

# Common folder defaults
DEFAULT_IMAGES_INPUT_DIR = "images_to_process"
DEFAULT_IMAGES_OUTPUT_DIR = "images_processed"
DEFAULT_VIDEOS_INPUT_DIR = "videos_to_process"
DEFAULT_VIDEOS_OUTPUT_DIR = "videos_processed"

# Video duration adjustment defaults
DEFAULT_MAPPING_FILE = "video_mapping.txt"
DEFAULT_TARGET_DURATION = 3.0
DEFAULT_FADE_DURATION = 0.5

# Legacy aliases for backward compatibility
DEFAULT_INPUT_FOLDER = DEFAULT_VIDEOS_INPUT_DIR
DEFAULT_OUTPUT_FOLDER = DEFAULT_VIDEOS_OUTPUT_DIR

# Output defaults
DEFAULT_HEADER_OUTPUT = 'photoData.h'
DEFAULT_VIDEO_OUTPUT_DIR = DEFAULT_VIDEOS_OUTPUT_DIR  # For image_to_video.py
DEFAULT_ARRAY_NAME = 'photoData'

# Image processing modes
class ImageMode(Enum):
    """PIL Image modes."""
    RGB = "RGB"
    RGBA = "RGBA"
    LA = "LA"
    P = "P"
    L = "L"
    CMYK = "CMYK"
    LAB = "LAB"


# Backward compatibility
RGB_MODE = ImageMode.RGB.value
RGBA_MODE = ImageMode.RGBA.value
LA_MODE = ImageMode.LA.value
P_MODE = ImageMode.P.value

# Modes that require conversion for JPEG
MODES_REQUIRING_RGB_CONVERSION = {ImageMode.RGBA.value, ImageMode.LA.value, ImageMode.P.value}

# JPEG settings
class JpegSubsampling(Enum):
    """JPEG chroma subsampling modes."""
    SUBSAMPLING_420 = 2  # 4:2:0 (high compression)
    SUBSAMPLING_422 = 1  # 4:2:2 (medium compression)
    SUBSAMPLING_444 = 0  # 4:4:4 (no subsampling, best quality)


# Backward compatibility
JPEG_SUBSAMPLING_420 = JpegSubsampling.SUBSAMPLING_420.value
JPEG_SUBSAMPLING_444 = JpegSubsampling.SUBSAMPLING_444.value

# Resampling methods
class ResamplingMethod(Enum):
    """PIL resampling methods."""
    NEAREST = "NEAREST"
    BILINEAR = "BILINEAR"
    BICUBIC = "BICUBIC"
    LANCZOS = "LANCZOS"


RESAMPLING_METHOD = ResamplingMethod.LANCZOS.value

# Video codec options
class VideoCodec(Enum):
    """Common video codecs."""
    H264 = "libx264"
    H265 = "libx265"
    VP9 = "libvpx-vp9"
    AV1 = "libaom-av1"
    MPEG4 = "mpeg4"


# Quality settings for different use cases
QUALITY_THUMBNAIL = "thumbnail"
QUALITY_WEB = "web"
QUALITY_ARCHIVE = "archive"

# Quality recommendations by format and use case
QUALITY_RECOMMENDATIONS = {
    QUALITY_THUMBNAIL: {"JPEG": 60, "WEBP": 65},
    QUALITY_WEB: {"JPEG": 85, "WEBP": 85},
    QUALITY_ARCHIVE: {"JPEG": 95, "WEBP": 95},
}

# Default quality fallback
DEFAULT_QUALITY_FALLBACK = 85

# Lossless format quality (always 100)
LOSSLESS_QUALITY = 100

# Format name constants for comparison
FORMAT_JPEG = "JPEG"
FORMAT_PNG = "PNG"
FORMAT_WEBP = "WEBP"
FORMAT_GIF = "GIF"


# Format validation helpers
def is_image_file(filename: str) -> bool:
    """Check if filename has a valid image extension."""
    from pathlib import Path
    return Path(filename).suffix.lower() in IMAGE_EXTENSIONS


def is_video_file(filename: str) -> bool:
    """Check if filename has a valid video extension."""
    from pathlib import Path
    return Path(filename).suffix.lower() in VIDEO_EXTENSIONS


def supports_transparency(format: str) -> bool:
    """Check if format supports transparency."""
    return format.upper() in TRANSPARENCY_FORMATS


def is_lossy_format(format: str) -> bool:
    """Check if format uses lossy compression."""
    return format.upper() in LOSSY_FORMATS
