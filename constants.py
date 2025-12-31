"""
Shared constants for image and video processing tools.
"""

# Image formats and extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
SUPPORTED_IMAGE_FORMATS = {'JPEG', 'JPG', 'PNG', 'WEBP', 'BMP', 'GIF', 'TIFF'}

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

# Output defaults
DEFAULT_HEADER_OUTPUT = 'photoData.h'
DEFAULT_VIDEO_OUTPUT_DIR = 'videos'
DEFAULT_ARRAY_NAME = 'photoData'

# Image processing modes
RGB_MODE = 'RGB'
RGBA_MODE = 'RGBA'
LA_MODE = 'LA'
P_MODE = 'P'

# JPEG settings
JPEG_SUBSAMPLING_420 = 2
JPEG_SUBSAMPLING_444 = 0

# Resampling methods
RESAMPLING_METHOD = 'LANCZOS'
